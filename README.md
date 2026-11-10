# Structured Output Check

[English](README.md) | [简体中文](README.zh-CN.md)

Validate AI-generated JSON and guide bounded repairs while preserving source facts.

## What this skill does

Local Python scripts strictly parse JSON, validate Draft 2020-12 schemas and report structural changes. The Agent follows [SKILL.md](SKILL.md) to interpret errors and create repair candidates. Scripts require no API key and do not call a model or automatically repair files.

## When to use

- Malformed JSON or output that violates a known schema.
- Missing fields, wrong types, enum or numeric constraint failures.
- Reviewable changes between original and repaired outputs.

This skill does not verify facts, implement provider integrations or authorize downstream execution.

## Install and examples

Requires Python 3.10+. Run from the repository root:

```console
python -m pip install -r requirements.txt
python scripts/validate.py --input examples/valid.json --schema examples/schema.json --report report.json
python scripts/validate.py --input examples/invalid.json --schema examples/schema.json
python scripts/compare.py --before examples/invalid.json --after examples/valid.json
```

The valid example passes. The invalid example reports a type error at `["count"]`. The comparison flags changes; converting `"two"` to `2` still requires source evidence.

Place the complete folder named structured-output-check in your Agent host's supported skills directory. Keep SKILL.md and scripts together and install dependencies in the Agent's Python environment. Discovery rules vary by host; use absolute script paths outside the repository root.

Example request:

> Use structured-output-check to validate original.json against schema.json. Repair only from supplied facts, with at most two attempts. Preserve the original, each candidate, validation reports and change explanations.

## Core workflow

1. Establish the schema and authoritative source facts.
2. Preserve and validate the original; resolve configuration errors before repair.
3. Create a separate candidate using minimal justified changes. An unambiguous outer Markdown fence may be removed. Do not guess missing facts or silently truncate records.
4. Revalidate against the unchanged schema, with at most two repair attempts by default.
5. Compare parseable documents and review changes against evidence. For unparseable originals, explain textual edits separately; unavailable comparison is not unchanged data.

## CLI contracts

| Exit | Validator | Comparator |
|---|---|---|
| 0 | Schema-valid | Unchanged |
| 1 | Parse/schema failure | Changes require review |
| 2 | Input/configuration/report failure | Comparison unavailable |

Argument misuse also exits 2. Validator JSON reports contain valid, stage and errors; schema errors include instance/schema paths. Comparator reports contain report_version, status and facts_verified=false, plus changes or an error message. Arrays are compared as whole values. Reports can contain input values; protect them like source data.

## Edge cases and limits

- Rejects duplicate keys, NaN, Infinity and overflowing exponents. Float precision and underflow follow Python behavior; not an exact-decimal validator.
- Supports self-contained Draft 2020-12 schemas and document-local references. External references and $id are unsupported; unknown keywords are not business validators.
- Format checking depends on jsonschema FormatChecker and installed dependencies.
- Never automatically inserts defaults or null for missing facts. Schema validity does not imply factual correctness.
- No resource limits for hostile schemas or oversized files; use trusted, reasonably sized local inputs.
- No built-in provider adapter or automatic batch repair service.

## Testing and status

```console
python -m unittest discover -s tests -v
```

CI is configured for Python 3.10–3.12; configuration alone is not a passing run. See [executed test results](evals/TEST_RESULTS.md) and [Agent evaluation scenarios](evals/README.md). No measured model improvement is claimed.

## References

Organization references the scope/workflow/examples approach of [llm-structured-output](https://github.com/sickn33/agentic-awesome-skills/blob/main/skills/llm-structured-output/SKILL.md) and validation/retry checkpoints of [ai-output-validation](https://github.com/DevelopersGlobal/ai-agent-skills/blob/main/skills/ai-output-validation/SKILL.md). Implementation and wording here are independent; provider capabilities from those projects are not included.

## Verification checkpoint — development paused

2026-11-10: three consecutive local rounds passed 21 unit test methods (including input matrices) and 9 CLI checks per round on Python 3.11.11 / Windows. Expanded coverage includes scalar JSON, invalid syntax, schema constraints, local/missing/external references, literal $ref data, array type differences, report overwrite protection, unreadable/missing files and output failures. Fixed nested array comparisons that previously missed true→1 or 1→1.0 changes, and handled parser recursion errors.

This checkpoint pauses feature development. Tests do not exhaust all boundaries, certify hostile-input resource safety, or establish independent Agent repair performance. Remaining limits include float precision/underflow, Unicode surrogate handling, deep/recursive schemas and resource budgets. See [boundary results](evals/boundary-results.json).
