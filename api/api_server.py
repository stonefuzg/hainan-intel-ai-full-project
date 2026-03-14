
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from database.models import Enterprise, Policy, Project
from database.postgres import get_session

app = FastAPI()


# Dependency to get DB session
def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Hainan Business Intelligence API", "endpoints": ["/health", "/summary", "/enterprises", "/policies", "/projects"]}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/enterprises")
def list_enterprises(db: Session = Depends(get_db)):
    enterprises = db.query(Enterprise).all()
    return [
        {
            "id": e.id,
            "name": e.name,
            "industry": e.industry,
            "capital": e.capital,
            "legal_representative": e.legal_representative,
            "registration_number": e.registration_number,
            "registration_date": e.registration_date,
            "region": e.region,
            "legal_form": e.legal_form,
            "business_scope": e.business_scope,
            "status": e.status,
            "phone": e.phone,
            "address": e.address,
            "website": e.website,
            "employees": e.employees,
            "annual_revenue": e.annual_revenue,
        }
        for e in enterprises
    ]


@app.get("/policies")
def list_policies(db: Session = Depends(get_db)):
    policies = db.query(Policy).all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "industry": p.industry,
            "policy_type": p.policy_type,
            "issuing_department": p.issuing_department,
            "issue_date": p.issue_date,
            "effective_date": p.effective_date,
            "content": p.content,
            "target_groups": p.target_groups,
            "benefits": p.benefits,
            "application_process": p.application_process,
            "contact_info": p.contact_info,
            "document_url": p.document_url,
            "status": p.status,
        }
        for p in policies
    ]


@app.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "investment": p.investment,
            "project_type": p.project_type,
            "region": p.region,
            "investment_source": p.investment_source,
            "construction_period": p.construction_period,
            "expected_completion": p.expected_completion,
            "land_area": p.land_area,
            "building_area": p.building_area,
            "target_industries": p.target_industries,
            "expected_enterprises": p.expected_enterprises,
            "infrastructure": p.infrastructure,
            "policy_support": p.policy_support,
            "contact_department": p.contact_department,
            "contact_phone": p.contact_phone,
            "project_website": p.project_website,
            "status": p.status,
        }
        for p in projects
    ]


@app.get("/summary")
def summary(db: Session = Depends(get_db)):
    return {
        "enterprises": db.query(Enterprise).count(),
        "policies": db.query(Policy).count(),
        "projects": db.query(Project).count(),
    }
