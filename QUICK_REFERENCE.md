# 数据収集快速参考指南

## 📌 3句话快速入门

```python
# 1. 获取所有汇总数据
from collectors import get_all_summaries
summary = get_all_summaries()

# 2. 获取过去24小时的增量数据  
from collectors import get_daily_increments
increments = get_daily_increments()

# 3. 获取特定类别的数据
from collectors import get_enterprise_summary, get_policy_summary, get_project_summary
enterprises = get_enterprise_summary()
```

---

## 🚀 快速API调用

### 汇总数据 (GET)
| 端点 | 说明 |
|------|------|
| `/api/data/summary/enterprises` | 企业汇总统计 |
| `/api/data/summary/policies` | 政策汇总统计 |
| `/api/data/summary/projects` | 项目汇总统计 |
| `/api/data/summary/all` | 全量汇总 |
| `/api/data/stats/overview` | 统计概览（汇总+增量合并） |

### 增量数据 (GET)
| 端点 | 参数 | 说明 |
|------|------|------|
| `/api/data/incremental/enterprises` | `?hours=24` | 企业增量（默认24小时） |
| `/api/data/incremental/policies` | `?days=7` | 政策增量（默认7天） |
| `/api/data/incremental/projects` | `?days=14` | 项目增量（默认14天） |
| `/api/data/incremental/daily` | - | 日增量报告 |
| `/api/data/incremental/weekly` | - | 周增量报告 |

### 导出数据 (GET)
| 端点 | 参数 | 说明 |
|------|------|------|
| `/api/export/csv` | `?type=all&days=7` | 导出CSV (enterprises/policies/projects/all) |

### 系统检查 (GET)
| 端点 | 说明 |
|------|------|
| `/api/data/health` | 健康检查 |

---

## 💻 Python 代码示例

### 方式1：使用便捷函数（最简单）

```python
from collectors import (
    get_all_summaries,
    get_daily_increments,
    get_weekly_increments,
    get_enterprise_summary,
    get_policy_summary,
    get_project_summary
)

# 获取所有汇总
all_data = get_all_summaries()
print(f"企业总数：{all_data['enterprises']['total_enterprises']}")

# 获取增量
daily_inc = get_daily_increments()
print(f"今日新增企业：{daily_inc['enterprises']['count']}")
```

### 方式2：使用 DataCollector 类（更强大）

```python
from collectors.summary_incremental import DataCollector

collector = DataCollector()

# 获取汇总
summary = collector.get_enterprise_summary()
print(json.dumps(summary, indent=2, ensure_ascii=False))

# 获取增量（自定义时间范围）
incremental = collector.get_enterprise_incremental(hours=48)  # 过去48小时
for enterprise in incremental['enterprises']:
    print(f"新企业：{enterprise['name']}")

# 获取自定义报告
daily_report = collector.get_daily_summary_report()
weekly_report = collector.get_weekly_incremental_report()
```

### 方式3：直接数据库查询（需要高级定制）

```python
from database.postgres import get_session, get_engine
from database.models import Enterprise
from sqlalchemy import func
from datetime import datetime, timedelta

session = get_session(get_engine())

# 按行业统计企业
industries = session.query(
    Enterprise.industry,
    func.count(Enterprise.id).label('count')
).group_by(Enterprise.industry).all()

# 获取过去7天新增
cutoff = datetime.utcnow() - timedelta(days=7)
new_enterprises = session.query(Enterprise).filter(
    Enterprise.created_at >= cutoff
).all()
```

---

## 📊 数据返回格式

### 汇总数据示例

```json
{
  "report_date": "2026-03-17",
  "total_enterprises": 150,
  "active_enterprises": 145,
  "total_capital_sum": 500000,
  "total_revenue_sum": 2500000,
  "industry_breakdown": {
    "航空运输": {"count": 5, "avg_annual_revenue": 1000000},
    "电子商务": {"count": 12, "avg_annual_revenue": 500000}
  },
  "region_breakdown": {
    "海口市": {"count": 50, "total_employees": 5000},
    "三亚市": {"count": 35, "total_employees": 3500}
  },
  "total_employees": 25000
}
```

### 增量数据示例

```json
{
  "time_range": "Last 24 hours",
  "cutoff_time": "2026-03-16T09:00:00",
  "count": 5,
  "enterprises": [
    {
      "name": "海南航空股份有限公司",
      "industry": "航空运输",
      "capital": 50000,
      "region": "海口市",
      "employees": 1000,
      "added_at": "2026-03-17T08:30:00"
    }
  ]
}
```

---

## 🔄 常见使用场景

### 场景1：每日报表生成

```python
from collectors import get_all_summaries, get_daily_increments
from datetime import datetime

# 获取汇总和增量
summary = get_all_summaries()
increments = get_daily_increments()

print(f"""
=== {datetime.now().strftime('%Y-%m-%d')} 商业情报日报 ===
企业：{summary['enterprises']['total_enterprises']} 家 (新增{increments['enterprises']['count']})
政策：{summary['policies']['total_valid_policies']} 条 (新增{increments['policies']['count']})
项目：{summary['projects']['total_projects']} 个 (新增{increments['projects']['count']})
""")
```

### 场景2：监控特定行业

