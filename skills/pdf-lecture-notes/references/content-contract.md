# Content contract

Write a structured `note.json`; output-specific syntax belongs to renderers.

## Document shape

- A precise title.
- A short reading guide only when it helps the intended learning goal.
- A concise outline of the lecture's logical progression.
- Sections built from coherent groups of one to five consecutive pages.
- The first section must declare `h1`; later sections may use `null` to continue that theme.
- A terminology summary or self-check only when useful for the profile.

## Section sequence

Each page group should normally contain:

1. A `summary` block stating the group's conclusion or purpose.
2. One `slide` block per page, followed by enough `paragraph` blocks to explain what is visible and why it matters.
3. A `formula` block when a formula is important to the profile. Its symbol explanations should match the reader's assumed knowledge.
4. A `terms` block for newly introduced specialist terms.
5. A `classroom_note` only when the transcript clearly supports it, including its timestamp.
6. A `learning_note` for a likely conceptual obstacle when that adds value; it is not mandatory in every section.
7. A `figure` only when a new diagram materially improves understanding.

The sequence may be shortened for concise or advanced profiles. Never pad sections to satisfy a fixed block count.

## Fidelity

- Use the exact page number and keep source values, formulas, labels, and proper nouns unchanged.
- List each section's pages in increasing order and include exactly one matching `slide` block for each page.
- Make uncertainty explicit. Do not turn an inference into a slide claim.
- Paraphrase transcript content and correct obvious transcription errors using the slides, but do not fabricate missing speech.
- Use one translation for each recurring term. Preserve the source-language term on first use when helpful.
- Constructed diagrams must encode the claimed relationship in their actual data.

## Block model

The authoritative structure is `schemas/note.schema.json`. Fill the top-level `labels` in the requested output language so renderers do not impose English or Chinese UI copy. Supported blocks are `summary`, `slide`, `paragraph`, `formula`, `terms`, `classroom_note`, `learning_note`, and `figure`. Images may be absolute paths or paths relative to the project root while drafting; renderers normalize them.
