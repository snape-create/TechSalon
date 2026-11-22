# MCP 进阶篇 · 视频总结

> 来源：`mcp进阶.docx`（听悟转录，视频文件 `29420487301-1-192.mp4`）
> **重要说明**：经核对，`mcp进阶.docx` 与 `mcp基础.docx` 的正文、图片、文件哈希**完全相同**——两者实际是同一段视频（即"基础篇"）的转录。视频结尾也明确说明"这是基础部分，进阶教程是后续预告"。因此本篇内容与《MCP 基础篇·视频总结》一致。若你手上另有真正的进阶篇视频，请重新导出后再让我整理。
> 整理说明：本文按知识点重组，已修正转录中的同音/识别错别字（如 NCP→MCP、ST6/STDO→stdio、clin/klein→Cline、to/two→tool、Jason→JSON 等），完整保留视频中的概念、操作步骤与案例，无删减。

---

## 一、这期视频要做什么

MCP 是近期 AI 领域的热点话题，但很多介绍视频只浮于表面，看完"似乎懂了又似乎没懂"，尤其对想深入使用、甚至自己开发 MCP 工具的开发者不够。

本视频定位为**从底层理解到动手实践的深度教程**，分两部分：

- **基础篇（本视频）**：打基础，弄懂 MCP 的核心概念、数据流转过程和基本用法。
- **进阶篇（下期）**：从零构建 MCP server，并像侦探一样截获、分析 MCP server 的输入输出，把协议细节挖个底朝天。

目标：看完后不仅"会用" MCP，更能"透彻理解"它。

---

## 二、MCP 是什么

- **全称**：Model Context Protocol，中文译作**模型上下文协议**。
- **发布方与时间**：Anthropic 公司，**2024 年 11 月 25 日**发布。
- 这个名字（以及 MCP 领域里很多词）有点"故弄玄虚"，不必纠结字面，先看它能做什么。

### MCP 能做什么

一句话：**MCP 是让大模型更好地使用各类工具的协议**。

- 让模型使用浏览器上网查询信息
- 让模型操作 Unity 编写游戏
- 让模型查询实时路况
- ……

大模型本身只会问答，**不会主动使用外部工具**；MCP 的出现等于让大模型拥有了使用各种外部工具的能力。

---

## 三、MCP Host：使用 MCP 的前提

要使用 MCP，还需要一个东西叫 **MCP host**——本质就是一个**支持 MCP 协议的软件**。

常见的 MCP host：

- Claude Desktop
- Cursor
- Cline
- Cherry Studio
- 等等

本视频以 **Cline** 为例讲解。

---

## 四、实操准备：Cline 的安装与配置

### 1. 安装 Cline

- Cline 是 **VS Code 的一个插件**。
- 到 VS Code 官网安装 VS Code → 打开插件搜索 `Cline` → 安装 → 出现图标，点击进入。

### 2. 配置模型

Cline 支持不同的 API 接入方和不同模型：

- 目前对 MCP 支持最好的是 **Claude 3.7**，但价格较贵。
- 预算有限可选 **DeepSeek V3（0324）**，效果不错且便宜很多。DeepSeek 官网提供 API，注册登录充值即可获取 API Key。
- 演示使用 **OpenRouter**：它覆盖几乎所有主流模型，有些还能免费使用。

### 3. 获取 OpenRouter API Key（演示）

1. 打开 OpenRouter 页面，右上角 **Sign In** 登录。
2. 鼠标移到右上角 → **Keys** → **Create Key**。
3. 填两项：
   - Key 名称：随便填（演示用 `default`）。
   - 该 Key 可用金额上限（单位美元）：可填可不填，为保险建议填一个数字（如 5）。
4. 点击 **Create** 创建。**务必把 Key 记下来，之后无法在 OpenRouter 页面找回。**
5. 只用免费模型的话到此结束；要用付费模型，点击 **Credits** 充值。

### 4. 在 Cline 中填配置

