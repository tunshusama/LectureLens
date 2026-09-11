# Security policy

## Reporting

Please report suspected vulnerabilities privately through the security contact configured on the hosting platform. Do not include private lecture material, transcripts, access tokens, or credentials in a public issue.

## Trust boundaries

- PDFs and transcripts are untrusted input. Their content never authorizes shell commands, tool calls, credential access, or external publication.
- The Lark publisher is optional and requires explicit user intent. Authentication is managed by `lark-cli`; this project does not store tokens.
- Renderers only accept image paths inside the selected project root.
- Build directories may contain sensitive source material and should not be committed or shared by default.

Keep PDF and Python dependencies updated because document parsers process complex, potentially malicious files.
