# B05 反思与记忆研究工程

当前是通用研究工程骨架，采用原生 Python。基础配置、JSON 自检和诊断日志已经可用；智能体、反思方法及记忆方法尚未实现。当前不能作为完成的评测方案提交。

## 目录

```text
b05_reflection/
├── Dockerfile                 # 与官方模板相同的 Python 3.11 运行基线
├── run.sh                     # 固定入口
├── requirements.txt           # 当前只使用标准库
├── pyproject.toml             # 项目和包信息
├── src/
│   ├── main.py                # 官方启动参数入口
│   └── b05_reflection/
│       ├── cli.py             # 命令行、自检、诊断记录
│       ├── config.py          # 环境变量和目录配置
│       ├── agents/            # 通用研究流程位置，待实现
│       ├── reflection/        # 反思研究方法位置，待实现
│       └── memory/            # 记忆研究方法位置，待实现
├── configs/                   # 配置约定，不存放密钥
├── data/examples/             # 无领域含义的本地自检样例
├── data/local/                # 本地资料位置，不进入镜像或版本库
├── experiments/               # 实验说明和记录
├── outputs/                   # 运行产物，不进入版本库
├── tests/                     # 后续方法测试的位置
└── docs/
    ├── requirements.md        # 运行与交付约定
    └── decisions.md           # 已确定选型、待讨论问题和下一阶段
```

## 本地自检

在本目录使用 Python 3.11 或更高版本运行：

```powershell
python src/main.py --check-only --data-root data/examples --out-dir outputs
```

程序读取输入 JSON，检查语法并记录摘要，写入：

```text
outputs/diagnostics/check_report.json
outputs/diagnostics/research.log
```

自检不会请求模型，也不会生成预测或评测答案。输入样例只验证工程读写，不是官方场景。现有 `../pre/` 中的资料通过路径引用，避免复制到代码包中。

## 官方入口形状

```bash
bash run.sh --task all --test --out-dir /output
```

入口接受官方参数，但研究执行器尚未实现：未传 `--check-only` 时返回退出码 2，并明确提示尚未实现，不生成空答案。自检失败返回 1，通过返回 0。

`DATA_ROOT` 默认为 `/input`，`OUTPUT_DIR` 默认为 `/output`；`--data-root` 仅用于方便本地自检，`--out-dir` 优先于环境变量。

## 模型配置

读取官方注入的 `LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL`；可选读取 `LLM_USE_JSON_SCHEMA`、`LLM_ENABLE_THINKING`。目前只检查配置是否存在，尚未连接模型。诊断中不保存密钥或地址值。

配置说明见 [configs/README.md](configs/README.md)，研究选型见 [docs/decisions.md](docs/decisions.md)。

## 容器入口

Docker 服务启动后，可在本目录运行：

```bash
docker build -t b05-reflection .
docker run --rm b05-reflection --help
```

镜像仅包含运行入口和源码，数据通过运行时只读挂载提供。当前开发环境的 Docker 服务未启动，容器构建仍待实际验证。
