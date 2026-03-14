
from dotenv import load_dotenv

from crawlers.enterprise import crawl_enterprises
from crawlers.policy import crawl_policies
from crawlers.projects import crawl_projects

from agents.data_agent import DataAgent
from agents.analysis_agent import AnalysisAgent
from agents.content_agent import ContentAgent

from database.models import Enterprise, Policy, Project, init_db, Base
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

    print("=== 今日商业情报 ===")

    for s in scripts:
        print("-", s)


if __name__ == "__main__":
    run_daily_pipeline()
