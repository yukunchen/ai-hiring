# AI 招聘系统

[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

AI 驱动的招聘系统，帮助 HR 部门自动化招聘流程。

## 功能特性

- **岗位管理** - 创建、编辑、删除岗位 JD
- **候选人搜索** - 从招聘网站搜索候选人（猎聘）
- **简历管理** - 自动下载和管理候选人简历
- **AI 匹配** - 使用 AI 分析候选人与岗位的匹配度
- **邮件自动化** - AI 生成并发送询问邮件
- **Web 管理后台** - 友好的图形界面

## 技术栈

- **后端**: Python 3.12+ / FastAPI
- **数据库**: SQLite
- **AI**: OpenAI API
- **前端**: HTML / CSS / JavaScript

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yukunchen/ai-hiring.git
cd ai-hiring
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置

复制 `config.yaml` 并配置必要的参数：

```yaml
# OpenAI API（用于 AI 匹配和邮件生成）
openai:
  api_key: "${OPENAI_API_KEY}"  # 设置环境变量 OPENAI_API_KEY

# SMTP（用于发送邮件）
smtp:
  host: "smtp.example.com"
  port: 587
  username: "your-email@example.com"
  password: "${SMTP_PASSWORD}"  # 设置环境变量
  from_name: "HR Team"

# 猎聘爬虫（可选）
scrapers:
  liepin:
    cookies: ""  # 登录后的 cookies
```

### 5. 启动服务

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. 访问

打开浏览器访问：http://localhost:8000

## 项目结构

```
aihiring/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py           # 配置管理
│   ├── database.py         # 数据库
│   ├── models/             # 数据模型
│   │   ├── job.py
│   │   └── candidate.py
│   ├── routers/            # API 路由
│   │   ├── jobs.py
│   │   ├── candidates.py
│   │   └── search.py
│   └── services/           # 业务服务
│       ├── scrapers/       # 爬虫
│       ├── resume.py       # 简历
│       ├── ai_match.py     # AI 匹配
│       ├── email_generation.py
│       └── mailer.py
├── tests/                  # 测试
├── static/                 # 前端
│   └── index.html
├── config.yaml            # 配置
└── requirements.txt
```

## API 文档

服务启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发

### 运行测试

```bash
pytest -v
```

### 环境变量

| 变量 | 说明 |
|------|------|
| OPENAI_API_KEY | OpenAI API Key |
| SMTP_PASSWORD | SMTP 邮箱密码 |

## 注意事项

1. 爬虫功能需要配置登录 cookies 才能获取真实数据
2. AI 功能需要配置 OpenAI API Key
3. 邮件发送需要配置 SMTP

## 许可证

MIT License
