# Agent Evaluation Platform

独立的 Agent 评测平台，用于注册被测对象、导入评测资产、创建运行任务、分发执行、收集产物并生成报表、趋势和告警。

## 项目定位

`cockpit-agent-evaluation-framework` 的核心目标，不是直接生成测试数据，而是把“评测对象管理、评测资产编排、任务执行、结果回收、分析展示”串成一套独立平台。

这个项目主要承担以下职责：

- 注册被测 `target`，描述一个 Agent 系统如何被调用
- 注册 `environment`，描述本次运行所使用的环境配置
- 管理 `suite` 和 `case`，作为评测资产目录
- 导入来自 `cockpit-benchmark` 的 benchmark package
- 创建 `run`，并把 case 展开为可执行任务
- 让本地或远端 `runner` 领取任务并回传结果
- 聚合 `artifact`、报表、趋势、回归信号和工作台视图

如果把 `cockpit-benchmark` 看作“测试数据生产系统”，那么这个项目更像“评测编排与结果分析系统”。

## 项目结构

```text
apps/api/                         FastAPI 启动入口
apps/web/                         React + Vite 前端工作台
src/agent_eval_platform/api/      API 组装、依赖和路由
src/agent_eval_platform/services/ catalog、imports、runs、reports 等核心服务
src/agent_eval_platform/execution/任务领取、执行编排、artifact 持久化
src/agent_eval_platform/models/   数据模型
src/agent_eval_platform/schemas/  Pydantic Schema
runners/agent_runner/             示例 runner，负责领取和执行任务
workers/                          executor、analyzer、notifier 等后台进程入口
tests/                            API、执行链路、分析、端到端测试
docs/runbooks/                    本地开发 runbook
scripts/smoke_local.py            本地 smoke 检查脚本
docker-compose.yml                PostgreSQL 和 MinIO 本地依赖
```

建议优先从这些文件进入项目：

- `apps/api/main.py`：FastAPI 入口
- `src/agent_eval_platform/api/app.py`：应用装配和路由注册
- `src/agent_eval_platform/services/runs.py`：run 创建与任务展开逻辑
- `src/agent_eval_platform/services/catalog.py`：catalog 资产管理逻辑
- `src/agent_eval_platform/api/routes/imports.py`：benchmark package 导入入口
- `runners/agent_runner/main.py`：runner 领取任务并回传 completion 的示例实现

## 执行流程

系统当前最核心的评测链路如下：

`注册/导入评测资产 -> 创建 run -> 展开 execution task -> runner 领取任务 -> 执行并回传 completion -> 持久化 artifact -> 生成 dashboard / report / alerts`

从平台职责来看，这条链路通常分成 5 个阶段：

1. **准备 catalog 资产**
   创建或导入 `target`、`environment`、`suite` 和 `case`。如果你使用 `cockpit-benchmark` 生成的评测包，也是在这个阶段通过导入接口把 package 注册到平台里。

2. **创建 run**
   `RunService` 会校验 suite 是否存在，然后根据 `target` 的 adapter contract，把 suite 中的 case 展开为 `execution task`。

3. **runner 领取任务**
   runner 通过 `/api/v1/runs/leases` 轮询领取待执行任务。任务里会包含 `adapter_type` 和 `dispatch_payload`，例如 `http`、`cli`、`native_test`、`python_sdk` 等适配方式。

4. **执行与回传**
   runner 执行任务后，把结果通过 `/api/v1/runs/completions` 回传。平台会更新 task / attempt 状态，并在配置了 artifact storage 时保存原始结果。

5. **展示与分析**
   平台对外提供 dashboard、report、workbench、alerts 等接口，前端工作台也基于这些读模型展示运行中心、趋势、回归信号和告警事件。

如果你只想抓住最短主线，可以把它理解成：

1. 导入或创建资产
2. 创建 run
3. runner 执行
4. 查看结果

## 快速开始

### 1. 环境要求

- Python `3.11+`
- Node.js 与 `npm`
- Docker 与 Docker Compose
- 推荐安装 `uv`

### 2. 安装依赖

```bash
uv sync --extra dev
```

前端依赖单独安装：

```bash
npm --prefix apps/web install
```

### 3. 配置环境变量

如果你需要自定义数据库、artifact 存储或 MinIO 地址，可以先复制环境文件：

```bash
cp .env.example .env
```

默认配置下，平台会使用：

- PostgreSQL 作为主数据库
- 本地 `.artifacts` 目录作为默认 artifact 存储位置
- MinIO 作为本地对象存储依赖启动，便于环境对齐和后续扩展

### 4. 启动本地基础设施

```bash
docker compose up -d
```

当前 `docker-compose.yml` 会启动：

- PostgreSQL：`localhost:5432`
- MinIO API：`localhost:9000`
- MinIO Console：`localhost:9001`

### 5. 启动后端 API

```bash
uv run uvicorn apps.api.main:app --reload
```

