# MCP 的三种传输方式

> 整理说明：本文把《mcp基础》《function_calling和mcp》两段视频中关于传输方式的内容系统化，并对照 MCP 官方规范（specification）核对了最新状态。
> 常说的"三种传输方式"指：**stdio**、**HTTP + SSE**、**Streamable HTTP**。它们解决的是同一个问题——**MCP client 与 MCP server 之间如何传递 JSON-RPC 消息**，只是走的路子不同：本地走进程通信，远程走网络。

---

## 〇、先把位置摆正：传输方式在 MCP 架构里是哪一层

MCP 采用 C/S 架构，三个核心角色：

```
        一台电脑 = MCP host（AI 应用，如 VS Code / Cline / Cursor / Trae）
   ┌─────────────────────────────────────────────────────┐
   │  MCP client ①   MCP client ②   MCP client ③         │  ← 实例化在应用后端内部，与 server 一对一
   └────┬──────────────┬──────────────┬──────────────────┘
        │ stdio        │ HTTP+SSE     │ Streamable HTTP
        ▼              ▼              ▼
   本地 MCP server  远程 MCP server  远程 MCP server
   （一条命令行配置） （一个 URL 配置）  （一个 URL 配置）
   "三条远程数据线 + 一条本地数据线" —— 视频里那张经典架构图
```

**传输方式（transport）是绑定层（binding）**：它只规定"消息如何分帧、如何传递、请求元数据怎么带、如何取消和终止"，**不改变消息语义**。协议语义（JSON-RPC 的 request / response / notification 模式）在所有传输方式上完全相同。

- 所有消息都用 **JSON-RPC 2.0** 编码，且**必须是 UTF-8**。
- 方向是固定的：client 只能发 requests 和 notifications，server 只能回 responses 和 notifications（server 不主动发起 JSON-RPC 请求）。

这就是"即插即用"的基础：AI 应用只要支持这几种传输方式，任何人的 server 都能接进来。

---

## 一、stdio（标准输入输出）

### 定位
**本地进程间通信**方式。视频里说"MCP server 一共有两种沟通方式，stdio 和 sse，目前大部分 MCP 用的是 stdio"——指的就是本地这一大类。

### 原理
- client 把 MCP server 作为**子进程启动**（配置里的 `command` + `args`，如 `npx`、`uvx` 命令）。
- server 从**标准输入 `stdin`** 读 JSON-RPC 消息，向**标准输出 `stdout`** 写消息。
- 消息是**按行分隔（newline-delimited）的 JSON-RPC**，每条消息内部不能含换行符。
- server 可以向 `stderr` 写 UTF-8 字符串做日志，client 可捕获/转发/忽略。
- **硬规矩**：`stdout` 里绝不能出现任何非 MCP 消息的内容（否则协议就乱了）；client 也不能往 `stdin` 写非 MCP 消息。这也解释了视频里"server 启动后停在那、什么都不输出是正常的"——它在等 stdin 的指令。

### 底层机制
- 操作系统给每个进程启动时会分配三个文件描述符：
  - `stdin` 标准输入 —— 默认来自键盘
  - `stdout` 标准输出 —— 默认到屏幕
  - `stderr` 标准错误
- 代码里的 `printf` / `scanf` / `System.in` 就是通过这套接口与外界交换数据。
- 串起两个进程的是**管道（pipe）**：内核提供的进程间通信机制，把 A 进程的 stdout 直接接到 B 进程的 stdin，形成一个**全双工通道**。
- 经典例子：`ps aux | grep python`——把 `ps aux` 的输出作为 `grep` 的输入，先列出所有进程再过滤出 python 进程。

### 为什么选 stdio（而不是共享内存、消息队列、信号量等一堆"八股"）
本质原因就俩字：**简单**。MCP client/server 之间主要传的是 JSON，没必要为了这点数据去自己管理共享内存（共享内存是为了快，这里不缺那点性能）。

### 配置形态
```json
{
  "mcpServers": {
    "amap": {
      "command": "npx",
      "args": ["..."],
      "env": { "..." : "..." }
    }
  }
}
```
本质就是**一条命令行配置**：host 执行它，把包拉下来、启动一个本地 MCP server 进程。视频里"启一个本地服务，通过进程间通信方式接入"说的就是它。取消请求时，client 发送 `notifications/cancelled` 通知。

