# 海南智能AI项目 - 数据收集详细方法

## 概述
本文档说明如何获取企业数据、政策数据和招商项目的**汇总（Summary）和增量（Incremental）数据**。

---

## 1. 企业数据爬虫 ✅

### 数据源
- **网站**：海南政府企业目录、企查查、天眼查等
- **更新频率**：每日更新

### 1.1 汇总数据获取方法

#### 方法 A：基础汇总查询
```python
# database/models.py 中的 Enterprise 表包含：
- name: 企业名称
- industry: 行业分类
- capital: 注册资本（万元）
- region: 地区
- status: 企业状态（存续/注销/迁出）
- employees: 员工数
- annual_revenue: 年收入（万元）
- created_at: 首次爬取时间

# SQL 查询示例
SELECT 
  COUNT(*) as 企业总数,
  COUNT(DISTINCT region) as 地区数,
  AVG(capital) as 平均注册资本,
  AVG(employees) as 平均员工数,
  SUM(annual_revenue) as 总年收入
FROM enterprises
WHERE status = '存续'
```

#### 方法 B：按行业分类统计
```python
SELECT 
  industry,
  COUNT(*) as 企业数,
  AVG(capital) as 平均资本,
  AVG(annual_revenue) as 平均收入
FROM enterprises
WHERE status = '存续'
GROUP BY industry
ORDER BY 企业数 DESC
```

#### 方法 C：按地区分布统计
```python
SELECT 
  region,
  COUNT(*) as 企业数,
  SUM(employees) as 总员工数,
  MAX(annual_revenue) as 最高年收入
FROM enterprises
WHERE status = '存续'
GROUP BY region
```

### 1.2 增量数据获取方法

#### 方法 A：基于时间戳的增量
```python
# 获取过去24小时新增的企业
SELECT * FROM enterprises
WHERE created_at >= NOW() - INTERVAL 24 HOUR
ORDER BY created_at DESC

# 实现函数示例
def get_incremental_enterprises(hours=24):
    from database.postgres import get_session, get_engine
    from datetime import datetime, timedelta
    from database.models import Enterprise
    
    session = get_session(get_engine())
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    new_enterprises = session.query(Enterprise).filter(
        Enterprise.created_at >= cutoff_time
    ).all()
    
    return [{
        'name': e.name,
        'industry': e.industry,
        'region': e.region,
        'capital': e.capital,
        'added_at': e.created_at
    } for e in new_enterprises]
```

#### 方法 B：基于哈希值的去重增量
```python
# 避免重复爬取相同企业
import hashlib

def generate_enterprise_hash(enterprise_data):
    """生成企业数据的唯一哈希值"""
    key = f"{enterprise_data['name']}_{enterprise_data['registration_number']}"
    return hashlib.md5(key.encode()).hexdigest()

def check_enterprise_exists(hash_value):
    """检查企业是否已存在"""
    session = get_session(get_engine())
    existing = session.query(Enterprise).filter(
        Enterprise.registration_number == hash_value
    ).first()
    return existing is not None
```

#### 方法 C：爬虫版本控制增量
```python
# 在 enterprises 表中添加列
- last_updated: 最后更新时间
- crawl_version: 爬虫版本号

# 只爬取需要更新的企业
def crawl_incremental_enterprises(version='v1'):
    from datetime import datetime, timedelta
    
    session = get_session(get_engine())
    # 获取7天未更新的企业
    stale_enterprises = session.query(Enterprise).filter(
        Enterprise.last_updated < datetime.utcnow() - timedelta(days=7)
    ).limit(100).all()
    
    for enterprise in stale_enterprises:
        # 更新企业数据
        updated_data = refresh_enterprise_data(enterprise.registration_number)
        enterprise.last_updated = datetime.utcnow()
        enterprise.crawl_version = version
        session.commit()
```

---

## 2. 政策数据 ✅

### 数据源
- **网站**：海南人民政府官网、各部委官网
- **更新频率**：每周更新

### 2.1 汇总数据获取方法

#### 方法 A：政策总体统计
```python
SELECT 
  COUNT(*) as 政策总数,
  COUNT(DISTINCT industry) as 涉及行业数,
  COUNT(DISTINCT policy_type) as 政策类型数,
  COUNT(DISTINCT issuing_department) as 发布部门数
FROM policies
WHERE status = '有效'
```

#### 方法 B：按行业和政策类型统计
```python
SELECT 
  industry,
  policy_type,
  COUNT(*) as 政策数量,
  GROUP_CONCAT(DISTINCT issuing_department) as 相关部门
FROM policies
WHERE status = '有效'
GROUP BY industry, policy_type
ORDER BY 政策数量 DESC
```

