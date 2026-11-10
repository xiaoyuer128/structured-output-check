"""Report structural changes between two strict JSON documents; not fact verification."""
import argparse
import json
from validate import load


def changes(before, after, path=None):
    path = [] if path is None else path
    if type(before) is not type(after):
        return [{"operation": "replace", "path": path, "before": before, "after": after}]
    result = []
    if isinstance(before, dict):
        for key in sorted(before.keys() | after.keys()):
            if key not in after:
                result.append({"operation": "remove", "path": path + [key], "before": before[key]})
            elif key not in before:
                result.append({"operation": "add", "path": path + [key], "after": after[key]})
            else:
                result.extend(changes(before[key], after[key], path + [key]))
    elif isinstance(before, list):
        # Compare the whole array: positional matching cannot prove item identity.
        if len(before) != len(after) or any(changes(a, b) for a, b in zip(before, after)):
            result.append({"operation": "replace", "path": path, "before": before, "after": after})
    elif before != after:
        result.append({"operation": "replace", "path": path, "before": before, "after": after})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', required=True)
    parser.add_argument('--after', required=True)
    args = parser.parse_args()
    try:
        result = changes(load(args.before), load(args.after))
        report = {"report_version": "1.0", "status": "review_required" if result else "unchanged", "changes": result, "facts_verified": False}
        code = 1 if result else 0
    except (ValueError, OSError, UnicodeError, RecursionError) as exc:
        report = {"report_version": "1.0", "status": "comparison_unavailable", "message": str(exc), "facts_verified": False}
        code = 2
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