---

## 二、HTTP + SSE（早期远程方案，现已废弃）

### 定位
**远程服务接入**的初代方案，MCP 协议 **2024-11-05** 版本定义。视频里讲的"远程三个 server 用 HTTP+SSE 接入"就是这个。

### 原理
- 客户端发请求：普通 **HTTP POST**。
- 服务端回消息：走 **SSE（Server-Sent Events）通道**。
- 需要**两个端点**：一个 `/messages`（POST 用）和一个 `/sse`（SSE 用）。

### 为什么当初不用普通 HTTP，非要引入 SSE
普通 HTTP 是"请求—响应"一问一答，服务端不能主动开口；而 SSE 与普通 HTTP 的核心差异是**支持服务端主动推送、流式推数据**。

MCP 有一个硬需求：**MCP server 的工具列表可能变化，变化时必须主动通知 client**（`notifications/tools/list_changed`），让 client 收到通知后立刻重新拉一次最新工具列表。这个"服务端主动发消息"的能力必须靠推送机制实现，SSE 正好满足。

附带好处：拉很长的数据时可以流式、及时地响应。

### 局限
- SSE 的 `Content-Type` **只能支持文本格式**；
- 支持的客户端主要针对**浏览器**，跨平台兼容性差；
- 性能不如后来者；
- 需要维护两个端点，较繁琐。

### 现状
**已废弃（deprecated）**，被 Streamable HTTP 取代。官方规范明确将其标为 deprecated，仅为向后兼容保留。兼容做法：服务端同时保留旧的 SSE/POST 端点与新的 MCP 端点；客户端先尝试 POST 一个 `InitializeRequest`，成功则是新方案，若返回 4xx 再 GET 打开 SSE 流、等 `endpoint` 事件，判断为旧方案。

---

## 三、Streamable HTTP（现行远程方案）

### 定位
**远程服务接入**的现行标准。MCP **2025-03-26** 版本引入，**2025-06-18** 起成为标准传输之一；2024-11-05 的 HTTP+SSE 被它替换。视频里说"现在已经更新成 streamable HTTP 传输"就是它。

> 注意它不是某个标准组织起的协议名，而是"**基于 HTTP 的可流式传输**"这一类技术的称呼。

### 原理（相对 SSE 的关键变化）
- server 作为独立进程，可处理多个 client 连接。
- **只需要一个 MCP 端点**（如 `https://example.com/mcp`），同时支持 **POST 和 GET**：
  - **client → server**：每一条 JSON-RPC 消息都是一次**新的 HTTP POST**。POST 体是单个 request / notification / response。请求头 `Accept` 必须同时声明 `application/json` 和 `text/event-stream`。
  - **server → client 的响应**：可以二选一——
    - 返回一个普通 JSON 对象（`Content-Type: application/json`）；
    - 或开启一条**请求级的 SSE 流**（`Content-Type: text/event-stream`），流式返回多条消息。
  - **client 监听 server 的主动消息**：可以发一个 **HTTP GET** 到该端点，打开一条 SSE 流（`Accept: text/event-stream`），server 在上面发 notifications / requests；若 server 不支持则回 `405 Method Not Allowed`。
- 也就是说：**SSE 不再是独立的通道，而是"按需、按请求"挂到统一 HTTP 端点上的流式响应**——把两个端点收敛成一个。

### 相比 HTTP + SSE 的优势（视频里点的三条）
1. **任意 Content-Type**：不再限于文本，可传任意格式数据；
2. **跨平台兼容**：不再只面向浏览器；
3. **性能更好**。

外加工程上的好处：支持**断线重连与消息重放**（SSE 事件带 `id`，client 用 `Last-Event-ID` 续传）、支持**会话管理**（`Mcp-Session-Id`）、支持**版本头**（`MCP-Protocol-Version`）。

### 安全要求（官方规范强调）
1. server **必须**校验所有入站连接的 `Origin` 头，防止 DNS rebinding 攻击；
2. 本地运行时应只绑定 `127.0.0.1`，不要绑定 `0.0.0.0`；
3. 应对所有连接做 proper authentication。

### 配置形态
和 SSE 一样，本质就是**一个 URL**：
```json
{ "mcpServers": { "xxx": { "url": "https://example.com/mcp" } } }
```

