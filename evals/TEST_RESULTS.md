# Test results / 测试记录

Date: 2026-11-10. Environment: Windows, Python 3.11.11.

| Executed check / 已执行检查 | Result / 结果 |
|---|---|
| Unit tests / 单元测试 | 14 passed |
| CLI smoke checks / 命令行测试 | 9 passed |

Reproduce from the repository root:

```console
python -m unittest discover -s tests -v
python evals/run_smoke.py
```

The smoke checks execute actual subprocesses and inspect both exit codes and JSON reports: invalid type, a valid supplied candidate, missing required field, duplicate keys, truncation, fenced output, changed values, unchanged values and unavailable comparison. Raw results: [smoke-results.json](smoke-results.json).

命令行测试通过真实子进程检查退出码及 JSON 报告，覆盖错误类型、合法候选、缺字段、重复键、截断、代码围栏及差异状态。

Candidates were supplied by the test author. This is not an independent Agent repair trial, a model comparison or a measured improvement claim. Missing-fact stopping behavior, retry discipline and factual preservation still need actual Agent trajectory evaluation. Other Python versions and remote CI status are not certified by this local run.

候选由测试作者提供，尚未开展独立 Agent 修复实验或模型对照。不把上述通过率当作模型修复率；事实缺失时停止、重试次数控制及事实保真仍待实际轨迹验证。本地运行也不证明其他 Python 版本或远端 CI 通过。
