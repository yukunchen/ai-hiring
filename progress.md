# AI 招聘系统 - 开发进度

## 项目概述

AI 招聘系统用于帮助 HR 部门根据研发部门提供的岗位 JD，在招聘网站（猎聘、BOSS直聘、LinkedIn）上搜索候选人，下载简历，并发送邮件询问意向。

## 技术栈

- **后端**: Python + FastAPI
- **前端**: HTML/CSS/JS
- **数据库**: SQLite
- **AI**: OpenAI API
- **简历存储**: 本地文件系统

## MVP 功能清单

| 功能 | 状态 | 说明 |
|------|------|------|
| 岗位 JD 管理（增删改查） | ✅ 完成 | API + Web 界面 |
| 猎聘网站候选人搜索 | ✅ 完成 | 模拟数据（需配置 cookies） |
| BOSS直聘/LinkedIn 搜索 | ❌ 后续 | MVP 暂不包含 |
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
- [x] 候选人搜索 API
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
49 passed, 54 warnings
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
│       │   └── liepin.py
│       ├── resume.py
│       ├── ai_match.py
│       ├── email_generation.py
│       └── mailer.py
├── tests/                  # 测试用例
│   ├── conftest.py
│   ├── test_jobs.py
│   ├── test_candidates.py
│   ├── test_scraper_liepin.py
│   └── test_ai_and_mail.py
├── static/
│   └── index.html          # Web 管理后台
├── config.yaml            # 配置文件
├── requirements.txt       # 依赖
└── progress.md           # 开发进度
```

## 启动方式

```bash
cd /home/ubuntu/WS/aihiring
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000

## 配置说明

在 `config.yaml` 中配置以下内容：

```yaml
# OpenAI API（用于 AI 匹配和邮件生成）
openai:
  api_key: "${OPENAI_API_KEY}"  # 设置环境变量

# SMTP（用于发送邮件）
smtp:
  host: "smtp.example.com"
  port: 587
  username: "hr@example.com"
  password: "${SMTP_PASSWORD}"  # 设置环境变量

# 猎聘爬虫（可选，配置后使用真实数据）
scrapers:
  liepin:
    cookies: ""  # 登录后的 cookies
```

## 待完成

- [ ] BOSS直聘爬虫
- [ ] LinkedIn 爬虫
- [ ] 真实环境测试
- [ ] 邮件模板自定义
- [ ] 候选人面试安排功能

## 更新日志

### 2026-02-21
- MVP 版本完成
- 基础 CRUD 功能
- 猎聘爬虫（模拟数据）
- AI 匹配和邮件生成
- Web 管理后台
