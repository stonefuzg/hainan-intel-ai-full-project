
from datetime import datetime

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


def run_daily_pipeline():
    """Run the full daily workflow and persist results to the database."""

    load_dotenv()

    engine = get_engine()
    # Drop and recreate tables to handle schema changes
    Base.metadata.drop_all(engine)
    init_db(engine)
    session = get_session(engine)

    enterprises = crawl_enterprises()
    policies = crawl_policies()
    projects = crawl_projects()

    session.add_all(
        [
            Enterprise(
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
            for e in enterprises
        ]
    )
    session.add_all(
        [
            Policy(
                title=p["title"],
                industry=p["industry"],
                policy_type=p.get("policy_type"),
                issuing_department=p.get("issuing_department"),
                issue_date=p.get("issue_date"),
                effective_date=p.get("effective_date"),
                content=p.get("content"),
                target_groups=str(p.get("target_groups", [])),
                benefits=str(p.get("benefits", [])),
                application_process=p.get("application_process"),
                contact_info=p.get("contact_info"),
                document_url=p.get("document_url"),
                status=p.get("status"),
            )
            for p in policies
        ]
    )
    session.add_all(
        [
            Project(
                name=p["name"],
                investment=p["investment"],
                project_type=p.get("project_type"),
                region=p.get("region"),
                investment_source=p.get("investment_source"),
                construction_period=p.get("construction_period"),
                expected_completion=p.get("expected_completion"),
                land_area=p.get("land_area"),
                building_area=p.get("building_area"),
                target_industries=str(p.get("target_industries", [])),
                expected_enterprises=p.get("expected_enterprises"),
                infrastructure=str(p.get("infrastructure", [])),
                policy_support=str(p.get("policy_support", [])),
                contact_department=p.get("contact_department"),
                contact_phone=p.get("contact_phone"),
                project_website=p.get("project_website"),
                status=p.get("status"),
            )
            for p in projects
        ]
    )
    session.commit()

    data_agent = DataAgent()
    analysis_agent = AnalysisAgent()
    content_agent = ContentAgent()

    summary = data_agent.summarize(enterprises, policies, projects)
    analysis = analysis_agent.industry_analysis(enterprises)

    scripts = content_agent.generate_scripts(summary, analysis)

    # Persist daily report summary
    report_date = datetime.now().strftime("%Y-%m-%d")
    previous_report = (
        session.query(DailyReport)
        .order_by(DailyReport.created_at.desc())
        .first()
    )

    new_enterprises = summary["enterprise_count"] - (previous_report.enterprise_count if previous_report else 0)
    new_policies = summary["policy_count"] - (previous_report.policy_count if previous_report else 0)
    new_projects = summary["project_count"] - (previous_report.project_count if previous_report else 0)

    report = DailyReport(
        report_date=report_date,
        enterprise_count=summary["enterprise_count"],
        policy_count=summary["policy_count"],
        project_count=summary["project_count"],
        top_industry=analysis.get("top_industry"),
        top_industry_count=analysis.get("count"),
        new_enterprises=new_enterprises,
        new_policies=new_policies,
        new_projects=new_projects,
    )

    session.add(report)
    session.commit()

    text_report = [
        f"=== 今日商业情报 ({report_date}) ===",
        f"新增企业：{new_enterprises}（总共 {summary['enterprise_count']} 家）",
        f"新增政策：{new_policies}（总共 {summary['policy_count']} 条）",
        f"新增项目：{new_projects}（总共 {summary['project_count']} 个）",
        f"行业焦点：{analysis.get('top_industry', '未知')}（{analysis.get('count')} 家）",
        "",
        "-- 生成脚本：",
    ]

    for s in scripts:
        text_report.append(f"- {s}")

    report_body = "\n".join(text_report)
    print(report_body)

    # Send email report if configured
    send_report(f"海南商业情报日报 - {report_date}", report_body)


if __name__ == "__main__":
    run_daily_pipeline()
