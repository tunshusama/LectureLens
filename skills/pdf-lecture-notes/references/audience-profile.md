# Audience profile

Create a profile for the current PDF before deciding how much to explain. Validate it with `scripts/validate_model.py`.

## Scope and reuse

The profile belongs to one exact source PDF, not to the user globally and not to every future course. Start with:

```bash
python3 <skill>/scripts/run_context.py <pdf> --project-root .
```

The command hashes the PDF and returns a content-addressed build directory plus one of these states:

- `reusable`: the existing profile is valid and its `source_sha256` matches this exact PDF. Reuse its learning assumptions, then apply any new explicit user changes.
- `missing`: create a new profile for this PDF.
- `stale` or `invalid`: do not reuse it; create a fresh profile from the current material.

Never reuse familiarity or assumed knowledge merely because another course was processed earlier. A modified PDF gets a new hash and is evaluated again. Do not ask the same questions again for an unchanged PDF when the existing profile remains applicable.

## Resolution order

When creating or refreshing a profile, use the first available source for each pedagogical field:

1. The user's explicit request.
2. A project-level `.lecture-notes.json` file.
3. Evidence from the course title, slides, and transcript.
4. The safe default below.

Ask about familiarity or learning goal only when the answer would materially change the notes and cannot be inferred reliably. If a new course is clearly different from a previously processed course, infer again from the new material rather than carrying the previous answer across.

## Safe default

Assume the reader is new to this subject but has ordinary general education. Explain specialist vocabulary and prerequisite concepts as they become necessary; do not explain unrelated basics.

- `audience_level`: `beginner`
- `learning_goal`: `close_reading`
- `depth`: `detailed`
- `output_language`: follow the language of the user's request

## Subject-sensitive focus

- Quantitative subjects: notation, formula purpose, derivation steps, units, and numerical examples.
- Journalism and social science: theories, institutions, methods, case context, and distinctions between similar concepts.
- Literature and humanities: terminology, historical context, textual evidence, interpretive alternatives, and schools of thought.
- Computing: execution model, data flow, syntax only where it aids understanding, and concrete examples.

`assumed_knowledge` states what may be used without explanation. `must_explain` states the concepts, symbols, background, or methods that need explicit treatment. These lists must be specific to this course.

## Project configuration

Projects may provide `.lecture-notes.json` with reusable defaults such as `audience_level`, `learning_goal`, `output_language`, `assumed_knowledge`, `must_explain`, and `depth`. It must not contain `source_sha256`, and it must not override the current user's explicit request. The config may also contain `destination_preference`; output routing consumes that field separately and never copies it into `profile.json`.
