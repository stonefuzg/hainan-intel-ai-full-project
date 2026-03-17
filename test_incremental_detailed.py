"""
增量爬虫 - 详细数据查看
显示爬虫返回的完整数据，而不仅仅是统计信息
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Ensure the project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from crawlers.enterprise import crawl_enterprises
from crawlers.policy import crawl_policies
from crawlers.projects import crawl_projects
from database.postgres import get_session, get_engine
from database.models import Enterprise, Policy, Project, init_db, Base

print("=" * 100)
print("增量爬虫 - 详细数据查看（2026-03-17）")
print("=" * 100)

# 爬取数据
print("\n【步骤1】爬取数据源...")
enterprises = crawl_enterprises()
policies = crawl_policies()
projects = crawl_projects()

print(f"✅ 企业爬虫返回：{len(enterprises)} 条数据")
print(f"✅ 政策爬虫返回：{len(policies)} 条数据")
print(f"✅ 项目爬虫返回：{len(projects)} 条数据")

# 初始化数据库
print("\n【步骤2】初始化数据库并保存数据...")
engine = get_engine()
init_db(engine)
session = get_session(engine)

# 保存企业数据
for e in enterprises:
    enterprise = Enterprise(
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
    session.add(enterprise)

# 保存政策数据
for p in policies:
    policy = Policy(
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
    session.add(policy)

# 保存项目数据
for p in projects:
    project = Project(
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
    session.add(project)

session.commit()
print("✅ 数据已保存到数据库")

# 显示企业详细信息
print("\n" + "=" * 100)
print("【企业详细数据】")
print("=" * 100)
for i, e in enumerate(enterprises, 1):
    print(f"\n企业 #{i}")
    print("-" * 100)
    print(f"  名称：{e['name']}")
    print(f"  行业：{e['industry']}")
    print(f"  地区：{e['region']}")
    print(f"  注册资本：{e['capital']} 万元")
    print(f"  法定代表人：{e.get('legal_representative', 'N/A')}")
    print(f"  注册号：{e.get('registration_number', 'N/A')}")
    print(f"  注册日期：{e.get('registration_date', 'N/A')}")
    print(f"  企业形式：{e.get('legal_form', 'N/A')}")
    print(f"  经营范围：{e.get('business_scope', 'N/A')}")
    print(f"  企业状态：{e.get('status', 'N/A')}")
    print(f"  联系电话：{e.get('phone', 'N/A')}")
    print(f"  企业地址：{e.get('address', 'N/A')}")
    print(f"  企业网站：{e.get('website', 'N/A')}")
    print(f"  员工数：{e.get('employees', 'N/A')} 人")
    print(f"  年营收：{e.get('annual_revenue', 'N/A')} 万元")

# 显示政策详细信息
print("\n" + "=" * 100)
print("【政策详细数据】")
print("=" * 100)
for i, p in enumerate(policies, 1):
    print(f"\n政策 #{i}")
    print("-" * 100)
    print(f"  标题：{p['title']}")
    print(f"  类型：{p.get('policy_type', 'N/A')}")
    print(f"  行业：{p['industry']}")
    print(f"  发布部门：{p.get('issuing_department', 'N/A')}")
    print(f"  发布日期：{p.get('issue_date', 'N/A')}")
    print(f"  生效日期：{p.get('effective_date', 'N/A')}")
    print(f"  政策状态：{p.get('status', 'N/A')}")
    print(f"  内容（摘要）：{p.get('content', 'N/A')[:100]}...")
    print(f"  目标群体：{p.get('target_groups', [])}")
    print(f"  优惠措施：{p.get('benefits', [])}")
    print(f"  申请流程：{p.get('application_process', 'N/A')}")
    print(f"  联系方式：{p.get('contact_info', 'N/A')}")
    print(f"  文档链接：{p.get('document_url', 'N/A')}")

# 显示项目详细信息
print("\n" + "=" * 100)
print("【招商项目详细数据】")
print("=" * 100)
for i, p in enumerate(projects, 1):
    print(f"\n项目 #{i}")
    print("-" * 100)
    print(f"  项目名称：{p['name']}")
    print(f"  项目类型：{p.get('project_type', 'N/A')}")
    print(f"  投资地区：{p.get('region', 'N/A')}")
    print(f"  投资金额：{p['investment']} 万元")
    print(f"  投资来源：{p.get('investment_source', 'N/A')}")
    print(f"  建设周期：{p.get('construction_period', 'N/A')}")
    print(f"  预计完成：{p.get('expected_completion', 'N/A')}")
    print(f"  项目状态：{p.get('status', 'N/A')}")
    print(f"  土地面积：{p.get('land_area', 'N/A')} 亩")
    print(f"  建筑面积：{p.get('building_area', 'N/A')} 平方米")
    print(f"  目标产业：{p.get('target_industries', [])}")
    print(f"  预期企业数：{p.get('expected_enterprises', 'N/A')}")
    print(f"  基础设施：{p.get('infrastructure', [])}")
    print(f"  政策支持：{p.get('policy_support', [])}")
    print(f"  联系部门：{p.get('contact_department', 'N/A')}")
    print(f"  联系电话：{p.get('contact_phone', 'N/A')}")
    print(f"  项目网站：{p.get('project_website', 'N/A')}")

# 显示统计信息
print("\n" + "=" * 100)
print("【数据统计总结】")
print("=" * 100)
print(f"\n报告日期：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\n数据总量：")
print(f"  • 企业总数：{len(enterprises)} 家")
print(f"  • 政策总数：{len(policies)} 条")
print(f"  • 项目总数：{len(projects)} 个")

# 企业统计
if enterprises:
    industries = {}
    regions = {}
    for e in enterprises:
        ind = e.get('industry', '未分类')
        reg = e.get('region', '未分类')
        industries[ind] = industries.get(ind, 0) + 1
        regions[reg] = regions.get(reg, 0) + 1
    
    print(f"\n企业行业分布：")
    for ind, count in sorted(industries.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {ind}：{count} 家")
    
    print(f"\n企业地区分布：")
    for reg, count in sorted(regions.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {reg}：{count} 家")

# 政策统计
if policies:
    types = {}
    depts = {}
    for p in policies:
        ptype = p.get('policy_type', '未分类')
        dept = p.get('issuing_department', '未分类')
        types[ptype] = types.get(ptype, 0) + 1
        depts[dept] = depts.get(dept, 0) + 1
    
    print(f"\n政策类型分布：")
    for ptype, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {ptype}：{count} 条")
    
    print(f"\n政策发布部门：")
    for dept, count in sorted(depts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {dept}：{count} 条")

# 项目统计
if projects:
    types = {}
    regions = {}
    statuses = {}
    
    for p in projects:
        ptype = p.get('project_type', '未分类')
        reg = p.get('region', '未分类')
        status = p.get('status', '未分类')
        types[ptype] = types.get(ptype, 0) + 1
        regions[reg] = regions.get(reg, 0) + 1
        statuses[status] = statuses.get(status, 0) + 1
    
    total_investment = sum(p.get('investment', 0) for p in projects)
    
    print(f"\n项目类型分布：")
    for ptype, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {ptype}：{count} 个")
    
    print(f"\n项目地区分布：")
    for reg, count in sorted(regions.items(), key=lambda x: x[1], reverse=True):
        inv = sum(p.get('investment', 0) for p in projects if p.get('region') == reg)
        print(f"  • {reg}：{count} 个项目，投资 {inv} 万元")
    
    print(f"\n项目投资阶段：")
    for status, count in sorted(statuses.items(), key=lambda x: x[1], reverse=True):
        inv = sum(p.get('investment', 0) for p in projects if p.get('status') == status)
        print(f"  • {status}：{count} 个项目，投资 {inv} 万元")
    
    print(f"\n项目投资总额：{total_investment} 万元")

print("\n" + "=" * 100)
print("✅ 爬虫数据查看完毕")
print("=" * 100)