### 有些框架直接支持普通 HTTP？（视频里的追问）
可以。作者给的观察：某些 Agent 框架的 MCP client 是**随时用、随时销毁的局部变量**，没有全局维护长连接，因此**不存在"工具更新必须通知"的问题**；而 MCP tool 绝大多数场景只传一个 JSON、不需要多文本，流式也不必要；HTTP 大家都熟，于是就直接支持了。只要 server 端与 client 端双方能对齐协议，就 OK。

---

## 四、三种方式横向对比

| 维度 | stdio | HTTP + SSE（已废弃） | Streamable HTTP（现行） |
|---|---|---|---|
| 场景 | 本地进程间 | 远程服务 | 远程服务 |
|  transports 本质 | stdin/stdout + 管道，按行分隔 JSON | POST 发请求 + SSE 通道回响应 | 单一端点，POST 发消息，响应为 JSON 或请求级 SSE 流 |
| 端点数 | 无（进程流） | 2 个（POST + SSE） | 1 个（同时支持 POST/GET） |
| 数据格式 | JSON-RPC 2.0（UTF-8） | JSON-RPC 2.0 + SSE 文本 | JSON-RPC 2.0，任意 Content-Type |
| 服务端主动通知 | 全双工天然支持 | 支持（选它的根本原因） | 支持（GET 开 SSE 流 / 请求级流） |
| 跨平台 | 本地进程，无网络问题 | 主要面向浏览器，兼容性差 | 好 |
| 性能 | 高（本地通信，简单） | 一般 | 更好，支持流式与断线续传 |
| 配置形态 | 一条命令行（command + args） | 一个 URL | 一个 URL |
| 典型启动器 | `uvx`（Python）/ `npx`（Node） | 远程部署的服务 | 远程部署的服务 |
| 官方状态 | 标准传输，client 应尽量支持 | deprecated，仅向后兼容 | 标准传输，推荐用于远程 |

---

## 五、演进脉络一句话记住

```
本地场景：stdio（因"简单"被选中，传 JSON 足够）
                  ┐
远程场景：HTTP+SSE ┘→ 为了"服务端主动通知工具更新"而引入 SSE
        → Streamable HTTP：把两个端点收敛成一个，支持任意格式/跨平台/更高性能
```

- **变的是"怎么送"**（binding），**不变的是"送什么"**（JSON-RPC 2.0 的消息语义、client/server 交互模式）。
- 所以视频反复强调的 host / client / server 架构、`tools/list`、`tools/call`、`notifications/tools/list_changed` 这些接口，在三种传输方式上都是一样的。

---

## 六、官方现状补充说明（截至最新规范）

- 最新的 MCP 规范（**2026-07-28**）把标准传输**精简为两种 binding**：**stdio** 与 **Streamable HTTP**；HTTP+SSE 已不在标准传输之列（历史版本中标为 deprecated）。
- 规范同时允许实现**自定义传输（custom transport）**：只要保留 JSON-RPC 消息格式、消息模式与逐请求元数据模型即可；若运行在可靠双向字节流上（如 Unix domain socket、TCP），**建议直接复用 stdio 的分帧方式**，只重写进程生命周期规则。
- 取消请求的语义保持一致：stdio 用 `notifications/cancelled`；Streamable HTTP 用关闭该请求的响应流。

> 参考：MCP 官方文档 `Docs → Transports`（modelcontextprotocol.io）及各版本 specification 的 `basic/transports` 章节。

---

## 附：与视频原话的对应关系

| 视频里的说法 | 本文对应 |
|---|---|
| "MCP server 两种沟通方式：stdio 和 sse，stdio 用得最多" | 第一、二节（本地 stdio / 远程 HTTP+SSE） |
| "为什么选择 stdio？因为简单，主要传 JSON" | 第一节"为什么选 stdio" |
| "为什么不用 HTTP？要用 SSE——为了服务端推送通知工具列表更新" | 第二节"为什么当初引入 SSE" |
| "现在更新成 streamable HTTP，SSE 只支持文本、跨平台差、性能问题" | 第三节 |
| "三条远程数据线用 HTTP+SSE，一条本地线用 stdio" | 第〇节架构图 |
| "有些 agent 框架直接支持 HTTP，因为 client 随时销毁、不需通知" | 第三节末"有些框架直接支持普通 HTTP" |
