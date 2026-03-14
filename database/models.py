import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Enterprise(Base):
    __tablename__ = "enterprises"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    capital = Column(Integer, nullable=False)  # in 万元
    legal_representative = Column(String)
    registration_number = Column(String)
    registration_date = Column(String)
    region = Column(String)
    legal_form = Column(String)
    business_scope = Column(Text)
    status = Column(String)
    phone = Column(String)
    address = Column(String)
    website = Column(String)
    employees = Column(Integer)
    annual_revenue = Column(Integer)  # in 万元
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    policy_type = Column(String)
    issuing_department = Column(String)
    issue_date = Column(String)
    effective_date = Column(String)
    content = Column(Text)
    target_groups = Column(Text)  # JSON string
    benefits = Column(Text)  # JSON string
    application_process = Column(Text)
    contact_info = Column(String)
    document_url = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    investment = Column(Integer, nullable=False)  # in 万元
    project_type = Column(String)
    region = Column(String)
    investment_source = Column(String)
    construction_period = Column(String)
    expected_completion = Column(String)
    land_area = Column(Float)  # in 亩
    building_area = Column(Float)  # in 平方米
    target_industries = Column(Text)  # JSON string
    expected_enterprises = Column(Integer)
    infrastructure = Column(Text)  # JSON string
    policy_support = Column(Text)  # JSON string
    contact_department = Column(String)
    contact_phone = Column(String)
    project_website = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True)
    report_date = Column(String, nullable=False, unique=True)
    enterprise_count = Column(Integer, nullable=False)
    policy_count = Column(Integer, nullable=False)
    project_count = Column(Integer, nullable=False)
    top_industry = Column(String)
    top_industry_count = Column(Integer)
    new_enterprises = Column(Integer)
    new_policies = Column(Integer)
    new_projects = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


def init_db(engine):
    """Create database tables if they do not exist."""
    Base.metadata.create_all(engine)