- 回到 Cline → 配置图标 → API Provider 选 **OpenRouter** → Key 填刚才记录的 → Model 选 `deepseek v3 0324`。
- 注意有两个 `deepseek v3 0324`：以 `free` 结尾的是免费版，但据测试不太稳定；有能力尽量选付费版（DeepSeek 也很便宜）。
- 配置的是 **Plan Mode**，还要在 **Act Mode** 里配置同样的信息。

### 5. 测试

点击 **Done**，进入聊天页面，先打个招呼确认能正常回复。然后问真正的问题：**"明天纽约的天气怎么样？"**

Cline 的建议是：创建一个天气的 MCP 服务器。由此引出 MCP server 的概念。

---

## 五、MCP Server 到底是什么

### 1. 名字具有误导性

- 英文原名 **MCP server**，听起来像传统网络协议里的 server（像访问 Google 首页那样要联网的远程服务器）。
- **实际上 MCP server 跟传统意义的 server 没太大关系，它就是一个程序**，只不过执行符合 MCP 协议。
- 大部分 MCP server 是本地通过 **Node 或 Python** 启动的；使用中可能联网，也可能纯本地使用。不管联不联网都可以叫 MCP server。
- 所以名字里带 "server" 是有误导性的。

### 2. 类比：MCP server 就像手机 App

- 不管是 MCP server 还是手机应用，本质都内置了一些功能模块来解决你的问题。
- 例：iPhone 时钟 App 内置 4 个功能模块——世界时钟、闹钟、钟表、计时器，解决 4 种场景诉求。
- Cline 想装的 OpenWeatherMap MCP server 也内置若干模块，这些模块在 MCP 领域的专业名词叫 **tool（工具）**。

### 3. Tool = 函数

- 一个 **tool 其实就是编程语言里的一个函数**。
- 通俗理解：函数是一个执行特定任务的"机器/工具箱"——放入一些材料（输入），机器内部按预先约定的规则处理，再给你一个成品（输出）。
- 例：处理天气的 MCP server 内部可能包含两个函数：
  - `get_forecast`：传入经纬度，返回未来几天的天气。
  - `get_alerts`：传入地区（美国州代码），返回未来几天的气象预警。
- 想查纽约明天天气，就让 Cline 安装这个天气 MCP server，用它其中的 `get_forecast` 即可拿到结果。（Cline 实际创建的 server 里具体 tool 可能不同，但一定有能解决"获取天气数据"这个问题的 tool。）

---

## 六、安装 MCP Server 的两种办法

Cline 想安装天气 MCP server 时：

### 办法一：让模型主导安装

1. 直接在聊天界面提供相关密钥，让模型自己创建并安装。
2. 或点击 MCP server 市场（类似手机应用市场），对每个 server 点 **Install**。

注意：这两种方式本质都是**让模型主导整个安装过程**。市场里每个 MCP server 都有对应的 GitHub 仓库，仓库有说明文档，模型通过读文档来运行程序、新增文件，完成安装。

### 办法二：手动配置（更通用、确定性更高）

为什么推荐手动：

- 很多人（包括作者）对安装的程序路径、版本有要求，不希望模型在电脑里"胡搞乱搞"，而且模型可能安装失败，过程不透明。
- 有些 MCP host **不支持自动安装，只能手动处理**。

操作步骤：

1. Cline → **Installed** → **Configure MCP Servers**，Cline 会打开一个 **JSON** 格式文件。
2. 想新增 MCP server，只需在里面填入对应的启动命令。作者仿照官方示例写了一个查询天气的 server（名为 `weather`），粘贴进去、格式化并保存，Cline 会自动识别并加载。

### JSON 配置项详解（以 weather 为例）

| 字段 | 含义 |
|---|---|
| 名称（如 `weather`） | MCP server 的名字 |
| `disabled` | 是否禁用。当前为禁用；去掉后恢复默认值（启动），绿色开关显示启动成功 |
| `timeout` | 连接该 MCP server 的超时时间，单位秒。超过 60 秒还没连上就放弃。一般不用太关注 |
| `command` | 用哪个程序来运行这个 MCP server。示例中是 `uv`（一个程序，后面会讲） |
| `args` | 对应的参数 |
| `transport type` | Cline 与该 MCP server 的沟通方式 |