#### 方法 C：政策受益企业群体分析
```python
SELECT 
  title,
  policy_type,
  CAST(target_groups AS JSON) as 目标群体,
  issue_date,
  status
FROM policies
WHERE status = '有效'
ORDER BY issue_date DESC
```

#### 方法 D：政策支持方向分析
```python
# 解析 benefits/policy_support 字段
def analyze_policy_support():
    session = get_session(get_engine())
    policies = session.query(Policy).all()
    
    support_summary = {}
    for policy in policies:
        benefits = json.loads(policy.benefits)
        for benefit in benefits:
            support_summary[benefit] = support_summary.get(benefit, 0) + 1
    
    return sorted(support_summary.items(), 
                  key=lambda x: x[1], reverse=True)
```

### 2.2 增量数据获取方法

#### 方法 A：最近发布的政策
```python
# 获取最近7天发布的新政策
def get_new_policies(days=7):
    from datetime import datetime, timedelta
    from dateutil import parser
    
    session = get_session(get_engine())
    cutoff_date = (datetime.utcnow() - timedelta(days=days)).date()
    
    new_policies = session.query(Policy).filter(
        Policy.issue_date >= str(cutoff_date)
    ).order_by(Policy.issue_date.desc()).all()
    
    return new_policies
```

#### 方法 B：政策监听和完整性检查
```python
# 建立政策版本控制
def track_policy_updates():
    """
    在 policies 表中添加：
    - last_scan_date: 最后扫描时间
    - version: 政策版本号
    - is_updated: 是否有更新
    """
    session = get_session(get_engine())
    
    policies_to_update = session.query(Policy).filter(
        Policy.last_scan_date < datetime.utcnow() - timedelta(days=1)
    ).all()
    
    for policy in policies_to_update:
        # 重新爬取该政策的详细信息
        fresh_data = scrape_policy_details(policy.document_url)
        
        if fresh_data['content'] != policy.content:
            policy.is_updated = True
            policy.version += 1
            policy.content = fresh_data['content']
        
        policy.last_scan_date = datetime.utcnow()
        session.commit()
```

#### 方法 C：政策制定部门增量订阅
```python
# 按部门持续监听新政策
def watch_policy_by_department(department):
    """
    政策发布部门列表：
    - 海南省人民政府
    - 海南省商务厅
    - 海南省文化和旅游厅
    - 海口市发改委
    - 三亚市旅游局
    等等
    """
    session = get_session(get_engine())
    
    latest_policy = session.query(Policy).filter(
        Policy.issuing_department == department
    ).order_by(Policy.issue_date.desc()).first()
    
    if latest_policy:
        since_date = latest_policy.issue_date
        # 爬取该部门在 since_date 之后的所有新政策
        new_department_policies = scrape_department_policies(
            department, since_date
        )
        return new_department_policies
```

---

## 3. 招商项目

### 数据源
- **网站**：海南招商局、各市县发改委、项目库平台
- **更新频率**：每周更新

### 3.1 汇总数据获取方法

#### 方法 A：项目总体概览
```python
SELECT 
  COUNT(*) as 项目总数,
  SUM(investment) as 总投资额,
  AVG(investment) as 平均投资额,
  COUNT(DISTINCT region) as 涉及地区数,
  COUNT(DISTINCT project_type) as 项目类型数
FROM projects
WHERE status IN ('建设中', '规划中', '招标中')
```

#### 方法 B：按投资阶段分类
```python
SELECT 
  status,
  COUNT(*) as 项目数,
  SUM(investment) as 总投资额,
  AVG(land_area) as 平均占地面积,
  AVG(building_area) as 平均建筑面积
FROM projects
GROUP BY status
ORDER BY 总投资额 DESC
```

#### 方法 C：按地区和项目类型统计
```python
SELECT 
  region,
  project_type,
  COUNT(*) as 项目数,
  SUM(investment) as 投资总额,
  MIN(expected_completion) as 最早完成日期,
  MAX(expected_completion) as 最晚完成日期
FROM projects
GROUP BY region, project_type
ORDER BY 投资总额 DESC
```

#### 方法 D：产业链分析
```python
def analyze_value_chain():
    """分析项目涉及的产业链"""
    session = get_session(get_engine())
    projects = session.query(Project).all()
    
    industries = {}
    for project in projects:
        target_industries = json.loads(project.target_industries)
        for industry in target_industries:
            if industry not in industries:
                industries[industry] = {
                    'count': 0,
                    'investment': 0,
                    'projects': []
                }
            industries[industry]['count'] += 1
            industries[industry]['investment'] += project.investment
            industries[industry]['projects'].append(project.name)
    
    return industries
```

