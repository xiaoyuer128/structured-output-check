# Structured Output Check

[English](README.md) | [简体中文](README.zh-CN.md)

校验 AI 生成的 JSON，引导有限次数修复，并保留来源事实。

## 功能

本地 Python 脚本负责严格 JSON 解析、Draft 2020-12 Schema 校验及结构差异报告。Agent 按 [SKILL.md](SKILL.md) 理解错误并生成候选。脚本无需 API Key，不调用模型，也不自动修复文件。

## 适用场景

- 非法 JSON 或输出不符合既定 Schema。
- 缺字段、类型、枚举或数值约束错误。
- 需要审查修复前后变化。

不提供事实核验、模型供应商接入层或下游执行授权。

## 安装与示例

需要 Python 3.10+，在仓库根目录运行：

```console
python -m pip install -r requirements.txt
python scripts/validate.py --input examples/valid.json --schema examples/schema.json --report report.json
python scripts/validate.py --input examples/invalid.json --schema examples/schema.json
python scripts/compare.py --before examples/invalid.json --after examples/valid.json
```

有效示例通过；无效示例报告 `["count"]` 类型错误。差异示例只标记变化，将 `"two"` 转为 `2` 仍需要来源支持。

把名为 structured-output-check 的完整目录放入 Agent 宿主支持的技能目录，保持 SKILL.md 与脚本在一起，并在 Agent 使用的 Python 环境安装依赖。不同宿主的发现规则不同；从其他工作目录调用时使用脚本完整路径。

示例请求：

> 使用 structured-output-check 校验 original.json 是否符合 schema.json。仅根据提供的事实修复，最多两轮；保留原文、每次候选、校验报告和修改说明。

## 核心流程

1. 明确 Schema 与权威事实来源。
2. 保留原文并校验，先解决输入或 Schema 配置问题。
3. 最小改动生成独立候选；可移除明确的外围 Markdown 围栏，不猜测缺失事实，不静默截断记录。
4. 使用不变的 Schema 重新校验，默认最多两轮修复。
5. 对可解析文档进行差异比较，结合来源审阅变化。原文无法解析时另行说明文本修改，无法比较不等于没有变化。

## 命令行约定

| 退出码 | 校验脚本 | 差异脚本 |
|---|---|---|
| 0 | 符合 Schema | 没有变化 |
| 1 | 解析或 Schema 错误 | 变化需要审阅 |
| 2 | 输入、配置或报告错误 | 无法比较 |

参数误用也返回 2。校验报告包含 valid、stage、errors，规则错误附带实例与 Schema 路径。差异报告包含 report_version、status、facts_verified=false，以及 changes 或错误说明。数组整体比较。报告可能含输入值，需按来源数据的敏感程度保存。

## 边界与限制

- 拒绝重复键、NaN、Infinity、指数溢出。浮点精度及下溢遵循 Python 行为，不是精确十进制校验器。
- 支持自包含 Draft 2020-12 Schema 与文档内引用；不支持外部引用及 $id，未知关键字不会变成业务校验器。
- format 检查依赖 jsonschema FormatChecker 及已安装依赖。
- 不自动补默认值或 null；Schema 合法不表示事实正确。
- 暂无恶意 Schema 或超大文件的资源限制，适用于大小合理的可信本地输入。
- 不内置模型适配器或自动批量修复服务。

## 测试与状态

```console
python -m unittest discover -s tests -v
```

CI 配置覆盖 Python 3.10–3.12，配置存在不等于通过。已执行检查见[测试记录](evals/TEST_RESULTS.md)，Agent 评测方案见[评测场景](evals/README.md)。不宣称模型效果提升。

## 参考

结构参考 [llm-structured-output](https://github.com/sickn33/agentic-awesome-skills/blob/main/skills/llm-structured-output/SKILL.md) 的范围、流程和示例，以及 [ai-output-validation](https://github.com/DevelopersGlobal/ai-agent-skills/blob/main/skills/ai-output-validation/SKILL.md) 的校验、重试与检查点。本文措辞和项目实现独立，不包含上述项目的模型供应商接入能力。

## 验证节点：暂停功能开发

2026-11-10：Windows / Python 3.11.11 下连续三轮通过，每轮包含 21 项单元测试方法（内含输入矩阵）和 9 项命令行检查。覆盖 JSON 标量、非法语法、Schema 约束、本地/缺失/外部引用、数据中的 $ref、数组类型差异、禁止覆盖输入、非法编码、文件缺失及报告写入失败。修复嵌套数组中 true→1、1→1.0 变化漏报，并处理解析递归错误。

本节点暂停功能开发。测试不代表边界已穷尽，也不证明恶意输入资源安全或独立 Agent 修复效果。浮点精度/下溢、Unicode 孤立代理字符、深层/递归 Schema 和资源预算仍属于限制。详见[多轮结果](evals/boundary-results.json)。

## Release v0.1.0 / 发布版本

MIT licensed. [Installation and complete demo / 安装与完整演示](docs/INSTALLATION.md). Run `python scripts/demo.py`. Platform indexing and Agent auto-activation are not certified by local checks.
