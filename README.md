
# Hainan Business Intelligence AI Agent

Automated system to collect public data about Hainan Free Trade Port and generate:
- commercial intelligence
- short‑video scripts
- daily reports
- datasets

## Modules

agents/          AI analysis agents
crawlers/        data collection
database/        database models
pipelines/       processing pipelines
video/           video generation
api/             API server
dashboard/       monitoring dashboard
scheduler/       automated jobs

## Quick Start

pip install -r requirements.txt
python pipelines/daily_pipeline.py

## Features

- ✅ 数据抓取：实时扫描最新企业 / 政策 / 招商项目
- ✅ 日报（邮件/数据库/API/可视化）
- ✅ API 接口：
  - `/summary`
  - `/enterprises`
  - `/policies`
  - `/projects`
  - `/reports`
- ✅ Dashboard：`streamlit run dashboard/streamlit_app.py`（含图表）

## 邮件提醒配置（可选）

在根目录创建 `.env` 并设置：

```dotenv
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_user
SMTP_PASSWORD=your_pass
EMAIL_FROM=from@example.com
EMAIL_TO=to@example.com
```

如果未配置邮件相关环境变量，系统将只在终端打印日报内容。
