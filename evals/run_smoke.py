"""Reproducible CLI checks, including author-guided candidate scenarios."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
results = []
with tempfile.TemporaryDirectory() as temp:
    base = Path(temp)
    schema = {'type':'object','properties':{'count':{'type':'integer'}},'required':['count'],'additionalProperties':False}
    (base/'schema.json').write_text(json.dumps(schema), encoding='utf-8')
    fixtures = {'original':'{"count":"2"}', 'candidate':'{"count":2}', 'missing':'{}', 'duplicate':'{"count":1,"count":2}', 'truncated':'{"count":', 'fenced':'```json\n{"count":2}\n```'}
    for name, raw in fixtures.items():
        (base/f'{name}.json').write_text(raw, encoding='utf-8')
    def check(name, script, args, expected, predicate):
        run = subprocess.run([sys.executable, str(root/'scripts'/script), *args], capture_output=True, text=True, encoding='utf-8')
        report = json.loads(run.stdout)
        passed = run.returncode == expected and predicate(report)
        results.append({'case':name,'passed':passed,'exit_code':run.returncode,'report':report})
        if not passed:
            raise AssertionError(name)
    def validate(name, expected):
        check(name, 'validate.py', ['--input',str(base/f'{name}.json'),'--schema',str(base/'schema.json')], expected, lambda r:r['valid']==(expected==0))
    for name in fixtures:
        validate(name, 0 if name=='candidate' else 1)
    check('type_change', 'compare.py', ['--before',str(base/'original.json'),'--after',str(base/'candidate.json')], 1, lambda r:r['changes'][0]['path']==['count'])
    check('unchanged', 'compare.py', ['--before',str(base/'candidate.json'),'--after',str(base/'candidate.json')], 0, lambda r:r['status']=='unchanged')
    check('unparseable_comparison', 'compare.py', ['--before',str(base/'truncated.json'),'--after',str(base/'candidate.json')], 2, lambda r:r['status']=='comparison_unavailable')
print(json.dumps({'python':sys.version.split()[0], 'passed':len(results), 'results':results, 'limitation':'Candidates supplied by author; no independent Agent trial or baseline.'}, ensure_ascii=False, indent=2))
