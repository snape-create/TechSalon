# 技术沙龙 · 分享素材导览

> 主线：**一个 AI 小应用，从「在我机器上能跑」到「别人也能跑、还能自己查数据」，要跨三道坎。**
> Docker 固环境（第一道）→ uv 管依赖（第二道）→ MCP 连世界（第三道）。

## 一、现场讲什么：以 `index.html` 幻灯片为准

- 幻灯片是唯一讲稿，按 `→` 翻页；按 `N` 看备注，按 `P` 开演讲者视图（备注里有完整讲法）。
- 时间分配（30–40 分钟）：Docker 10–12 min、uv 8–10 min、MCP 12–15 min。
- 每个部分**只现场敲一段** demo，其余用预录/截图。

## 二、现场 demo 在哪

| 部分 | 演示内容 | 文件 |
|---|---|---|
| Docker | C++ 镜像构建（容器输出 Hello world!） | `demo_for_docker/Dockerfile` |
| uv | 从零走一遍 `init → add → run`（1 分钟） | 现场敲，无需现成文件 |
| MCP | 天气数据库 Server，把 `weather.sqlite3` 的查询封装成工具 | `Proj/server.py` + `Proj/tools.py` |

> 依赖已装在 `.venv`（`fastmcp`、`mcp<2`、`requests`、`dotenv` 等），`uv run` 或激活环境即可运行。

## 三、`doc/` 里的总结怎么用：当弹药库，不当讲稿

| 文件 | 用途 | 优先级 |
|---|---|---|
| `docker-summary.md` | Docker 全部知识点速查（讲义提炼） | ★★ 备查 |
| `note.md` | uv 一站式工具总结 + 常用命令速查 | ★★ 备查 |
| `function_calling和mcp.md` | **差异化亮点**：Function Calling 与 MCP 的关系 | ★★★ 重点讲 |
| `MCP三种传输方式.md` | **差异化亮点**：stdio → SSE → Streamable HTTP 演进 | ★★★ 重点讲 |
| `mcp基础.md` | MCP 是什么 / Host / Server / 安装 / 数据流转 | ★★ 备查 |
| `mcp进阶.md` | ⚠️ 内容与 `mcp基础.md` 相同（同一段视频转录），不算进阶篇 | ★ 忽略 |
| `resources.md` | 视频与讲义原始链接 | ★ 备查 |

## 四、需要纠正的过时说法

- `MCP三种传输方式.md` 明确：**HTTP+SSE 已废弃**（MCP 2024-11-05 定义），现行远程方案是 **Streamable HTTP**（2025-03-26 引入，2025-06-18 成为标准）。
- 幻灯片里已按此修正；如果引用旧视频/旧资料里"远程用 HTTP/SSE"的说法，记得说明它已过时。

## 五、原始资料链接

### uv 官方与教程
- 官方文档：https://uv.oaix.tech/
- B 站视频：https://www.bilibili.com/video/BV1Stwfe1E7s/

### MCP
- Function Calling / MCP 讲解：https://www.bilibili.com/video/BV1qTYizcEN3/
- Function Calling 补充：https://www.bilibili.com/video/BV15YJTzkENC/
- MCP 基础篇：https://www.bilibili.com/video/BV1uronYREWR/
- ⚠️ 所谓"进阶篇"链接与基础篇是同一个（BV1uronYREWR），目前没有真正的进阶篇视频

### Docker
- 讲义：https://summer25.net9.org/backend/docker/note/
