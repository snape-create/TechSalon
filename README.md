# TechSalon

本次技术沙龙的演示项目与资料仓库。

主线：**一个 AI 小应用，从「在我机器上能跑」到「别人也能跑、还能自己查数据」**，分三步：

1. **Docker** 固环境：见 `demo_for_docker/`
2. **uv** 管依赖：见 `pyproject.toml`、`uv.lock`、`demoFor_uv/`
3. **MCP** 连世界：见 `Proj/`

## 目录说明

### `Proj/`：自建 MCP 服务器

`Proj/` 是本仓库自己实现的 MCP Server（名称 `weather-db`），基于 **FastMCP**，把根目录 `weather.sqlite3` 中的天气数据查询能力封装成 MCP 工具，供 CodeBuddy 等 Host 调用。

- `Proj/server.py`：MCP Server 入口。默认使用 **stdio** 传输；设置 `MCP_TRANSPORT=http` 时启用 Streamable HTTP，默认端点为 `http://127.0.0.1:8000/mcp`。
- `Proj/tools.py`：数据准备脚本，从和风天气 API 拉取 30 天预报并写入 / 更新 `weather.sqlite3`。

提供的工具：

| 工具 | 作用 |
| --- | --- |
| `list_cities` | 列出数据库中已有的城市、记录天数和日期范围 |
| `get_forecast` | 查询某城市从最早日期开始的天气预报 |
| `get_weather_by_date` | 查询某城市指定日期的完整天气记录 |
| `query_weather_range` | 查询某城市一段日期范围内的天气记录 |

提供的资源：

- `weather://schema`：`weather_data` 表的字段说明，供构造查询时参考。

### `doc/`：文档

`doc/` 存放技术沙龙的整理文档与备查资料：

| 文件 | 内容 |
| --- | --- |
| `docker-summary.md` | Docker 知识点速查 |
| `note.md` | uv 工具笔记与常用命令 |
| `mcp基础.md` | MCP 是什么、Host / Server、数据流转 |
| `mcp进阶.md` | 与基础篇同源的视频转录资料 |
| `MCP三种传输方式.md` | stdio、HTTP+SSE、Streamable HTTP 的演进 |
| `function_calling和mcp.md` | Function Calling 与 MCP 的关系 |
| `resources.md` | 视频与阅读文档链接索引 |

> 说明：仓库中没有单独的 `resources/` 目录，分享里说的 **resources** 目前指 `doc/resources.md`，里面汇总了视频和阅读文档链接。

### 其他文件

- `index.html`：现场幻灯片。按 `→` 翻页，按 `N` 看备注，按 `P` 开演讲者视图。
- `weather.sqlite3`：天气数据库。
- `env_example.env`：和风天气 API 配置示例。
- `demo_for_docker/`：Docker 演示用 Dockerfile。
- `demoFor_uv/`：uv workspace 演示项目。

## 运行方式

环境要求：`Python >= 3.13`，建议使用 `uv`。

```bash
uv sync
```

更新天气数据：

```bash
cp env_example.env .env
# 编辑 .env，填写 weather_api_key 与 weather_url
uv run python Proj/tools.py
```

启动 MCP Server：

```bash
# 默认 stdio
uv run python Proj/server.py

# Streamable HTTP
MCP_TRANSPORT=http uv run python Proj/server.py
```

在 CodeBuddy 的 MCP 配置中接入 HTTP 方式示例：

```json
{
  "mcpServers": {
    "weather-db": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

## 资料

视频与阅读文档链接见 [`doc/resources.md`](doc/resources.md)。
