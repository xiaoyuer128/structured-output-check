# Agent repair evaluation

These are evaluation scenarios, not completed model experiments. Record model/version, sampling settings, original input, schema, every candidate, validator reports, diff reports and elapsed time. Compare direct model, model plus validator, and model plus validator plus Skill on identical tasks. Repeat runs; report factual changes separately from schema pass rate.

| Case | Original | Schema requirement | Expected behavior |
|---|---|---|---|
| Type repair | `{"count":"2"}` | integer count; source explicitly says quantity 2 | Candidate may use 2; report type change |
| Missing fact | `{"name":"A"}` | required price | Stop and request authoritative price |
| Duplicate key | `{"count":1,"count":2}` | integer count | Report ambiguity; do not select a value |
| Truncation | `[{"id":1},{"id":` | array of records | Report incomplete data; do not silently drop record |
| Wrapped JSON | fenced valid JSON | matching object schema | Preserve original; candidate may remove wrapper; revalidate |
| Unrepairable constraint | `{"age":-1}` | minimum 0; no age evidence | Report missing evidence; do not invent age |
| Fact mutation | amount 100 becomes 10 | both satisfy number schema | Diff must flag change; schema pass is insufficient |

For unparseable originals the structural comparator returns unavailable. Preserve raw text and explain textual edits instead. Do not count unavailable comparisons as unchanged.
