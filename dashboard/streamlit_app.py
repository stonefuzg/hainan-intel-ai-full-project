
import os
import sys

# Ensure the project root is on sys.path so imports like `database.models` resolve.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st

from database.models import Enterprise, Policy, Project
from database.postgres import get_session


st.title("Hainan Business Intelligence Dashboard")

session = get_session()

enterprise_count = session.query(Enterprise).count()
policy_count = session.query(Policy).count()
project_count = session.query(Project).count()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("企业数量", enterprise_count)
with col2:
    st.metric("政策数量", policy_count)
with col3:
    st.metric("项目数量", project_count)

st.subheader("企业详情")
enterprises = session.query(Enterprise).all()
for e in enterprises:
    with st.expander(f"{e.name} - {e.industry}"):
        st.write(f"**注册号**: {e.registration_number}")
        st.write(f"**资本**: {e.capital}万元")
        st.write(f"**法定代表人**: {e.legal_representative}")
        st.write(f"**注册日期**: {e.registration_date}")
        st.write(f"**地区**: {e.region}")
        st.write(f"**企业形式**: {e.legal_form}")
        st.write(f"**经营范围**: {e.business_scope}")
        st.write(f"**状态**: {e.status}")
        st.write(f"**电话**: {e.phone}")
        st.write(f"**地址**: {e.address}")
        if e.website:
            st.write(f"**网站**: {e.website}")
        st.write(f"**员工数**: {e.employees}")
        st.write(f"**年营收**: {e.annual_revenue}万元")

st.subheader("政策详情")
policies = session.query(Policy).all()
for p in policies:
    with st.expander(f"{p.title} - {p.industry}"):
        st.write(f"**政策类型**: {p.policy_type}")
        st.write(f"**发布部门**: {p.issuing_department}")
        st.write(f"**发布日期**: {p.issue_date}")
        st.write(f"**生效日期**: {p.effective_date}")
        st.write(f"**内容**: {p.content}")
        st.write(f"**目标群体**: {p.target_groups}")
        st.write(f"**优惠措施**: {p.benefits}")
        st.write(f"**申请流程**: {p.application_process}")
        st.write(f"**联系方式**: {p.contact_info}")
        st.write(f"**文档链接**: {p.document_url}")
        st.write(f"**状态**: {p.status}")

st.subheader("项目详情")
projects = session.query(Project).all()
for p in projects:
    with st.expander(f"{p.name} - {p.investment}万元"):
        st.write(f"**项目类型**: {p.project_type}")
        st.write(f"**地区**: {p.region}")
        st.write(f"**投资来源**: {p.investment_source}")
        st.write(f"**建设周期**: {p.construction_period}")
        st.write(f"**预计完成**: {p.expected_completion}")
        st.write(f"**土地面积**: {p.land_area}亩")
        st.write(f"**建筑面积**: {p.building_area}平方米")
        st.write(f"**目标产业**: {p.target_industries}")
        st.write(f"**预期企业数**: {p.expected_enterprises}")
        st.write(f"**基础设施**: {p.infrastructure}")
        st.write(f"**政策支持**: {p.policy_support}")
        st.write(f"**联系部门**: {p.contact_department}")
        st.write(f"**联系电话**: {p.contact_phone}")
        st.write(f"**项目网站**: {p.project_website}")
        st.write(f"**状态**: {p.status}")
