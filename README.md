# B05 Reflection

反思与记忆研究工程。当前提供配置读取、JSON 输入自检和诊断记录，研究算法与模型调用尚未实现。

## Docker 运行

启动 Docker 的 Linux 容器服务后，在项目根目录执行：

```bash
docker compose --env-file .env.example run --rm --build research
```

诊断结果写入 `outputs/docker/diagnostics/`。修改源码或依赖后重新构建；仅修改挂载的配置文件时直接重跑即可。

## Conda 开发环境

在 Anaconda Prompt 或已初始化 Conda 的终端中执行：

```bash
conda env create --file environment.yml --no-default-packages
conda activate b05-reflection
python -m pip install -r requirements.txt
python src/main.py --check-only --config configs/config.example.toml
```

开发环境由 `environment.yml` 定义，Python 版本为 3.11。Docker 使用独立的 Linux 运行时，不依赖主机解释器。

## 配置

- [`.env.example`](.env.example)：环境变量和 Docker 挂载路径示例。
- [`configs/config.example.toml`](configs/config.example.toml)：非敏感运行参数。
- [配置说明](configs/README.md)：参数含义与读取方式。

优先级为：命令行 > 非空环境变量 > TOML > 默认值。模型参数只读取环境变量，程序不自动加载 dotenv 文件。

## 检查

激活开发环境后运行：

```bash
python -m unittest discover -s tests -v
```

CI 检查 Python 测试、运行入口和容器自检。

## 结构

```text
src/b05_reflection/   配置、入口及研究模块
configs/             配置说明与模板
data/examples/       自检样例
experiments/         实验说明
tests/               测试
docs/                运行与交付约定
```

固定入口为 `run.sh`。当前需添加 `--check-only` 才执行工程自检；研究执行器未实现时返回退出码 2。运行与交付约定见 [docs/requirements.md](docs/requirements.md)。
