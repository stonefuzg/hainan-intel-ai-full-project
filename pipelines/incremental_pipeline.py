"""
改进版本的 Daily Pipeline
- 支持增量爬虫（不删除已有数据）
- 支持数据去重
- 生成汇总和增量报告
"""

import os
import sys
import json
import hashlib
from datetime import datetime

# Ensure the project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv

from crawlers.enterprise import crawl_enterprises
from crawlers.policy import crawl_policies
from crawlers.projects import crawl_projects

from agents.data_agent import DataAgent
from agents.analysis_agent import AnalysisAgent
from agents.content_agent import ContentAgent
from notifications.emailer import send_report

from database.models import DailyReport, Enterprise, Policy, Project, init_db, Base
from database.postgres import get_engine, get_session
from collectors.summary_incremental import DataCollector


def generate_data_hash(data: dict) -> str:
    """为数据项生成唯一哈希值"""
    # 选择关键字段用于哈希
    if 'registration_number' in data:  # Enterprise
        key = f"{data.get('name', '')}_{data.get('registration_number', '')}"
    elif 'issue_date' in data:  # Policy
        key = f"{data.get('title', '')}_{data.get('issue_date', '')}"
    else:  # Project
        key = f"{data.get('name', '')}_{data.get('region', '')}"
    
    return hashlib.md5(key.encode()).hexdigest()


def enterprise_exists(session, data_hash: str, registration_number: str) -> bool:
    """检查企业是否已存在"""
    if registration_number:
        existing = session.query(Enterprise).filter(
            Enterprise.registration_number == registration_number
        ).first()
        return existing is not None
    return False


def policy_exists(session, title: str, issue_date: str) -> bool:
    """检查政策是否已存在"""
    existing = session.query(Policy).filter(
        Policy.title == title,
        Policy.issue_date == issue_date
    ).first()
    return existing is not None


def project_exists(session, name: str, region: str) -> bool:
    """检查项目是否已存在（按名称和地区）"""
    existing = session.query(Project).filter(
        Project.name == name,
        Project.region == region
    ).first()
    return existing is not None


