# Structured Output Check

校验 AI 生成的 JSON，并指导 Agent 在有限次数内修复结构错误的 Skill。

适用于模型输出无法解析、字段缺失、类型不符、额外字段和 Schema 约束不满足的情况。校验通过仅表示结构符合约定，不代表业务事实正确。

## 工作方式

```text
原始输出 + JSON Schema
          ↓
    确定性校验脚本
          ↓
   错误报告 → Agent 修复候选
                   ↓
              再次校验（默认最多两轮）
```

脚本不调用模型、不需要 API Key，也不自动覆盖原始输入。修复由支持 Skill 的 Agent 按 SKILL.md 执行；需要权威信息才能补充的业务字段，信息不足时停止并报告。

## 快速开始

需要 Python 3.10+，在仓库根目录执行：

```console
python -m pip install -r requirements.txt
python scripts/validate.py --input examples/valid.json --schema examples/schema.json --report report.json
```

有效示例输出：

```json
{"valid": true, "stage": "validation", "errors": []}
```

运行失败示例：

```console
python scripts/validate.py --input examples/invalid.json --schema examples/schema.json --report invalid-report.json
```

示例中的 `count` 为字符串，而 Schema 要求整数；报告会给出 `instance_path: ["count"]` 以及对应 Schema 路径。

| 退出码 | 含义 |
|---|---|
| 0 | 数据通过校验 |
| 1 | JSON 解析失败或数据不符合 Schema |
| 2 | 输入读取、依赖、Schema 或报告写入失败 |

命令行参数误用由 argparse 返回退出码 2。

## 在 Agent 中使用

将完整仓库文件夹放入宿主支持的 Skill 目录，文件夹名保留为 `structured-output-check`，确保根目录存在 SKILL.md。安装 Python 依赖后，可提出：

> 使用 structured-output-check 检查 original.json 是否符合 schema.json；如果可以根据已有事实修复，最多尝试两轮，每轮保留候选文件和校验报告，不覆盖原始文件。

安装目录及自动发现方式以所用 Agent 的文档为准。直接运行 Python 命令只会校验，不会自动修复。SKILL.md 中的命令相对于本仓库目录执行；从其他目录使用时请切换工作目录或使用完整路径。

## 校验规则与边界

- 支持 JSON Schema Draft 2020-12、自包含 Schema 和本地片段引用。
- 拒绝重复对象键、NaN、Infinity 和外部 Schema 引用。
- 使用 jsonschema FormatChecker；具体格式的支持取决于已安装依赖。
- 不提供事实核验、自定义业务规则执行、模型调用和远程引用解析。
- 不将 Schema 的默认值自动写入数据，不保证修复一定成功。
- 适用于可信大小的本地输入，尚未针对超大文件和恶意复杂 Schema 做资源限制。

## 目录

```text
structured-output-check/
├── SKILL.md
├── README.md
├── requirements.txt
├── scripts/validate.py
├── examples/
│   ├── schema.json
│   ├── valid.json
│   └── invalid.json
└── tests/test_validate.py
```

## 验证与开发状态

```console
python -m unittest discover -s tests -v
```

2026-11-09：Python 3.11 环境下 7 项单元测试通过，覆盖合法数据、错误路径、严格 JSON 解析、字段约束、非法 Schema、外部引用拒绝和本地引用。此结果验证校验脚本，不证明 Agent 修复效果。

当前为早期版本。尚未完成真实 Agent 修复评测，也没有成功率提升或效率收益数据。后续将补充固定评测集、修复轨迹和三组基线对照：直接模型、模型加脚本、模型加脚本和 Skill。

本项目独立维护。api-regression、test-failure-triage、agent-tool-test 和 migration-review 将分别使用独立仓库。
