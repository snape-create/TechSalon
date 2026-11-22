# Docker 课程讲义 · 知识总结

> 来源：[酒井科协暑培 2025 · Docker 讲义](https://summer25.net9.org/backend/docker/note/)（Tempest，2025-08-26）
> 本文为网页内容的提炼总结，保留全部关键概念、命令与示例。

---

## 1. Docker 是什么 / 为什么用

Docker 是基于虚拟化技术、用于"打包"和"承载"应用程序运行环境的**轻量级**工具。官方文档定义：一个用于开发、交付、运行应用的开放平台，让应用与基础设施分离，从而快速交付软件。

它把应用放进**容器（Container）**中运行：容器直接跑在主机内核上、共享主机资源，同时与操作系统及其他容器隔离。

**解决的痛点**

- 依赖项冲突
- 程序修改本机系统文件、甚至危害系统
- 项目频繁部署
- 无法复现他人的运行环境（"您配吗"问题）

**三大优势**

| 优势 | 说明 |
|---|---|
| 隔离与安全 | 容器与外界隔离（正确配置下）不干扰环境 |
| 环境一致性 | 合作者拥有完全相同的运行环境 |
| 轻量化 | 无需独立操作系统，资源占用远小于虚拟机 |

> 相比虚拟机：VM 包含完整操作系统，体积庞大、启动慢；容器只是进程级隔离，秒级启动、MB 级体积。

---

## 2. 核心概念

### 镜像（Image）
- 相当于一个 **root 文件系统**，包含应用运行所需的程序、库、资源、配置，以及匿名卷、环境变量、用户等配置参数。
- **不包含动态数据**，构建后内容不变。
- **分层存储**：使用 UnionFS 将多个文件系统联合挂载到同一目录。镜像不是一个文件，而是一组文件系统的组合（虚拟概念）。每层构建后不再改变，后一层的所有改动（增、删、改）只发生在自己这一层。

### 容器（Container）
- 与镜像的关系类比**类与实例**：镜像静态（像类），容器是运行实例（像对象），在容器里改环境不会改变镜像。
- 本质是**进程**，运行于独立的**命名空间**（文件系统、网络、进程空间、用户 ID 空间等）。
- 同样分层：以镜像为基础层，之上叠加可读写的**容器存储层**。
- **容器是易失的**：容器消亡 → 存储层消亡 → 数据丢失。持久化需用**数据卷**或**绑定宿主目录**。

### 仓库（Registry / Repository / Tag）
- **Registry**（注册服务）存储分发镜像，下分多个**仓库（Repository）**，每个仓库用**标签（Tag）**区分版本。
- 命名规则：
  - `ubuntu` = `ubuntu:latest`（未指定标签默认 latest）
  - `ubuntu:24.04` —— 官方仓库的版本
  - `yyy/ubuntu:22.04` —— 用户 `yyy` 的 Docker Hub 仓库（省略用户名则指向官方仓库）

---

## 3. 常用命令

### `docker run`
```bash
docker run <options> <image> <command>
```
典型：`docker run alpine:latest echo "hello world!"`

**背后做了四件事：**
1. 本地找镜像，没有就去 Registry（默认 Docker Hub，"换源"换的就是它）拉取；
2. 用镜像创建并启动新容器；
3. 运行指定 command（未指定则跑镜像默认命令）；
4. 执行完**终止**容器（注意：不是删除！`docker ps -a` 仍可见）。

**常用选项**

| 选项 | 作用 |
|---|---|
| `-d` / `--detach` | 后台运行并显示容器 ID |
| `-e` / `--env K=V` | 设置环境变量 |
| `--rm` | 容器结束后自动删除 |
| `--name <name>` | 命名容器 |
| `-p` / `--publish 宿主:容器` | 端口映射 |
| `-it` | 交互模式 + 伪终端（可 `exit` 退出） |

常用玩法：`docker run --rm -it ubuntu`（临时模拟 Ubuntu 环境）

### 其他命令
```bash
docker build -f path/to/Dockerfile -t test:1.0 .   # 构建镜像（-f 指定 Dockerfile，-t 命名标签）
docker images                       # 列出镜像
docker ps [-a]                      # 列出运行中（含全部）容器
docker exec <options> <container> <command>       # 在运行中的容器执行命令
docker attach <container>           # 连接后台容器，CTRL+P CTRL+Q 断开
docker start / stop / rm <containers>             # 启动 / 停止 / 删除容器
docker rmi <images>                 # 删除镜像
docker cp <src> <container>:<dest>  # 宿主机与容器间复制文件
```

---

## 4. 用 Dockerfile 定制镜像

### 常用指令

| 指令 | 作用 |
|---|---|
| `FROM <image>` | 指定基础镜像，如 `FROM ubuntu:22.04` |
| `RUN <command>` | 执行命令；支持 shell 格式与 exec 格式 `RUN ["apt","install","vim"]` |
| `WORKDIR <path>` | 设定工作目录（不存在则自动创建）；影响**后续各层**，而 `RUN cd` 只影响当前层 |
| `COPY <src> <dest>` | 从**构建上下文**复制文件到镜像新层；支持 exec 格式 |
| `ENV K=V ...` | 设置环境变量（单个可写 `ENV K V`） |
| `EXPOSE <port>` | **声明**暴露端口（不会自动映射，运行时仍需 `-p`） |
| `CMD <command>` | 容器启动命令，可被 `docker run <image> <command>` 覆盖；推荐 exec 格式 `CMD ["./main"]` |

### 示例一：内置源码的 C++ 镜像
```dockerfile
FROM ubuntu
WORKDIR /usr/src/cpp
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt install -y build-essential
RUN echo "#include <iostream>" > main.cpp
RUN echo "int main() {" >> main.cpp
RUN echo "\tstd::cout << \"Hello world!\" << std::endl;" >> main.cpp
RUN echo "\treturn 0;" >> main.cpp
RUN echo "}" >> main.cpp
RUN g++ main.cpp -o main
CMD ["./main"]
```
```bash
docker build -t cpp:1.0 . && docker run --rm cpp:1.0
```
> `ENV DEBIAN_FRONTEND=noninteractive` 用于避免安装时弹出交互式时区选择导致构建卡住。

### 示例二：通用的 C++ 镜像（COPY 宿主机源码）
```dockerfile
FROM ubuntu
WORKDIR /usr/src/cpp
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y build-essential
COPY main.cpp .
RUN g++ main.cpp -o main
CMD ["./main"]
```
```bash
docker build -t cpp:2.0 . && docker run --rm cpp:2.0
```
> 宿主机上的 `main.cpp` 不在镜像中（隔离性），必须 `COPY` 进去。改源码后重新 build 即可，不必改 Dockerfile。

### 示例三：Python Web 应用的通用 Dockerfile
讲义以 Web 后端为例给出的典型结构（省略 Django 专属细节）：
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV DEPLOY=False
EXPOSE 80
CMD ["sh", "start.sh"]
```
```bash
docker build -t backend . && docker run -p 8000:80 backend
```
> 关键点：先 `COPY requirements.txt` 再装依赖，最后 `COPY . .` ——利用分层缓存加速构建。

---

## 5. 镜像构建机制与优化

**分层**：Dockerfile 的**每一行**指令都会新建一层，层层叠加（类似继承，但不完全一致）。层数过多会让镜像臃肿。

**合并层**：用 `\` 换行 + `&&` 把多条命令合成一条，只产生一层。
```dockerfile
RUN apt update \
    && apt install -y build-essential \
    && echo "#include <iostream>" > main.cpp \
    && echo "int main() {" >> main.cpp \
    && echo "\tstd::cout << \"Hello world!\" << std::endl;" >> main.cpp \
    && echo "\treturn 0;" >> main.cpp \
    && echo "}" >> main.cpp \
    && g++ main.cpp -o main
```

**构建上下文（那个 `.`）**
- `docker build` 末尾的路径是**上下文目录**，不是 Dockerfile 所在目录（Dockerfile 由 `-f` 指定）。
- 客户端把上下文目录下**所有内容打包上传**给 Docker Engine，引擎展开后用于构建。
- `COPY` 的**源路径相对于上下文（镜像外）**，**目标路径相对于工作目录（镜像内）**。
- 因此 `COPY ../package.json .`（父目录）和 `COPY /usr/xxx .`（绝对路径）都会失败——超出上下文范围。
- 用 `.dockerignore` 忽略无关文件，减小上传体积。

---

## 6. 多阶段构建

目的：只保留最终产物，不把源码、编译工具、依赖库带进最终镜像。每条 `FROM` 开启一个新阶段，`AS` 给阶段命名，`COPY --from=builder` 从指定阶段取文件（路径是**镜像内**的）。

```dockerfile
# build 阶段
FROM ubuntu AS builder
WORKDIR /usr/src/cpp
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y build-essential
COPY main.cpp .
RUN g++ main.cpp -o main

# runtime 阶段
FROM ubuntu AS runtime
WORKDIR /usr/src/cpp
COPY --from=builder /usr/src/cpp/main .
CMD ["./main"]
```

**用 scratch 进一步瘦身**：`scratch` 是完全空的镜像；因缺少 C++ 动态链接库，编译需加 `-static` 静态链接：
```dockerfile
FROM ubuntu AS builder
WORKDIR /usr/src/cpp
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y build-essential
COPY main.cpp .
RUN g++ main.cpp -o main -static

FROM scratch
COPY --from=builder /usr/src/cpp/main .
CMD ["./main"]
```
最终镜像可小至 **2.25 MB**。

---

## 7. 数据管理

容器是易失的，持久化有**数据卷**和**挂载主机目录**两种方式。

### 数据卷（volume）
绕过联合文件系统的特殊目录，可供一个或多个容器使用：
- 容器间可共享；
- 修改立即生效；
- 更新不影响镜像；
- 默认一直存在，即使容器被删除。

```bash
docker volume create <vol_name>     # 创建
docker volume ls                    # 列出
docker volume inspect <vol_name>    # 查看详情
docker volume rm <vol_name>         # 删除（不会随容器消亡而自动删除）

docker run --name web_backend \
    --mount source=database,target=/app/database \
    backend
docker inspect web_backend          # 在 Mounts 字段查看挂载信息
```

### 挂载主机目录（bind）
```bash
docker run --name web_backend \
    --mount type=bind,source=/usr/apps/web_database,target=/app/database \
    backend
```
- `type=bind` 表示挂载主机目录（数据卷是 `type=volume`，可省略）。
- 本地目录**必须用绝对路径**。
- 默认读写，加 `,readonly` 设为只读。
- 也可挂载单个文件（如 `.env` 配置）；一个容器可同时有多个挂载项。

---

## 8. Docker Compose

用 YAML 定义**容器集群**，一条命令编排多个服务。

```yaml
volumes:
  db:

services:
  backend:
    build: .
    ports:
      - "8000:80"
    volumes:
      - "/usr/apps/web_app/config.json:/app/config.json:ro"
    restart: unless-stopped
  database:
    image: mysql
    volumes:
      - "db:/var/lib/mysql"
    environment:
      MYSQL_ROOT_PASSWORD: "my_password"
      MYSQL_DATABASE: web_app
```
```bash
docker compose up            # 启动所有容器
docker compose down          # 停止所有容器
docker compose logs <service>  # 查看服务日志
```
> `restart: unless-stopped` 让容器持续重启（除非手动停止）直到成功，用于应对后端依赖数据库先就绪的问题。

---

## 9. 速查要点

1. **容器 ≠ 迷你 VM**：进程级隔离，共享内核，轻快小。
2. **镜像只读、分层；容器可写、易失**。
3. `docker run` 结束后容器是"终止"不是"删除"，要加 `--rm` 才自动删。
4. `EXPOSE` 只是声明，端口映射靠 `-p`。
5. Dockerfile 每行一层 → 合并命令、先 COPY 依赖清单以利用缓存。
6. build 末尾的 `.` 是**构建上下文**，不是 Dockerfile 路径。
7. 多阶段构建 + `scratch` + `-static` 大幅减小镜像。
8. 持久化用数据卷 / bind mount，Compose 编排多服务。

## 10. 参考资料
- [Docker 官方文档](https://docs.docker.com/)
- [Docker 从入门到实践](https://yeasy.gitbook.io/docker_practice)
- [2024 暑培讲义](https://summer24.net9.org/backend/docker/handout/) · [2023 暑培讲义](https://summer23.net9.org/backend/docker/)
