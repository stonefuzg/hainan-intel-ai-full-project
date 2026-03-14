
from crawlers.enterprise import crawl_enterprises
from crawlers.policy import crawl_policies
from crawlers.projects import crawl_projects

from agents.data_agent import DataAgent
from agents.analysis_agent import AnalysisAgent
from agents.content_agent import ContentAgent


def run_daily_pipeline():

    enterprises = crawl_enterprises()
    policies = crawl_policies()
    projects = crawl_projects()

    data_agent = DataAgent()
    analysis_agent = AnalysisAgent()
    content_agent = ContentAgent()

    summary = data_agent.summarize(enterprises, policies, projects)
    analysis = analysis_agent.industry_analysis(enterprises)

    scripts = content_agent.generate_scripts(summary, analysis)

    print("=== 今日商业情报 ===")

    for s in scripts:
        print("-", s)
