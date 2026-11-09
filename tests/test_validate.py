import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate.py"
spec = importlib.util.spec_from_file_location("validator", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ValidationTests(unittest.TestCase):
    def run_case(self, raw, schema):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "input.json").write_text(raw, encoding="utf-8")
            (base / "schema.json").write_text(json.dumps(schema), encoding="utf-8")
            return validator.validate_files(base / "input.json", base / "schema.json")

    def test_valid(self):
        self.assertEqual(self.run_case('{"x":1}', {"type":"object"})[0], 0)

    def test_constraint_errors_have_paths(self):
        code, report = self.run_case('{"x":"bad"}', {"properties":{"x":{"type":"integer"}}})
        self.assertEqual(code, 1)
        self.assertEqual(report["errors"][0]["instance_path"], ["x"])

    def test_invalid_json(self):
        for raw in ('{', '{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.subTest(raw=raw):
                self.assertEqual(self.run_case(raw, {})[1]["stage"], "parse")

    def test_required_and_extra_fields(self):
        schema = {"type":"object", "required":["x"], "additionalProperties":False}
        self.assertEqual(self.run_case('{"y":1}', schema)[0], 1)

    def test_bad_schema(self):
        self.assertEqual(self.run_case('{}', {"type":"nonsense"})[0], 2)

    def test_external_reference(self):
        self.assertEqual(self.run_case('{}', {"$ref":"https://example.com/schema"})[0], 2)

    def test_local_reference(self):
        self.assertEqual(self.run_case('3', {"$defs":{"n":{"type":"integer"}}, "$ref":"#/$defs/n"})[0], 0)


if __name__ == "__main__":
    unittest.main()