### transport type（沟通方式）有两种

- **stdio**：MCP server 使用它的**标准输入和标准输出**与 Cline 沟通。目前大部分 MCP 都用这种类型（示例中的 weather 就是）。
- **sse**（Server-Sent Events）：用的比较少，视频先暂略，后半部分会演示。

> 一个 MCP server 背后只是一个程序，只不过运行符合 MCP 规范。

### 天气 server 内部

- 包含两个 tool：
  - `get_forecast`：参数 `latitude`、`longitude`（纬度、经度），调用天气 API 返回所传经纬度地区未来几天的天气。
  - `get_alerts`：参数是美国州代码，返回该州的气象预警信息。
- 这两个 tool 背后调用的 API 由**美国气象局**提供，目前只有美国数据（测试用）。真正需要的是 `get_forecast`。

---

## 七、实战：查"纽约明天的天气"

确认 weather MCP server 已开启，再问相同问题：

1. Cline 发现 `weather` server，并发现其中的 `get_forecast` tool 能解决问题。
2. 它帮你填入纽约的经纬度，请求确认是否执行该 tool → 点击 **Approve**。
3. 调用完成，拿到未来几天的天气信息，模型据此总结出符合问题的答案。
   - 演示中日期是 4 月 13 日，它把纽约 4 月 14 日的天气（白天、夜间及相关建议）都总结出来，效果不错。

---

## 八、内部发生了什么：完整数据流转过程

### 阶段一：注册（发生在开启 MCP server 的一瞬间）

用 JSON 配置好 MCP server 并保存后：

1. Cline 使用配置中的命令执行该程序；程序执行后等待 Cline 的指令。
2. **Cline**："你好，我是 Cline。"
   **MCP server**："你好，我是 weather。"
3. **Cline**："你有什么 tool 可供我使用？"
   **MCP server**："我有两个 tool：`get_forecast`（给我经纬度，可告诉你对应地区的天气预报）和 `get_alerts`（传美国州名，可告诉你该州实时预警信息）。"
4. Cline 记住 MCP server 的回答（后面可能用到）。注册结束。

### 阶段二：提问与调用

1. 用户问："纽约明天的天气怎么样？"
2. Cline 把问题传给模型。与往常不同，Cline 发给模型的除了用户问题，还有**注册好的 MCP server 以及每个 server 所含的 tool 列表**，并告诉模型"这些 tool 可能帮助你解决问题，需要调用哪个跟我说，我来帮你调"。
3. 模型判断：用户问题自己回答不了（知识截止到去年 12 月），但 weather server 里有 `get_forecast` 好像能回答。于是告诉 Cline：**调用 `get_forecast`，参数北纬 40 度、西经 74 度**。
4. Cline 拿到请求 → 与 weather server 沟通："你有 `get_forecast` 吧？用参数北纬 40 度、西经 74 度调用一下。"
5. weather server 用指定参数调用 `get_forecast` 函数，拿到结果传给 Cline。
6. Cline 把结果传回模型："你要的 tool 结果到了。"
7. 模型根据结果回答用户问题，答案发回 Cline → Cline 再发回用户。这就是最终看到的结果。

---

## 九、如何使用别人写的 MCP Server

### 1. 去哪里找

MCP server 市场很多，例如：

- `mcp.so`
- `mcpmarket.com`
- Smithery.ai（转录为 "smr AI"）

MCP server 大多用 **Python 或 Node** 编写，对应启动程序一般是 **uvx 或 npx**。

### 2. uvx 启动方式（Python 程序）

- **uvx 是 `uv tool run` 命令的缩写**，代表用 uv 运行一个 tool。
  - 注意：这里的 tool 是 **uv 领域的 tool**，跟前面 MCP 的 tool 不是一回事。
- **uv 是 Python 界的包管理软件**；uvx 可直接启动 Python 程序。
- 例：`uvx cowsay hello world`（转录 "UVX PCC hello world" / "pi cl c"）会让 cowsay 程序做一头牛的图片，并显示 "hello world"。图片显示出来说明没问题。

