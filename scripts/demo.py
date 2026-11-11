import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
def run(args, expected):
    result=subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    if result.returncode != expected: raise RuntimeError(result.stdout+result.stderr)
    return {'command':args,'exit_code':result.returncode,'output':json.loads(result.stdout)}
results=[run(['scripts/validate.py','--input','examples/invalid.json','--schema','examples/schema.json'],1),run(['scripts/validate.py','--input','examples/valid.json','--schema','examples/schema.json'],0),run(['scripts/compare.py','--before','examples/invalid.json','--after','examples/valid.json'],1)]
print(json.dumps({'results':results,'limitation':'Script demonstration, not independent Agent evaluation.'},ensure_ascii=True,indent=2))