def run_incremental_pipeline():
    """
    运行增量管道
    - 爬取新数据
    - 去除重复数据
    - 保留旧数据，仅添加新数据
    - 生成汇总和增量报告
    """
    load_dotenv()
    
    engine = get_engine()
    init_db(engine)  # 创建表但不删除现有数据
    session = get_session(engine)
    
    print("[Pipeline] 开始增量爬虫...")
    
    # 爬取新数据
    print("[Crawlers] 爬取企业数据...")
    enterprises = crawl_enterprises()
    
    print("[Crawlers] 爬取政策数据...")
    policies = crawl_policies()
    
    print("[Crawlers] 爬取招商项目...")
    projects = crawl_projects()
    
    # 统计增量情况
    stats = {
        'new_enterprises': 0,
        'existing_enterprises': 0,
        'new_policies': 0,
        'existing_policies': 0,
        'new_projects': 0,
        'existing_projects': 0,
    }
    
    # 处理企业数据 - 去重并插入新数据
    print("[Processing] 处理企业数据...")
    for e in enterprises:
        if not enterprise_exists(session, generate_data_hash(e), e.get("registration_number")):
            new_enterprise = Enterprise(
                name=e["name"],
                industry=e["industry"],
                capital=e["capital"],
                legal_representative=e.get("legal_representative"),
                registration_number=e.get("registration_number"),
                registration_date=e.get("registration_date"),
                region=e.get("region"),
                legal_form=e.get("legal_form"),
                business_scope=e.get("business_scope"),
                status=e.get("status"),
                phone=e.get("phone"),
                address=e.get("address"),
                website=e.get("website"),
                employees=e.get("employees"),
                annual_revenue=e.get("annual_revenue"),
            )
            session.add(new_enterprise)
            stats['new_enterprises'] += 1
        else:
            stats['existing_enterprises'] += 1
    
    # 处理政策数据 - 去重并插入新数据
    print("[Processing] 处理政策数据...")
    for p in policies:
        if not policy_exists(session, p.get("title"), p.get("issue_date")):
            new_policy = Policy(
                title=p["title"],
                industry=p["industry"],
                policy_type=p.get("policy_type"),
                issuing_department=p.get("issuing_department"),
                issue_date=p.get("issue_date"),
                effective_date=p.get("effective_date"),
                content=p.get("content"),
                target_groups=json.dumps(p.get("target_groups", [])),
                benefits=json.dumps(p.get("benefits", [])),
                application_process=p.get("application_process"),
                contact_info=p.get("contact_info"),
                document_url=p.get("document_url"),
                status=p.get("status"),
            )
            session.add(new_policy)
            stats['new_policies'] += 1
        else:
            stats['existing_policies'] += 1
    
    # 处理招商项目 - 去重并插入新数据
    print("[Processing] 处理招商项目...")
    for p in projects:
        if not project_exists(session, p.get("name"), p.get("region")):
            new_project = Project(
                name=p["name"],
                investment=p["investment"],
                project_type=p.get("project_type"),
                region=p.get("region"),
                investment_source=p.get("investment_source"),
                construction_period=p.get("construction_period"),
                expected_completion=p.get("expected_completion"),
                land_area=p.get("land_area"),
                building_area=p.get("building_area"),
                target_industries=json.dumps(p.get("target_industries", [])),
                expected_enterprises=p.get("expected_enterprises"),
                infrastructure=json.dumps(p.get("infrastructure", [])),
                policy_support=json.dumps(p.get("policy_support", [])),
                contact_department=p.get("contact_department"),
                contact_phone=p.get("contact_phone"),
                project_website=p.get("project_website"),
                status=p.get("status"),
            )
            session.add(new_project)
            stats['new_projects'] += 1
        else:
            stats['existing_projects'] += 1
    
    session.commit()
    
    # 生成汇总报告
    print("[Reports] 生成汇总报告...")
    collector = DataCollector()
    summary_report = collector.get_daily_summary_report()
    incremental_report = collector.get_daily_incremental_report()
    
    # 运行数据分析
    print("[Analysis] 运行数据分析...")
    data_agent = DataAgent()
    analysis_agent = AnalysisAgent()
    content_agent = ContentAgent()
    
    old_enterprises = session.query(Enterprise).count() - stats['new_enterprises']
    old_policies = session.query(Policy).count() - stats['new_policies']
    old_projects = session.query(Project).count() - stats['new_projects']
    
    summary = {
        'enterprise_count': session.query(Enterprise).count(),
        'policy_count': session.query(Policy).count(),
        'project_count': session.query(Project).count(),
    }
    
    analysis = analysis_agent.industry_analysis(enterprises) if enterprises else {}
    scripts = content_agent.generate_scripts(summary, analysis) if summary else []
    
    # 保存日报报告
    print("[Database] 保存日报...")
    report_date = datetime.now().strftime("%Y-%m-%d")
    
    report = DailyReport(
        report_date=report_date,
        enterprise_count=summary['enterprise_count'],
        policy_count=summary['policy_count'],
        project_count=summary['project_count'],
        top_industry=analysis.get('top_industry') if analysis else None,
        top_industry_count=analysis.get('count') if analysis else None,
        new_enterprises=stats['new_enterprises'],
        new_policies=stats['new_policies'],
        new_projects=stats['new_projects'],
    )
    
    session.add(report)
    session.commit()
    
    # 生成文本报告
    print("[Reports] 生成完整报告...")
    
    text_report = [
        "=" * 80,
        f"海南智能AI项目 - 每日增量报告",
        f"报告日期：{report_date}",
        "=" * 80,
        "",
        "【增量统计】",
        f"  新增企业：{stats['new_enterprises']}",
        f"  已存在企业：{stats['existing_enterprises']}",
        f"  总企业数：{summary['enterprise_count']}",
        "",
        f"  新增政策：{stats['new_policies']}",
        f"  已存在政策：{stats['existing_policies']}",
        f"  总政策数：{summary['policy_count']}",
        "",
        f"  新增项目：{stats['new_projects']}",
        f"  已存在项目：{stats['existing_projects']}",
        f"  总项目数：{summary['project_count']}",
        "",
        "【汇总数据亮点】",
    ]
    
    # 添加汇总亮点
    if summary_report.get('enterprises'):
        ent_summary = summary_report['enterprises']
        text_report.append(f"  • 企业总数：{ent_summary.get('total_enterprises', 0)}")
        text_report.append(f"  • 在存续企业：{ent_summary.get('active_enterprises', 0)}")
        text_report.append(f"  • 总员工数：{ent_summary.get('total_employees', 0)}")
    
    if summary_report.get('policies'):
        pol_summary = summary_report['policies']
        text_report.append(f"  • 有效政策数：{pol_summary.get('total_valid_policies', 0)}")
    
    if summary_report.get('projects'):
        proj_summary = summary_report['projects']
        text_report.append(f"  • 招商项目数：{proj_summary.get('total_projects', 0)}")
        text_report.append(f"  • 总投资规模：{proj_summary.get('total_investment', 0):.0f} 万元")
    
    text_report.extend([
        "",
        "【行业焦点】",
        f"  {analysis.get('top_industry', '未知')}（{analysis.get('count', 0)} 家企业）"
        "",
        "【推荐内容】",
    ])
    
    for i, script in enumerate(scripts, 1):
        text_report.append(f"  {i}. {script}")
    
    text_report.extend([
        "",
        "【详细数据】",
        "汇总报告数据：已保存",
        "增量报告数据：已保存",
        "=" * 80,
    ])
    
    report_body = "\n".join(text_report)
    print(report_body)
    
    # 发送邮件报告
    print("[Notifications] 发送邮件报告...")
    send_report(f"海南商业情报日报 - {report_date}", report_body)
    
    print("[Pipeline] ✅ 增量管道完成！")
    
    return {
        'status': 'success',
        'report_date': report_date,
        'statistics': stats,
        'summary': summary_report,
        'incremental': incremental_report
    }


if __name__ == "__main__":
    result = run_incremental_pipeline()
    print(json.dumps({
        'status': result['status'],
        'report_date': result['report_date'],
        'statistics': result['statistics'],
    }, indent=2, ensure_ascii=False))
