"""
清空数据库并重新获取过去7天的数据
"""

import sys
import os
from datetime import datetime, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database.postgres import get_session, get_engine
from database.models import Enterprise, Policy, Project, DailyReport, init_db, Base
from data_source_manager import get_manager

print("=" * 100)
print("数据库重置与数据重新导入（2026-03-17）")
print("=" * 100)

# ============================================================================
# 步骤1：清空数据库
# ============================================================================
print("\n【步骤1】清空数据库...")
print("-" * 100)

engine = get_engine()
session = get_session(engine)

try:
    # 删除所有表中的数据
    session.query(DailyReport).delete()
    session.query(Project).delete()
    session.query(Policy).delete()
    session.query(Enterprise).delete()
    session.commit()
    print("✅ 已删除 DailyReport 表中的全部数据")
    print("✅ 已删除 Project 表中的全部数据")
    print("✅ 已删除 Policy 表中的全部数据")
    print("✅ 已删除 Enterprise 表中的全部数据")
except Exception as e:
    print(f"❌ 删除数据失败: {e}")
    session.rollback()
    exit(1)

# ============================================================================
# 步骤2：验证数据库已清空
# ============================================================================
print("\n【步骤2】验证数据库已清空...")
print("-" * 100)

enterprise_count = session.query(Enterprise).count()
policy_count = session.query(Policy).count()
project_count = session.query(Project).count()
report_count = session.query(DailyReport).count()

print(f"Enterprise 表记录数：{enterprise_count}")
print(f"Policy 表记录数：{policy_count}")
print(f"Project 表记录数：{project_count}")
print(f"DailyReport 表记录数：{report_count}")

if enterprise_count == 0 and policy_count == 0 and project_count == 0:
    print("\n✅ 数据库已成功清空")
else:
    print("\n⚠️ 数据库清空可能不完整")

# ============================================================================
# 步骤3：获取新数据
# ============================================================================
print("\n【步骤3】获取新数据...")
print("-" * 100)

manager = get_manager()

print("正在获取企业数据...")
enterprises = manager.get_enterprises(verbose=True)
print(f"✅ 获取企业数据：{len(enterprises)} 条")

print("正在获取政策数据...")
policies = manager.get_policies(verbose=True)
print(f"✅ 获取政策数据：{len(policies)} 条")

print("正在获取项目数据...")
projects = manager.get_projects(verbose=True)
print(f"✅ 获取项目数据：{len(projects)} 条")

# ============================================================================
# 步骤4：保存数据到数据库
# ============================================================================
print("\n【步骤4】保存数据到数据库...")
print("-" * 100)

try:
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
        import json
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
        import json
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
    print(f"✅ 已保存 {len(enterprises)} 条企业数据")
    print(f"✅ 已保存 {len(policies)} 条政策数据")
    print(f"✅ 已保存 {len(projects)} 条项目数据")

except Exception as e:
    print(f"❌ 保存数据失败: {e}")
    session.rollback()
    exit(1)

# ============================================================================
# 步骤5：验证数据已保存
# ============================================================================
print("\n【步骤5】验证数据已保存...")
print("-" * 100)

enterprise_count = session.query(Enterprise).count()
policy_count = session.query(Policy).count()
project_count = session.query(Project).count()

print(f"Enterprise 表记录数：{enterprise_count}")
print(f"Policy 表记录数：{policy_count}")
print(f"Project 表记录数：{project_count}")

total = enterprise_count + policy_count + project_count
print(f"\n📊 总计：{total} 条数据")

# ============================================================================
# 步骤6：显示数据示例
# ============================================================================
print("\n【步骤6】数据样本展示...")
print("-" * 100)

if enterprises:
    print(f"\n企业数据示例：")
    for i, e in enumerate(enterprises[:1], 1):
        print(f"  {i}. {e['name']} ({e['industry']}) - {e.get('region')}")
        print(f"     注册资本：{e['capital']} 万元")
        print(f"     员工数：{e.get('employees')} 人")
        print(f"     年营收：{e.get('annual_revenue')} 万元")

if policies:
    print(f"\n政策数据示例：")
    for i, p in enumerate(policies[:1], 1):
        print(f"  {i}. {p['title']}")
        print(f"     发布部门：{p.get('issuing_department')}")
        print(f"     发布日期：{p.get('issue_date')}")

if projects:
    print(f"\n招商项目示例：")
    for i, p in enumerate(projects[:1], 1):
        print(f"  {i}. {p['name']}")
        print(f"     投资金额：{p['investment']} 万元")
        print(f"     项目状态：{p.get('status')}")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 100)
print("【操作完成】")
print("=" * 100)
print("\n✅ 数据库已清空并重新导入新数据")
print(f"✅ 导入时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"✅ 导入数据量：")
print(f"   • 企业：{enterprise_count} 家")
print(f"   • 政策：{policy_count} 条")
print(f"   • 项目：{project_count} 个")
print("\n💡 提示：请运行 'streamlit run dashboard/streamlit_app.py' 查看Dashboard")
print("=" * 100)
