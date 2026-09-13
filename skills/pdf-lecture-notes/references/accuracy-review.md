# Accuracy review before delivery

Schema success means structurally valid, not factually correct. This is a required
source-based editorial check in all modes, performed by the writing agent. It does
not require another agent or user approval.

Save `accuracy-review.md` next to note.json with: source files, reviewed sections,
claim/location, source page or transcript timestamp, check performed, finding and
resolution. Mark unavailable evidence explicitly. Do not write “all verified” if
only samples were checked. Recheck changed claims after corrections.

1. Coverage: compare planned pages with the PDF and note. Check that important
   formulas, code, table units, footnotes and limitations were not omitted. Validate
   that groups marked transition really contain no substantive teaching material.
2. Formulas: verify signs, subscripts, units and domains. Recalculate worked examples.
   Separate rounded display values from exact calculation values. In y=a+bx a vertical
   line is not an admissible candidate; do not turn an analogy into a false claim
   about the optimizer's actual implementation.
3. Statistical claims when relevant: p-values concern results at least as extreme
   under the null and assumptions, not the probability the null is true. Qualify
   nonnegative in-sample R² by OLS with an intercept and the usual definition.
   Correlation is not causation; collinearity does not guarantee unaffected future
   prediction. Preserve scope and assumptions rather than copying loose classroom speech.
4. Data flow: trace train/validation/test roles and information dates against source
   code. Fit coefficients and preprocessing on training data; predict on test data.
   Never describe a frozen forecast as using a model fitted on the test sample.
5. Evidence: check each classroom addition against the transcript, retaining recording
   identity or a documented timestamp offset. Separate source facts, inference,
   teaching examples, and unsupported uncertainty. Reproduction claims need actual
   calculation evidence; do not infer verification from plausible matching numbers.
6. Charts: inspect labels, units, legends, plotted values, and explanatory captions.
   Do not interchange majority-class accuracy, positive-month rate, or MA(12) accuracy.
7. Readability: remove repeated definitions, preserve code indentation, check formulas
   and figure readability in rendered output. Sample beginning, a difficult middle
   section, and appendices; report any destination preview you could not inspect.

Unresolved factual issues must be corrected or explicitly qualified in the note.
The JSON validator checks page ordering, review references, mode consistency and
teaching structure only; it cannot certify these semantic checks.
