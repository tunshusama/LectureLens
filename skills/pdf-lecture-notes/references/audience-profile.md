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

For a `missing`, `stale`, or `invalid` profile, familiarity is course-specific user information, not something the slides can establish. If neither the current request nor project configuration supplies `audience_level`, ask the user once how familiar they are with this course before writing. Do not substitute the safe default merely to avoid this question. If `learning_goal` is also unspecified and different goals would materially change the result, ask it in the same concise prompt rather than as a second interruption.

## Resolution order

When creating or refreshing a profile, use the first available source for each pedagogical field:

1. The user's explicit request.
2. A project-level `.lecture-notes.json` file.
3. Evidence from the course title, slides, and transcript.
4. The safe default below.

Infer the discipline and subject-specific explanation needs from the new material when possible, but never infer the user's personal familiarity from course difficulty. Ask about the learning goal only under the condition above. Never carry answers from a different course into the new profile.

## Safe default

Use this default only when the user declines to specify familiarity, or when interaction is unavailable. Assume the reader is new to this subject but has ordinary general education. Explain specialist vocabulary and prerequisite concepts as they become necessary; do not explain unrelated basics.

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
