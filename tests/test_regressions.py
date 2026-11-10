import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from compare import changes
import test_validate


class RegressionTests(unittest.TestCase):
    run_case = test_validate.ValidationTests.run_case
    def test_exponent_overflow(self):
        self.assertEqual(self.run_case('1e9999', {})[0], 1)

    def test_literal_ref_is_data(self):
        self.assertEqual(self.run_case('{"$ref":"https://example.com"}', {'const': {'$ref':'https://example.com'}})[0], 0)

    def test_nested_external_reference(self):
        self.assertEqual(self.run_case('{}', {'properties':{'x':{'$ref':'remote.json'}}})[0], 2)

    def test_id_rejected(self):
        self.assertEqual(self.run_case('{}', {'$id':'https://example.com/schema'})[0], 2)

    def test_empty_local_reference(self):
        self.assertEqual(self.run_case('1', {'type':'integer', 'if':{'type':'string'}, 'then':{'$ref':''}})[0], 0)

    def test_change_report(self):
        result = changes({'x':1, 'old':2}, {'x':'1', 'new':3})
        self.assertEqual({e['operation'] for e in result}, {'add','remove','replace'})
        self.assertEqual(changes({'x':1}, {'x':1}), [])

    def test_array_change(self):
        self.assertEqual(changes([1,2], [2,1])[0]['path'], [])
