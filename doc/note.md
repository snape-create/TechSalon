# UV 一站式 Python 项目管理工具

## 背景：Python 生态工具碎片化

- 版本管理用 pyenv、虚拟环境用 venv/virtualenv、依赖管理用 pip/poetry、代码检查用 ruff、打包发布又是另一套工具……
- 各自独立、配置繁琐、依赖冲突频发，新人上手成本高。
- 有没有一个工具能把全流程串起来？—— **UV**（Astral 出品，Rust 编写，最大特点是"快"）。

## UV 核心能力：一站式全流程

一个工具统一完成：

- Python 版本安装与管理
- 虚拟环境创建
- 项目依赖管理（含锁文件）
- 全局开发工具安装
- 项目打包与发布

## 实操演示流程（基于 AI Agent 示例项目）

### 1. 管理 Python 解释器版本

- `uv python list`：查看 UV 支持的 Python 版本（3.7 ~ 3.14 预发布，含 PyPy）
- `uv python install <版本>`：安装指定 Python
- `uv run -p <版本> 脚本.py`：临时用指定版本运行；缺失版本 UV 会自动下载，无需手动 `install`

### 2. 新建项目 & 管理依赖

- `uv init -p <版本>`：初始化项目，自动生成 `pyproject.toml`、`.python-version` 等配置文件
- `uv add <包名>`：安装依赖，自动创建 `.venv` 虚拟环境，依赖写入 `pyproject.toml`，同时生成 `uv.lock`
- VSCode 切换解释器到项目 `.venv`，消除"找不到模块"的提示
- `uv run 脚本.py`：在项目虚拟环境中运行代码
- `uv tree`：查看完整依赖树

### 3. 区分项目依赖与全局工具（重点）

- `uv add --dev <包名>`：开发期依赖（pytest、mock 等），属于项目相关依赖，打包时排除
- `uv tool install <工具>`：全局独立工具（如 ruff），每个工具自带隔离虚拟环境，不污染项目、无依赖冲突，全系统可用
- 配套命令：`uv tool list` 查看全局工具、`uv tool run`（或 `uvx`）临时运行工具、`uv remove` 移除项目依赖

### 4. 打包与分发

- 在 `pyproject.toml` 配置 `[project.scripts]`，定义可执行命令名称
- `uv build`：打包生成 wheel / sdist 安装包，可上传 PyPI 分发
- 他人可通过 `uv tool install <本地路径 / 线上包>` 安装，生成全局独立可执行命令，自带隔离环境，脱离原开发环境即可运行

## 补充：常用命令速查

| 场景 | 命令 |
| --- | --- |
| 安装 UV 本身 | `curl -LsSf https://astral.sh/uv/install.sh \| sh`（或 `pip install uv` / `brew install uv`） |
| 创建虚拟环境 | `uv venv` |
| 同步环境（按锁文件还原） | `uv sync` |
| 生成 / 更新锁文件 | `uv lock` |
| 临时增加一次性依赖运行 | `uv run --with <包名> 脚本.py` |
| 一次性运行工具（不落盘安装） | `uvx <工具>` |
| 兼容旧项目（pip 替代品） | `uv pip install -r requirements.txt` |
| 查看已安装依赖 | `uv pip list` |

## 补充：为什么快 & 最佳实践

- **快的原因**：Rust 实现、全局缓存复用、并行下载与解析，且引导安装 UV 本身不依赖系统 Python。
- **锁文件 `uv.lock`**：记录精确版本，保证不同机器 / CI 环境安装结果一致，建议提交到版本库。
- **环境复现**：换机器或 CI 中只需 `uv sync`，即可按 `uv.lock` 一键还原完整环境，适合新同事 onboarding。
- **兼容性好**：可直接读取 `pyproject.toml`、`requirements.txt`，能平滑迁移现有项目；`uv pip` 可作为 pip 的提速替代品。
- **选型建议**：项目内依赖用 `uv add`，通用命令行工具用 `uv tool install`，二者环境隔离、互不干扰。

## 总结

UV 用一套命令打通了"版本 → 环境 → 依赖 → 工具 → 打包发布"的完整链路，以速度、可复现的锁文件和干净的环境隔离，替代了过去多工具拼凑的繁琐流程。
