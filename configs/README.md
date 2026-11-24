# 配置模板与读取方式

| 模板 | 用途 | 读取方式 |
| --- | --- | --- |
| [`.env.example`](../.env.example) | Docker 挂载路径、可覆盖的环境变量清单；模型字段为空 | `docker compose --env-file .env.example ...` 显式读取 |
| [`config.example.toml`](config.example.toml) | 非敏感的输入输出目录和日志级别 | Python 的 `--config`；Compose 默认只读挂载并读取 |

运行配置优先级：**命令行 > 非空环境变量 > TOML 文件 > 内置默认值**。TOML 中的相对路径以该文件所在目录为基准。模型参数始终只从 `LLM_*` 环境变量读取。

显式使用 env 示例运行容器：

```bash
docker compose --env-file .env.example run --rm --build research
```

不传 `--env-file` 时，Compose 使用模板中相同的缺省挂载路径；程序不会自动搜索或加载 `.env`。正式评测仍由服务注入模型参数，所有 `.env*` 文件均排除在镜像之外。

直接使用 TOML 运行本地 Python 自检：

```bash
python src/main.py --check-only --config configs/config.example.toml
```

可将 TOML 复制为 `configs/config.local.toml` 后编辑，再通过 `--config` 指定；该本地文件已被 Git 忽略。容器中 `DATA_ROOT=/input`、`OUTPUT_DIR=/output` 会优先于 TOML 的本地目录，日志级别仍可从 TOML 读取。

环境变量约定：

| 变量 | 用途 | 缺省处理 |
| --- | --- | --- |
| `DATA_ROOT` | 输入目录 | `/input` |
| `OUTPUT_DIR` | 输出目录 | `/output` |
| `B05_LOG_LEVEL` | 覆盖日志级别 | 未设置时使用 TOML，再缺省为 `INFO` |
| `LLM_BASE_URL` | 官方模型网关 | 不设置默认地址 |
| `LLM_API_KEY` | 官方注入凭证 | 不设置默认密钥 |
| `LLM_MODEL` | 官方指定模型 | 不设置默认模型名 |
| `LLM_USE_JSON_SCHEMA` | 可选能力标记 | 未提供时为未知；提供时只能是 `0` 或 `1` |
| `LLM_ENABLE_THINKING` | 可选能力标记 | 未提供时为未知；提供时只能是 `0` 或 `1` |

`.env.example` 中的 `B05_INPUT_DIR`、`B05_OUTPUT_DIR`、`B05_CONFIG_FILE` 分别控制主机输入目录、主机输出目录和只读挂载的 TOML 文件。它们与容器内的 `/input`、`/output` 路径分开。

示例不填真实密钥、网关或模型名；程序不自动加载 dotenv 文件，TOML 也不接受模型凭证。当前自检只记录模型参数是否存在，不代表已连通。客户端实现前，超时、重试和调用预算需要另行确定。

## 本地环境变量示例

在仓库根目录的 PowerShell 中：

```powershell
$env:DATA_ROOT = (Resolve-Path data/examples).Path
$env:OUTPUT_DIR = Join-Path (Get-Location).Path "outputs/env-example"
python src/main.py --check-only
```

在 Bash 中：

```bash
DATA_ROOT="$PWD/data/examples" OUTPUT_DIR="$PWD/outputs/env-example" \
  python3 src/main.py --check-only
```

这两个示例只设置输入输出目录。模型参数由获授权的运行环境注入，示例和 GitHub CI 均不需要设置模型密钥。

## GitHub 与本地资料

- `data/examples/` 中的通用样例随仓库提交。
- `data/local/`、`outputs/`、虚拟环境和运行缓存由 `.gitignore` 排除。
- `.env.example` 和 `config.example.toml` 可提交；真实 `.env*` 及 `configs/*.local.toml` 被忽略，所有 env 文件和配置目录均不进入镜像。
- 仓库外的官方资料通过路径引用；克隆仓库时不自动下载。
- GitHub Actions 使用 Python 3.11，在 Windows、Linux 和 Linux 容器中检查工程入口；容器使用同一份 Compose 配置，不进行模型调用。

## Docker 镜像下载

如果构建出现 `failed to fetch oauth token` 或连接 `auth.docker.io` 超时，先检查镜像仓库连通性。Windows 系统代理可用时，构建工具仍可能需要命令行代理变量。

以下 PowerShell 示例读取现有系统代理，只设置当前终端进程的环境变量；不将代理地址写入项目，也不更改全局配置：

```powershell
$dockerAuthUri = [Uri]"https://auth.docker.io"
$dockerProxyUri = [System.Net.WebRequest]::DefaultWebProxy.GetProxy($dockerAuthUri)
if ($null -eq $dockerProxyUri -or $dockerProxyUri.Host -eq $dockerAuthUri.Host) {
    throw "没有检测到适用的系统代理，请先检查网络或现有代理软件。"
}
$env:HTTP_PROXY = $dockerProxyUri.AbsoluteUri
$env:HTTPS_PROXY = $dockerProxyUri.AbsoluteUri
docker compose run --rm --build research
```

本机首次构建已验证：直连镜像认证服务超时，临时沿用现有系统代理后构建和自检成功。镜像构建完成且源码未变化时，可用 `docker compose run --rm research` 直接重跑，无需再次构建。
