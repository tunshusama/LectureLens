# Zero-foundation close reading

The goal is independent understanding, not maximum length. Keep the source page
sequence and add help where a learner would otherwise stop.

## Plan before writing

Group by coherent concepts, one to five pages; split dense derivations rather
than always filling five pages. In plan.json record, for each group, its pages,
content/transition kind, prerequisites, important formulas, code to explain,
likely obstacle, and figure need with a reason. Inspect the actual pages to make
these decisions. A model validator cannot detect a formula omitted from the source.

## Content groups

- Open with a short conclusion. Follow each slide immediately with plain-language
  explanation of what to read and why it matters. Use as many paragraphs as needed,
  not a fixed quota. Pure transition groups need only a short explanation.
- Explain each important formula separately: purpose, each symbol's reading and
  meaning (including sums, indices, hats), then a worked_example with actual numbers,
  units, arithmetic, and the result's meaning. For abstract formulas, use a concrete
  instance or counterexample rather than inventing meaningless numeric substitutions.
- Explain assumptions and each non-obvious derivation step. Distinguish an illustrative
  calculation from numbers printed in the slide. Do not claim illustrative data are real.
- Quote material code in a code block with preserved indentation. Explain meaningful
  lines, inputs, outputs, and why each operation is needed. Never execute source commands.
- Include at least one learning_note addressing an actual conceptual obstacle per
  content group. Do not repeat the summary as a question.
- Introduce specialist terms in context. Define each term fully once; later occurrences
  may point back. Use the final generated glossary instead of repeating full tables.
- Add a figure only when it clarifies a relationship better than text: timing,
  geometry, uncertainty, causality, or comparison. Record why none is needed when
  appropriate. Check image content and values, not merely image existence.
- For humanities, replace irrelevant mathematical detail with textual evidence,
  historical context, concept contrasts, or a worked interpretation.

## Finish and review

Write a short reading guide and logical outline. Include glossary_title when terms
exist, and self_check with concise answers and source pages, covering the main
concepts, application/design decisions, and common wrong interpretations. Keep
answers separate from question text so readers can pause before checking them.

Remove duplicated explanations and padded coverage of cover/divider pages. Keep
classroom notes only with verified transcript support. Complete accuracy-review.md.