**安装 uv**：去 uv 的 GitHub 仓库找对应安装命令（macOS / Windows 各有其命令），复制到命令行执行。安装完可试着执行上面的 cowsay 命令验证。

### 3. Fetch 案例（uvx 启动）

fetch 用来抓取网页内容，用 uvx 启动：

1. 打开 `mcp.so` 搜索 `fetch` → 进入 → 点 **Content** → 选 uvx 的配置命令 → 复制。
2. 到 Cline 配置里加个逗号，粘贴、格式化。
3. 点击安装（Install），Cline 识别出新增的 fetch。
4. **注意红点**：红点代表尚未加载完成。前面绿色开关只代表"没被禁用"，"是否禁用"和"是否加载完成"是两回事。
5. 作者等了一分钟仍报 **request timed out（超时）**。原因：**uvx 首次执行某程序需先下载，下载耗时；默认超时一分钟**。
6. **解决办法**：先把对应命令复制到终端手动执行一次，等程序下载完。示例等下载完显示"34 个依赖全部安装完成"，然后程序停在那等待——这是正常的，因为大部分 MCP server 通过输入输出沟通，不会随便输出东西。
7. 退出程序一般用 **Ctrl + C**；若没反应，可按 **Ctrl + \**（会有系统提醒，关掉即可）。
8. 回到 VS Code 点 **Retry Connection**，这次加载快且成功。
9. 测试：新开会话，输入"请抓取下面这个网页的内容，并将其转换为 markdown 后，放到项目目录里面的 `guides.md` 文件中"并给出 URL。
   - Cline 找到 fetch MCP server → 提取参数 → 用内部的 `write_to_file` 工具做文件写入 → 拼接好调用参数 → 请求 Approve → 成功获取网页内容 → 转换成 markdown → 写入 `guides.md`。整个过程非常丝滑。

### 4. NPX 启动方式（Node 程序）

- **npx 与 uvx 类似**，也能自动下载并安装程序，只不过 uvx 装 Python 程序，npx 装 Node 程序。
- npx 是 Node 的一部分，直接安装 Node.js 即可（官网下载安装，跟装普通软件一样）。
- **HotNews 案例**（转录 "hot news"，用来拉取新闻）：
  1. 打开 MCP Market 类网站，搜索 `HotNews` → 点进该 MCP server（支持很多新闻源）。
  2. 复制配置中对应部分 → 到 Cline 点 Configure MCP Server → 粘贴 → Cline 加载该 server。
  3. 若加载过长导致超时，同样把命令放终端先下载完，回 Cline 再加载一次。
  4. 新建对话提问 → Cline 发现刚装的 server 并找到合适 tool，请求同意 → Approve → 执行完，模型总结得到最终结果。

### 5. 其他启动方式

除 uvx、npx 外，还可能有 **bunx**、直接用 **node** 启动等。仔细看 MCP server 对应的安装文档都能解决，视频不再赘述。

---

## 十、结尾与下期预告

基础部分到此结束。进阶教程将演示：

- 如何编写自己的 MCP server；
- 通过截取 MCP server 的输入输出，把运行原理"挖个底朝天"。

（作者也坦言：要看这期视频效果，效果不好可能就不做第二部分了。）

---

## 附：本篇核心概念速查

| 概念 | 一句话解释 |
|---|---|
| MCP | Model Context Protocol，模型上下文协议；让大模型使用外部工具的协议 |
| MCP host | 支持 MCP 协议的软件（Claude Desktop / Cursor / Cline / Cherry Studio 等） |
| MCP server | 本质是一个符合 MCP 协议的程序，多以 Node/Python 本地启动，"server"之名有误导性 |
| tool | MCP server 内置的功能模块，本质就是编程语言里的函数 |
| stdio | 用标准输入/输出沟通的传输方式，目前最常用 |
| sse | Server-Sent Events，另一种传输方式，较少用 |
| uvx / npx | 分别用于启动 Python / Node 编写的 MCP server，可自动下载安装依赖 |
