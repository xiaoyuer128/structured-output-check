"""Strict JSON and self-contained Draft 2020-12 schema validation."""
import argparse
import json
import sys
from pathlib import Path


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"Duplicate object key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Non-finite JSON number: {value}")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=pairs, parse_constant=reject_constant)


def check_refs(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ("$ref", "$dynamicRef") and isinstance(item, str) and not item.startswith("#"):
                raise ValueError("External schema references are unsupported")
            check_refs(item)
    elif isinstance(value, list):
        for item in value:
            check_refs(item)


def validate_files(input_path, schema_path):
    try:
        from jsonschema import Draft202012Validator, FormatChecker
        schema = load(schema_path)
        if isinstance(schema, dict) and schema.get("$schema", "https://json-schema.org/draft/2020-12/schema") != "https://json-schema.org/draft/2020-12/schema":
            raise ValueError("Only JSON Schema Draft 2020-12 is supported")
        Draft202012Validator.check_schema(schema)
        check_refs(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
    except Exception as exc:
        return 2, {"valid": False, "stage": "configuration", "errors": [{"message": str(exc)}]}
    try:
        data = load(input_path)
    except (ValueError, UnicodeError) as exc:
        return 1, {"valid": False, "stage": "parse", "errors": [{"message": str(exc)}]}
    except OSError as exc:
        return 2, {"valid": False, "stage": "input", "errors": [{"message": str(exc)}]}
    try:
        errors = [{"instance_path": list(e.absolute_path),
                   "schema_path": list(e.absolute_schema_path), "message": e.message}
                  for e in validator.iter_errors(data)]
    except Exception as exc:
        return 2, {"valid": False, "stage": "configuration", "errors": [{"message": str(exc)}]}
    return (1 if errors else 0), {"valid": not errors, "stage": "validation", "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--report")
    args = parser.parse_args()
    if args.report and Path(args.report).resolve() in (Path(args.input).resolve(), Path(args.schema).resolve()):
        parser.error("Report must not overwrite input or schema")
    code, report = validate_files(args.input, args.schema)
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        try:
            Path(args.report).write_text(output + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"Unable to write report: {exc}", file=sys.stderr)
            return 2
    print(output)
    return code


if __name__ == "__main__":
    sys.exit(main())
