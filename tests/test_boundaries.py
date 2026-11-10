import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import test_validate
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from compare import changes


class BoundaryTests(unittest.TestCase):
    run_case = test_validate.ValidationTests.run_case

    def test_json_syntax_matrix(self):
        for raw in ('', ' ', 'null null', '{"x":1,}', "{'x':1}", '01', '+1', '[1,]', 'undefined', '-Infinity', '1e9999', '\ufeff{}'):
            with self.subTest(raw=raw):
                self.assertEqual(self.run_case(raw, {})[0], 1)

    def test_valid_scalar_matrix(self):
        for raw in ('null','true','false','0','-1','1.5','"你好😀"','[]','{}','1e-20'):
            with self.subTest(raw=raw):
                self.assertEqual(self.run_case(raw, {})[0], 0)

    def test_schema_matrix(self):
        cases = [('null', False, 1), ('null', True, 0), ('true', {'type':'integer'}, 1), ('2.0', {'type':'integer'}, 0), ('[1,1]', {'uniqueItems':True}, 1), ('"bad"', {'format':'email'}, 1), ('"x"', {'enum':['a','b']}, 1), ('3', {'minimum':4}, 1), ('{}', {'required':['x']}, 1), ('{"x":1}', {'additionalProperties':False}, 1), ('"a"', {'minLength':2}, 1), ('[1]', {'minItems':2}, 1), ('1', {'allOf':[{'type':'integer'},{'maximum':2}]}, 0), ('"a"', {'anyOf':[{'type':'integer'},{'type':'string'}]}, 0)]
        for raw, schema, expected in cases:
            with self.subTest(raw=raw, schema=schema):
                self.assertEqual(self.run_case(raw, schema)[0], expected)

    def test_reference_matrix(self):
        for keyword in ('const','default','examples','enum'):
            value = {'$ref':'https://example.com'}
            schema = {keyword:[value] if keyword in ('examples','enum') else value}
            self.assertEqual(self.run_case(json.dumps(value), schema)[0], 0)
        for schema in ({'items':{'$ref':'remote.json'}}, {'allOf':[{'$ref':'remote.json'}]}, {'$ref':'#/$defs/missing'}, {'$schema':'http://json-schema.org/draft-07/schema#'}):
            self.assertEqual(self.run_case('[1]', schema)[0], 2)

    def test_nested_array_types_are_changes(self):
        for before, after in (([True],[1]), ([1],[1.0]), ([{'x':False}],[{'x':0}]), ([[1]],[[True]])):
            self.assertTrue(changes(before, after))

    def test_diff_matrix(self):
        for value in (None, True, 1, '你好', [], {}, {'a':[1,2]}):
            self.assertEqual(changes(value, value), [])
        self.assertEqual(changes({'a/b~':1},{'a/b~':2})[0]['path'], ['a/b~'])
        self.assertTrue(changes([1,2],[2,1]))

    def test_cli_errors_and_preservation(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            data = base/'data.json'; schema = base/'schema.json'
            data.write_text('{}'); schema.write_text('{}')
            command = [sys.executable, str(root/'scripts/validate.py'), '--input',str(data),'--schema',str(schema)]
            for tail in (['--report',str(data)], ['--report',str(schema)], ['--report',str(base/'missing'/'report.json')]):
                run = subprocess.run(command+tail, capture_output=True)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(data.read_text(), '{}')
                self.assertEqual(schema.read_text(), '{}')
            data.write_bytes(b'\xff')
            self.assertEqual(subprocess.run(command,capture_output=True).returncode, 1)
            data.unlink()
            self.assertEqual(subprocess.run(command,capture_output=True).returncode, 2)
