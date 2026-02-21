# AI 招聘系统 - 开发进度

## 项目概述

AI 招聘系统用于帮助 HR 部门根据研发部门提供的岗位 JD，在招聘网站（猎聘、BOSS直聘、LinkedIn）上搜索候选人，下载简历，并发送邮件询问意向。

## 技术栈

- **后端**: Python + FastAPI
- **前端**: HTML/CSS/JS
- **数据库**: SQLite
- **AI**: OpenAI API
- **简历存储**: 本地文件系统

## 功能清单

| 功能 | 状态 | 说明 |
|------|------|------|
| 岗位 JD 管理（增删改查） | ✅ 完成 | API + Web 界面 |
| 猎聘网站候选人搜索 | ✅ 完成 | 模拟数据（需配置 cookies） |
| BOSS直聘候选人搜索 | ✅ 完成 | 模拟数据（需配置 cookies） |
| LinkedIn 候选人搜索 | ✅ 完成 | 模拟数据（需配置 cookies） |
| 简历下载存储 | ✅ 完成 | 服务已实现 |
| AI 简历匹配 | ✅ 完成 | OpenAI API（需配置 key） |
| AI 邮件生成 | ✅ 完成 | OpenAI API（需配置 key） |
| 邮件发送 | ✅ 完成 | SMTP（需配置） |
| Web 管理后台 | ✅ 完成 | 基础界面 |

## 开发进度

### Phase 1: 基础架构 ✅
- [x] 项目初始化（目录结构、依赖）
- [x] 配置管理（config.yaml）
- [x] 数据库模型（SQLAlchemy）
- [x] 岗位 CRUD API
- [x] 候选人 CRUD API

### Phase 2: 爬虫模块 ✅
- [x] 猎聘爬虫框架
- [x] BOSS直聘爬虫
- [x] LinkedIn 爬虫
- [x] 爬虫工厂统一管理
- [x] 候选人搜索 API（支持多数据源）
- [x] 模拟数据支持（无 cookies 时使用）

### Phase 3: 简历管理 ✅
- [x] 简历下载服务
- [x] 简历存储管理
- [x] 文件命名规范

### Phase 4: AI 功能 ✅
- [x] AI 简历匹配服务
- [x] AI 邮件生成服务

### Phase 5: 邮件发送 ✅
- [x] SMTP 邮件发送服务
- [x] 邮件模板支持

### Phase 6: Web 后台 ✅
- [x] 岗位管理页面
- [x] 候选人列表页面
- [x] 候选人搜索页面

## 测试结果

```
59 passed, 54 warnings
```

## 项目结构

```
aihiring/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py           # 配置管理
│   ├── database.py         # 数据库初始化
│   ├── models/             # 数据模型
│   │   ├── job.py
│   │   └── candidate.py
│   ├── routers/            # API 路由
│   │   ├── jobs.py
│   │   ├── candidates.py
│   │   └── search.py
│   └── services/           # 业务服务
│       ├── scrapers/
│       │   ├── factory.py      # 爬虫工厂
│       │   ├── liepin.py       # 猎聘爬虫
│       │   ├── zhipin.py       # BOSS直聘爬虫
│       │   └── linkedin.py     # LinkedIn爬虫
│       ├── resume.py
│       ├── ai_match.py
│       ├── email_generation.py
│       └── mailer.py
├── tests/                  # 测试用例
├── static/
│   └── index.html
├── config.yaml
├── requirements.txt
└── progress.md
```

## API 文档

| 接口 | 说明 |
|------|------|
| GET /api/jobs | 获取岗位列表 |
| POST /api/jobs | 创建岗位 |
| GET /api/jobs/{id} | 获取岗位详情 |
| PATCH /api/jobs/{id} | 更新岗位 |
| DELETE /api/jobs/{id} | 删除岗位 |
| GET /api/candidates | 获取候选人列表 |
| POST /api/candidates | 创建候选人 |
| GET /api/candidates/{id} | 获取候选人详情 |
| PATCH /api/candidates/{id} | 更新候选人状态 |
| DELETE /api/candidates/{id} | 删除候选人 |
| GET /api/search | 搜索候选人 |
| GET /api/search/sources | 获取可用数据源 |

## 启动方式

```bash
cd ai-hiring
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000

## 配置说明

在 `config.yaml` 中配置：

```yaml
# OpenAI API
openai:
  api_key: "${OPENAI_API_KEY}"

# SMTP
smtp:
  host: "smtp.example.com"
  port: 587
  username: "hr@example.com"
  password: "${SMTP_PASSWORD}"

# 爬虫（配置 cookies 获取真实数据）
scrapers:
  liepin:
    enabled: true
    cookies: ""
  zhipin:
    enabled: true
    cookies: ""
  linkedin:
    enabled: true
    cookies: ""
```

## 待完成

- [ ] 真实环境测试
- [ ] 邮件模板自定义
- [ ] 候选人面试安排功能

## 更新日志

### 2026-02-21
- MVP 版本完成
- 基础 CRUD 功能
- 猎聘/BOSS直聘/LinkedIn 爬虫
- AI 匹配和邮件生成
- Web 管理后台

### 2026-02-21 (新增)
- 添加 BOSS直聘爬虫
- 添加 LinkedIn 爬虫
- 爬虫工厂统一管理
- 多数据源搜索支持
