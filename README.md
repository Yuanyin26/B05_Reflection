# B05 Reflection

通用反思与记忆研究工程，采用原生 Python。当前可进行 JSON 自检、配置存在性检查和诊断记录；研究算法与模型调用尚未实现。

仓库：[Yuanyin26/B05_Reflection](https://github.com/Yuanyin26/B05_Reflection)。本机目录为 `Reflection`，克隆后默认目录为 `B05_Reflection`；以下命令都在仓库根目录执行。Python 包名保持 `b05_reflection`。

## 获取代码

已配置 GitHub SSH 的成员可运行：

```bash
git clone git@github.com:Yuanyin26/B05_Reflection.git
cd B05_Reflection
git switch dev
```

日常在 `dev` 开发，稳定版本通过 Pull Request 合并至 `main`。

## 配置示例

- [`.env.example`](.env.example)：Docker 挂载路径和环境变量清单，模型字段保留空值。
- [`configs/config.example.toml`](configs/config.example.toml)：非敏感的输入输出目录和日志级别，支持 `--config` 实际读取。

读取 env 示例启动：`docker compose --env-file .env.example run --rm --build research`。

程序不自动加载 `.env`；正式运行的模型参数由环境注入。配置优先级和使用方法见[配置说明](configs/README.md)。

## 快速运行

首选 Docker Compose：Windows 上启动 Docker Desktop 并使用 Linux 容器；Linux 主机启动 Docker 服务。Windows 可直接使用 PowerShell，代码无需搬入 WSL。

在仓库根目录执行：

```bash
docker compose run --rm --build research
```

这一条命令会构建 **Linux＋Python 3.11** 镜像，读取两个普通 JSON 样例，并将诊断结果写回本机：

```text
outputs/docker/diagnostics/check_report.json
outputs/docker/diagnostics/research.log
```

首次构建需要下载基础镜像。`compose.yaml` 已配置输入和TOML配置只读挂载，以及输出目录；自检完成后容器自动移除。当前只验证工程运行，不请求模型。

镜像已经构建、源码未变化时，再次自检可直接运行：

```bash
docker compose run --rm research
```

修改源码或依赖后再加 `--build`；只改挂载的TOML或环境变量时，重新运行即可。如果下载镜像时 Docker Hub 连接超时，参见[配置说明中的网络处理](configs/README.md#docker-镜像下载)。

如果 Docker 提示无法连接引擎，先启动 Docker Desktop。使用以下命令确认引擎类型，期望输出 `linux`：

```bash
docker info --format '{{.OSType}}'
```

## 本地 Python 运行（可选）

需要直接调试 Python 时，再使用本节。运行基线为 **Python 3.11**，当前运行依赖全部来自标准库。

Windows PowerShell，已安装 Python 3.11 时：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\examples\run_local.ps1
```

Linux：

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
bash examples/run_local.sh
```

示例脚本优先使用仓库内的 `.venv`，从任意工作目录调用均可。也可直接运行：

```bash
python src/main.py --task all --test --check-only --data-root data/examples --out-dir outputs/local
```

本地脚本生成 `outputs/local/diagnostics/check_report.json` 和 `research.log`。它们和容器调用同一份源码。

## 目录

```text
Reflection/                     # Git 仓库根目录
├── .github/workflows/ci.yml     # GitHub 自动检查
├── .env.example                # 环境变量与主机挂载路径模板
├── compose.yaml                # Windows / Linux 统一容器入口
├── Dockerfile                  # Python 3.11 Linux 镜像
├── run.sh                      # 官方固定入口
├── requirements.txt
├── pyproject.toml
├── examples/                   # 可选的本地 Python 运行脚本
├── src/
│   ├── main.py
│   └── b05_reflection/
│       ├── cli.py              # 自检与诊断
│       ├── config.py           # 环境变量配置
│       ├── agents/             # 待实现
│       ├── reflection/         # 待实现
│       └── memory/             # 待实现
├── configs/                    # 配置说明和config.example.toml
├── data/examples/              # 可入库的通用样例
├── data/local/                 # 本地资料，不入库
├── outputs/                    # 运行结果，不入库
├── experiments/                # 实验说明
├── tests/                      # 标准库 unittest 检查
└── docs/                       # 需求与选型记录
```

GitHub 克隆不包含本机仓库外的 `../pre/` 资料。需要的资料通过路径引用，或自行放入已忽略的 `data/local/`。文本换行由 `.gitattributes` 统一；Shell 文件使用 LF。

## GitHub 自动检查

工作流在推送至 `dev`、`main` 或创建／更新 Pull Request 时运行，也支持从 GitHub 手动触发。

- Windows、Linux：使用 Python 3.11，运行测试和样例自检。
- Linux：检查 Shell 入口，并通过同一份 Compose 配置构建、运行容器自检。
- CI 不需要模型密钥，不调用模型，也不发布镜像或部署服务。

本地运行相同的 Python 测试：

```bash
python -m unittest discover -s tests -v
```

工作流配置上传后，到仓库的 **Actions** 页面查看实际结果。本地检查不代表 GitHub 工作流已运行。

## 容器辅助命令

查看程序帮助：`docker compose run --rm research --help`。

检查容器中的 Python：`docker compose run --rm --entrypoint python3 research --version`。

镜像只包含源码和入口，输入数据在运行时只读挂载。Compose 用于本地开发与自检；官方仍通过 `Dockerfile` 和 `run.sh` 启动程序。

2026-11-25 已在本机通过实际镜像构建和容器自检，容器为 Linux、Python 3.11.18，两个输入样例通过且输入内容未改变。GitHub CI 的执行结果另以 Actions 日志为准。

## 官方参数与模型配置

官方调用形状为 `bash run.sh --task <值> --test --out-dir /output`。当前入口接受这些参数；研究执行器未实现时返回退出码 2，不生成评测答案。添加 `--check-only` 后可运行工程自检，通过返回 0，失败返回 1。

`DATA_ROOT` 默认 `/input`，`OUTPUT_DIR` 默认 `/output`，显式命令行参数优先。模型配置读取官方注入的 `LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL` 等变量，目前只检查是否存在，不代表模型已连接。

详见 [配置说明](configs/README.md)、[运行与交付约定](docs/requirements.md)、[选型记录](docs/decisions.md)。