### 3.2 增量数据获取方法

#### 方法 A：新增项目时间序列
```python
# 获取最近14天发布的新项目
def get_new_projects(days=14):
    from datetime import datetime, timedelta
    
    session = get_session(get_engine())
    cutoff_time = datetime.utcnow() - timedelta(days=days)
    
    new_projects = session.query(Project).filter(
        Project.created_at >= cutoff_time
    ).order_by(Project.created_at.desc()).all()
    
    return [{
        'name': p.name,
        'investment': p.investment,
        'type': p.project_type,
        'region': p.region,
        'status': p.status,
        'added_at': p.created_at
    } for p in new_projects]
```

#### 方法 B：项目状态变更追踪
```python
# 在 projects 表中添加列
- status_history: JSON 字段记录历史状态变更
- status_updated_at: 状态最后更新时间

def track_project_status_changes():
    """追踪项目状态变化"""
    session = get_session(get_engine())
    
    # 获取过去7天状态变化的项目
    changed_projects = session.query(Project).filter(
        Project.status_updated_at >= datetime.utcnow() - timedelta(days=7)
    ).all()
    
    status_changes = []
    for project in changed_projects:
        history = json.loads(project.status_history or '[]')
        if len(history) > 1:
            latest = history[-1]
            previous = history[-2]
            status_changes.append({
                'project': project.name,
                'from': previous['status'],
                'to': latest['status'],
                'changed_at': latest['timestamp']
            })
    
    return status_changes
```

#### 方法 C：按项目地区增量监听
```python
def watch_projects_by_region(region, days=7):
    """监听特定地区的新项目"""
    session = get_session(get_engine())
    cutoff_time = datetime.utcnow() - timedelta(days=days)
    
    regional_projects = session.query(Project).filter(
        Project.region == region,
        Project.created_at >= cutoff_time
    ).all()
    
    return regional_projects
```

#### 方法 D：投资机会评估
```python
def identify_investment_opportunities():
    """识别高潜力投资项目"""
    session = get_session(get_engine())
    
    # 筛选条件：
    # 1. 投资额 > 1000万
    # 2. 状态为"规划中"或"招标中"
    # 3. 完成期限 > 1年
    
    opportunities = session.query(Project).filter(
        Project.investment > 1000,
        Project.status.in_(['规划中', '招标中']),
    ).order_by(Project.investment.desc()).all()
    
    return opportunities
```

#### 方法 E：项目进展更新获取
```python
def get_project_progress_updates():
    """
    需要建立项目进展监听机制：
    
    在 projects 表中添加：
    - progress_percentage: 项目进度百分比
    - last_progress_update: 最后进度更新时间
    - progress_notes: 进度备注
    - construction_period: 施工周期
    """
    session = get_session(get_engine())
    
    # 获取最近有进度更新的项目
    updated_projects = session.query(Project).filter(
        Project.last_progress_update >= 
            datetime.utcnow() - timedelta(days=7)
    ).order_by(Project.last_progress_update.desc()).all()
    
    return updated_projects
```

---

## 4. 实现汇总与增量的综合方案

### 4.1 数据库模式优化

```python
# 在 database/models.py 中添加通用追踪字段

class DataSourceMixin:
    """数据源追踪 Mixin"""
    created_at = Column(DateTime, default=datetime.datetime.utcnow)  # 首次入库
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, 
                       onupdate=datetime.datetime.utcnow)  # 最后更新
    data_hash = Column(String)  # 数据哈希，用于检测变更
    is_verified = Column(Boolean, default=False)  # 是否已验证
    source_url = Column(String)  # 数据源 URL
    crawl_version = Column(String, default='v1')  # 爬虫版本

# 在爬虫函数中使用
def crawl_with_deduplication(data_list, entity_type):
    """
    带去重的数据爬取
    entity_type: 'enterprise', 'policy', 'project'
    """
    from hashlib import md5
    import json
    
    session = get_session(get_engine())
    inserted = 0
    updated = 0
    
    for item in data_list:
        # 生成数据哈希
        item_json = json.dumps(item, sort_keys=True, ensure_ascii=False)
        data_hash = md5(item_json.encode()).hexdigest()
        
        # 查找已存在的记录
        existing = session.query(entity_class).filter(
            entity_class.data_hash == data_hash
        ).first()
        
        if existing:
            # 只更新时间戳
            existing.updated_at = datetime.datetime.utcnow()
            updated += 1
        else:
            # 插入新记录
            new_entity = create_entity(item, entity_type, data_hash)
            session.add(new_entity)
            inserted += 1
    
    session.commit()
    return {'inserted': inserted, 'updated': updated}
```

