---
name: feishu-coding-agent-listener
description: "指导 Coding Agent 通过长连接将本地服务接入飞书聊天消息和文档评论 @。适用于实现、诊断或记录飞书机器人监听服务；不用于普通的一次性消息发送或文档编辑。"
---

# 飞书 Coding Agent 监听器

为飞书事件到本地 Coding Agent 建立一条尽量精简、可靠的处理链路。除非用户要求重写，否则沿用现有运行环境和框架。

## 目标链路

每个应用进程只使用一条长连接，并在同一连接上注册两类处理器：

```text
飞书长连接
  ├─ im.message.receive_v1       → 消息队列 → Coding Agent → 回复聊天
  └─ drive.notice.comment_add_v1 → 评论队列 → 读取评论和上下文
                                      → Coding Agent → 回复原评论
```

同一个应用建立多条长连接时，事件可能被分发到没有对应处理器的连接。优先采用“一条 SDK 连接、多个处理器”的结构。事件回调只负责解析、入队和返回；耗时的模型调用与文档处理放到工作线程中执行。

## 飞书配置清单

在飞书开发者后台确认：

1. 应用已开启机器人能力，并已发布可供目标用户使用的版本。
2. 事件订阅方式为**长连接**。
3. 已添加以下事件：
   - `im.message.receive_v1`：接收机器人聊天消息。
   - `drive.notice.comment_add_v1`：接收文档新增评论或回复。
4. 应用权限至少包括：
   - 接收私聊：`im:message.p2p_msg:readonly`。
   - 接收群聊 @：`im:message.group_at_msg:readonly`；更宽泛的 `im:message:readonly` 也可能满足接口要求。
   - 发送聊天消息：`im:message:send_as_bot`。
   - 读取评论：`docs:document.comment:read`。
   - 回复评论：`docs:document.comment:create`，或当前接口错误明确要求的写权限。
   - 读取文档上下文：`docs:document.content:read`；Docx 还可能需要 `docx:document:readonly`。

权限名称可能随版本变化。以当前 CLI 或 API 返回的 `missing_scopes` 和 `console_url` 为准，不要绕过权限错误继续猜测。

文档评论事件还需要用户与应用维度的 Drive 订阅。使用目标 `lark-cli` profile 明确检查：

```bash
lark-cli --profile <应用ID或profile> drive user subscription_status \
  --event-type drive.notice.comment_add_v1 --as user --json
```

如果用户已经授权搭建监听服务，且返回的 `is_subscribe` 为 `false`，先预览再创建订阅：

```bash
lark-cli --profile <profile> drive user subscription --as user \
  --data '{"event_type":"drive.notice.comment_add_v1"}' --dry-run --json

lark-cli --profile <profile> drive user subscription --as user \
  --data '{"event_type":"drive.notice.comment_add_v1"}' --json
```

创建后再次运行 `subscription_status` 验证。这是写操作；只有用户明确要求搭建监听服务或单独同意订阅时才能执行。未经授权，不要创建或移除订阅。

## 实现指引

长连接优先使用飞书官方 SDK。`lark-cli event consume` 适合消费其事件目录中已经收录的事件，但某些版本并未暴露 `drive.notice.comment_add_v1`。如果 `lark-cli event list --json` 中找不到评论事件，应使用 SDK 注册原始或自定义事件，不要虚构 EventKey。

Python 的最小结构如下：

```python
handler = (
    lark.EventDispatcherHandler.builder("", "")
    .register_p2_customized_event("im.message.receive_v1", on_message)
    .register_p1_customized_event("im.message.receive_v1", on_message)
    .register_p2_customized_event("drive.notice.comment_add_v1", on_comment)
    .register_p1_customized_event("drive.notice.comment_add_v1", on_comment)
    .build()
)
lark.ws.Client(app_id, app_secret, event_handler=handler).start()
```

同时兼容 v1 和 v2 事件信封。v2 的事件类型通常位于 `header.event_type`，消息数据位于 `event.message`，评论标识可能嵌套在 `event.notice_meta` 中。

评论工作线程应依次完成：

1. 按事件 ID 去重；只有处理成功或明确忽略后才标记完成。
2. 忽略机器人自身产生的事件。
3. 使用 `file_token`、`file_type` 和 `comment_id` 查询评论。
4. 检查最新评论回复，只有其中提及机器人的 `open_id` 才继续处理。
5. 如果回复接口不支持已解决评论或全文评论，则直接忽略。
6. 获取小而相关的上下文：优先评论关联的 block，其次搜索引用文本，最后才读取有长度上限的全文。
7. 要求 Coding Agent 只输出回复正文，并将结果添加到原评论。

常用 CLI 操作：

```bash
lark-cli --profile <profile> drive +batch-query-comments ... --as bot --json
lark-cli --profile <profile> drive +list-replies ... --as bot --json
lark-cli --profile <profile> docs +fetch ... --as bot --json
lark-cli --profile <profile> drive +add-reply ... --as bot --json
lark-cli --profile <profile> im +messages-send ... --as bot --json
```

构造参数前先运行对应命令的 `--help`。判断 JSON 是否成功时使用 `ok == true` 或进程退出码 0，不要依赖不存在的顶层 `code` 字段。

## 凭据与运行管理

- App Secret 和 Token 不得写进源码、日志、进程参数或提交到版本库的配置。优先使用环境变量、系统钥匙串或权限受限的密钥文件。
- 未经脱敏，不要打印 `auth status`、服务管理器的完整环境变量或 SDK 原始连接 URL；其中可能包含凭据或连接票据。
- 长期运行的本地监听器使用 launchd、systemd 等进程管理器托管。日志记录启动、收到事件、处理结果和重连或失败状态，但不记录密钥或完整私密文档。
- 增加评论能力时应保留原有聊天行为。为两类事件信封增加解析测试，并覆盖自身事件、错误 @、重复投递和回复失败等路由情况。

## 验证与排障

按以下顺序验证：

1. 语法和测试通过，必要配置存在。
2. `lark-cli auth status --json --verify` 能验证机器人身份。
3. 所需权限已经开通。
4. `drive.notice.comment_add_v1` 的用户级订阅返回 `true`。
5. 该应用只建立了一条长连接。
6. 一条真实聊天消息能够到达消息处理器并收到回复。
7. 在真实文档评论中 @机器人，事件能够到达评论处理器并在原位置收到回复。

未经用户授权，不要主动创建测试消息或文档评论。如果连接成功但没有评论事件，依次检查开发者后台事件、已发布的应用版本、用户级 Drive 订阅，以及文档和应用的可见范围。如果事件已经到达但处理失败，应分别定位评论读取、@ 解析、文档访问、模型生成和评论回复环节。