```python
from collectors.summary_incremental import DataCollector

collector = DataCollector()
summary = collector.get_enterprise_summary()

# 找出企业数最多的3个行业
top_industries = sorted(
    summary['industry_breakdown'].items(),
    key=lambda x: x[1]['count'],
    reverse=True
)[:3]

for industry, stats in top_industries:
    print(f"{industry}: {stats['count']} 家企业")
```

### 场景3：投资机会识别

```python
from collectors.summary_incremental import DataCollector

collector = DataCollector()
projects = collector.get_project_incremental(days=7)

# 筛选高投资额项目
high_investment = [
    p for p in projects['projects'] 
    if p['investment'] > 5000  # 超过5000万元
]

print(f"过去7天新增高价值项目：{len(high_investment)}")
for project in high_investment:
    print(f"  - {project['name']}: {project['investment']}万元")
```

### 场景4：数据导出

```python
import csv
from collectors.summary_incremental import DataCollector

collector = DataCollector()
projects = collector.get_project_incremental(days=30)

# 导出到CSV
with open('projects_export.csv', 'w', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['项目名称', '投资额(万元)', '地区', '类型', '状态'])
    
    for p in projects['projects']:
        writer.writerow([
            p['name'],
            p['investment'],
            p['region'],
            p['type'],
            p['status']
        ])
```

---

## 📈 数据更新频率

| 数据类型 | 汇总更新 | 增量更新 | 推荐查询频率 |
|---------|---------|---------|------------|
| **企业数据** | 每日 | 每日 (24h) | 每天1-2次 |
| **政策数据** | 每周 | 每周 (7d) | 每周1-2次 |
| **招商项目** | 每周 | 每周 (14d) | 每周1次 |

---

## 🔧 Pipeline 选择

### 完整爬虫 (run_daily_pipeline)
```python
from pipelines.daily_pipeline import run_daily_pipeline
run_daily_pipeline()
# ⚠️ 警告：每次运行会删除并重新创建所有表
# 适合：初始化、数据积累验证
```

### 增量爬虫 (run_incremental_pipeline) ✅ 推荐
```python
from pipelines.incremental_pipeline import run_incremental_pipeline
result = run_incremental_pipeline()
# ✅ 优点：保留旧数据，只添加新数据，支持去重
# 适合：生产环境日常运行
```

---

## 🛠️ 集成到您自己的项目

### 步骤1：导入模块
```python
from collectors import DataCollector, get_all_summaries
from pipelines.incremental_pipeline import run_incremental_pipeline
```

### 步骤2：配置scheduler
```python
import schedule
from pipelines.incremental_pipeline import run_incremental_pipeline

# 每日早上9点运行增量爬虫
schedule.every().day.at("09:00").do(run_incremental_pipeline)

# 每日下午3点生成报表
schedule.every().day.at("15:00").do(lambda: print(get_all_summaries()))
```

### 步骤3：集成到 API
```python
from flask import Flask
from api.data_endpoints import register_data_api

app = Flask(__name__)
register_data_api(app)
app.run()
# 现在可以访问 http://localhost:5000/api/data/summary/all
```

---

## ⚠️ 常见问题 (FAQ)

**Q1：如何修改增量查询的时间范围？**
```python
# 获取过去48小时的企业
collector = DataCollector()
data = collector.get_enterprise_incremental(hours=48)

# 获取过去30天的政策
data = collector.get_policy_incremental(days=30)
```

**Q2：为什么数据重复了？**
```python
# 使用增量 pipeline 而不是完整 pipeline
# 增量 pipeline 有去重逻辑
from pipelines.incremental_pipeline import run_incremental_pipeline
```

**Q3：如何实时获取数据而不是定时爬虫？**
```python
# 直接调用爬虫函数并保存
from crawlers.enterprise import crawl_enterprises
from database.postgres import get_session, get_engine
from database.models import Enterprise

enterprises = crawl_enterprises()
session = get_session(get_engine())
# ... 自定义去重和保存逻辑
```

**Q4：性能如何？**
```
- 汇总查询：< 100ms（针对百万级数据）
- 增量查询：< 50ms
- 完整报告：< 200ms
详见 test_examples.py 中的性能测试
```

**Q5：支持哪些导出格式？**
```
✅ JSON (API 原生)
✅ CSV (通过 /api/export/csv)
🔄 Excel (可通过 pandas 扩展)
🔄 数据库备份 (PostgreSQL native)
```

---

## 📚 完整示例脚本

运行完整演示：
```bash
python collectors/test_examples.py        # 运行所有示例
python collectors/test_examples.py 1      # 运行示例1
python collectors/test_examples.py perf   # 性能测试
```

---

## 🎯 总结

| 需求 | 推荐方式 | 代码 |
|------|---------|------|
| 快速获取汇总 | 便捷函数 | `get_all_summaries()` |
| 获取增量更新 | 便捷函数 | `get_daily_increments()` |
| 自定义查询 | DataCollector 类 | `DataCollector().get_enterprise_summary()` |
| 定时爬虫 | Pipeline | `run_incremental_pipeline()` |
| 对外提供API | Flask 蓝图 | `register_data_api(app)` |
| 高级查询 | 直接 SQL | `session.query(Enterprise)...` |

---

**版本：v1.0 | 最后更新：2026-03-17 | 作者：AI Assistant**