启动后可访问：

- 健康检查：`http://127.0.0.1:8000/health`
- OpenAPI 文档：`http://127.0.0.1:8000/docs`

### 6. 启动前端工作台

```bash
npm --prefix apps/web run dev
```

Vite 开发服务器会把 `/api` 请求代理到本地后端。

### 7. 运行基础验证

后端测试：

```bash
uv run pytest -q
```

前端测试：

```bash
npm --prefix apps/web run test -- --run
```

前端构建检查：

```bash
npm --prefix apps/web run build
```

本地 smoke：

```bash
uv run python scripts/smoke_local.py
```

## 使用说明

### 推荐的最小使用路径

第一次本地跑通，建议按下面顺序操作：

1. 启动 PostgreSQL、MinIO、API 和前端
2. 先访问 `/health`，确认服务正常
3. 通过 catalog 或导入接口准备好 `target`、`environment`、`suite`、`case`
4. 创建一个 `run`
5. 启动 runner 或手动调用 runner 接口消费任务
6. 在 dashboard、report、workbench 和 alerts 中查看结果

### 导入 benchmark package

如果你的评测资产来自 `cockpit-benchmark`，推荐先导出一个 `benchmark-agent-export/v1` package，然后通过导入接口写入平台。

示例请求：

```bash
curl -X POST http://localhost:8000/api/v1/imports/benchmark-agent-package \
  -H 'Content-Type: application/json' \
  -d @import-request.json
```

通常流程是：

1. 从 `cockpit-benchmark` 导出一个 zip 或 JSON package
2. 调用 `/api/v1/imports/benchmark-agent-package`
3. 为请求指定有效的 `env_id`，例如 `local_mock`
4. 导入完成后，再基于新注册的 suite 创建 run

### 创建 run

run 的创建入口是：

- `POST /api/v1/runs`

它会完成这些事情：

- 校验请求中的 suite 是否存在
- 创建 run 主记录
- 为每个 suite 建立 run suite 实例
- 为每个 case 建立 run case 实例
- 结合 target profile 生成对应的 execution task

如果你需要基于历史运行再次执行，可以使用：

- `POST /api/v1/runs/{run_id}/rerun`

### runner 执行任务

runner 的典型交互是两步：

1. 通过 `GET /api/v1/runs/leases` 领取一个待执行任务
2. 执行后通过 `POST /api/v1/runs/completions` 回传结果

仓库自带了一个示例 runner：

- `runners/agent_runner/main.py`

它会根据租约中的 `adapter_type` 选择对应执行器，并在完成后把 `status` 和 `raw_result` 回传给平台。

### 查看结果

平台当前提供几类主要结果接口：

- `GET /api/v1/dashboard/targets/{target_id}`：target 总览
- `GET /api/v1/dashboard/runs/{run_id}`：run 中心视图
- `GET /api/v1/dashboard/cases/{case_id}`：case 级别视图
- `GET /api/v1/dashboard/trends/{scope_id}`：趋势面板
- `GET /api/v1/dashboard/regressions`：回归信号
- `GET /api/v1/reports/runs/{run_id}`：run 报表
- `GET /api/v1/alerts/events`：告警事件
- `GET /api/v1/workbench/home`：工作台首页读模型
- `GET /api/v1/workbench/runs`：工作台 run 列表

## 常见问题

**为什么 `/health` 正常，但前端页面拿不到数据？**

通常是前端开发服务器没有正常运行，或者 `/api` 代理没有指向本地后端。先确认 `npm --prefix apps/web run dev` 正在运行，再检查浏览器里请求是否走到了 `http://127.0.0.1:8000`。

**为什么创建 run 时报 suite 不存在？**

`RunService` 在创建 run 前会校验所有 `suite_id`。如果 suite 还没有导入、创建，或者 ID 写错，就会直接返回 404。

**为什么 run 创建成功了，但一直没有执行结果？**

最常见原因是没有 runner 来领取任务。平台本身会把 task 放到待执行状态，但不会替你自动消费。你需要启动本地 runner，或自己调用 `/api/v1/runs/leases` 和 `/api/v1/runs/completions`。

**为什么导入 benchmark package 后，看不到 suite 或 case？**

通常是导入请求里的 package 结构不符合要求，或者 `env_id` 不合法。先检查导入接口返回的 summary，再确认 package 来自 `cockpit-benchmark` 的正确导出格式。

**为什么 artifact 没有持久化？**

当前默认 runtime 使用的是本地 `.artifacts` 目录，而不是直接写入 MinIO。优先检查后端进程是否有目录写权限，以及 `local_artifact_dir` 配置是否正确；如果你后续自己接入对象存储，再额外检查 MinIO 或 S3 相关配置。

**为什么前端工作台是空的？**

dashboard、workbench 和 alerts 都是读模型接口，没有 run 数据时通常只会返回空状态或占位结构。至少创建并执行一次 run 后，页面内容才会变得完整。