### 4.2 增量爬虫执行策略

```python
# pipelines/incremental_pipeline.py

def run_incremental_pipeline():
    """增量爬取管道"""
    from crawlers.enterprise import crawl_incremental_enterprises
    from crawlers.policy import crawl_incremental_policies
    from crawlers.projects import crawl_incremental_projects
    
    results = {
        'enterprises': crawl_incremental_enterprises(),
        'policies': crawl_incremental_policies(),
        'projects': crawl_incremental_projects()
    }
    
    # 生成增量报告
    report = generate_incremental_report(results)
    
    # 发送通知
    send_incremental_notification(report)
    
    return report

# scheduler/cron.py 更新

def start_scheduler():
    import schedule
    import time
    
    # 全量爬虫：每周一凌晨
    schedule.every().monday.at("02:00").do(run_full_pipeline)
    
    # 增量爬虫：每日早上9点
    schedule.every().day.at("09:00").do(run_incremental_pipeline)
    
    # 汇总报表生成：每日下午3点
    schedule.every().day.at("15:00").do(generate_summary_reports)
    
    while True:
        schedule.run_pending()
        time.sleep(30)
```

### 4.3 汇总报表生成

```python
# agents/report_agent.py

def generate_summary_reports():
    """生成汇总报表"""
    session = get_session(get_engine())
    
    report = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'enterprises': {
            'total': session.query(Enterprise).count(),
            'by_industry': get_enterprises_by_industry(),
            'by_region': get_enterprises_by_region(),
            'top_companies_by_revenue': get_top_enterprises(10)
        },
        'policies': {
            'total': session.query(Policy).count(),
            'by_type': get_policies_by_type(),
            'by_industry': get_policies_by_industry(),
            'recent': get_recent_policies(7)
        },
        'projects': {
            'total': session.query(Project).count(),
            'total_investment': session.query(
                func.sum(Project.investment)
            ).scalar(),
            'by_status': get_projects_by_status(),
            'by_region': get_projects_by_region(),
            'high_value': get_high_value_projects()
        }
    }
    
    # 存储报表
    save_report_to_db(report)
    
    return report
```

---

## 5. 最佳实践

| 场景 | 方法 | 频率 | 说明 |
|------|------|------|------|
| **汇总数据** | 离线 SQL 聚合 | 每日 | 使用 GROUP BY、COUNT、SUM 等聚合函数 |
| **增量数据** | 时间戳过滤 | 每日/每小时 | 基于 `created_at` 或 `updated_at` 字段 |
| **去重机制** | 哈希值比对 | 每次爬取 | 避免重复入库相同数据 |
| **数据验证** | 人工/算法 | 随机抽样 | 确保数据质量 |
| **变更追踪** | 版本控制 | 每次更新 | 记录数据变化历史 |
| **监听订阅** | 按部门/地区 | 实时 | 针对特定实体的增量监听 |

---

## 6. 查询示例

### 快速获取汇总数据

```python
def get_daily_summary():
    """获取最新的日汇总数据"""
    session = get_session(get_engine())
    
    today = datetime.now().strftime('%Y-%m-%d')
    daily_report = session.query(DailyReport).filter(
        DailyReport.report_date == today
    ).first()
    
    if daily_report:
        return daily_report
    else:
        # 实时生成
        return generate_summary_reports()
```

### 快速获取增量数据

```python
def get_daily_increments():
    """获取今日新增数据"""
    session = get_session(get_engine())
    today_start = datetime.combine(datetime.today(), 
                                   datetime.min.time())
    
    return {
        'new_enterprises': session.query(Enterprise).filter(
            Enterprise.created_at >= today_start
        ).count(),
        'new_policies': session.query(Policy).filter(
            Policy.created_at >= today_start
        ).count(),
        'new_projects': session.query(Project).filter(
            Project.created_at >= today_start
        ).count()
    }
```

---

## 总结

✅ **企业数据**：支持按行业/地区分析，增量可通过时间戳或哈希去重获取
✅ **政策数据**：支持按类型/部门追踪，增量可通过发布日期和版本控制获取
✅ **招商项目**：支持按投资额/阶段分析，增量可通过状态变更和地区监听获取
