# 小龙虾视频分析平台 V2

完全独立于现有系统的「数据驱动内容智能中台」对照版本。

## 核心定位

- 数据采集 → 多维资产 → 角色视图 → 内容生产 → 效果回流
- 与旧系统并行运行，互相验证，最终融合优点。

## 技术栈

- 后端：FastAPI + SQLAlchemy 2.0 + Pydantic V2 + Alembic + PostgreSQL 16 + Redis 7
- 前端：Next.js 16 + React 19 + TypeScript + Ant Design 6
- 任务队列：RQ（Redis Queue）
- 爬虫：复用 MediaCrawlerPro 子进程

## 目录结构

```
v2/
├── backend/          FastAPI 后端
├── frontend/         Next.js 前端
├── docs/             设计文档
└── docker-compose.yml
```

## 快速启动

```bash
# 1. 确保旧系统的 PostgreSQL + Redis 已启动
#    V2 与旧系统共用基础设施，database 为 xiaolongxia_v2，Redis db index 为 1

# 2. 初始化后端
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.main

# 3. 启动前端
cd ../frontend
npm install
npm run dev
```

## 端口规划

| 服务 | 端口 | 说明 |
|---|---|---|
| V2 后端 | 8001 | 与旧系统 8000 错开 |
| V2 前端 | 3001 | 与旧系统 3000 错开 |
| PostgreSQL | 5432 | 与旧系统共用，database 为 `xiaolongxia_v2` |
| Redis | 6379 | 与旧系统共用，db index 为 `1` |

## 数据库准备

```bash
psql -h localhost -U root -d postgres -c "CREATE DATABASE xiaolongxia_v2;"
```

## MVP 范围

- 平台：抖音 + 小红书
- 角色：老板/决策、内容总监/编导、文案/创作者
- 能力：采集 → 评论语义分析 → 爆款因子分析 → 多版本文案生成 → 分镜生成
