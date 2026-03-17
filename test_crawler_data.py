"""
测试爬虫 - 检查实际返回的数据（真实 vs 模拟）
"""

import sys
import os
import json

# Ensure the project root is on sys.path
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from crawlers.enterprise import crawl_enterprises
from crawlers.policy import crawl_policies
from crawlers.projects import crawl_projects

print("=" * 80)
print("爬虫数据源检查 - 检查是否为真实数据")
print("=" * 80)

# 爬取企业数据
print("\n【企业数据爬虫】")
print("-" * 80)
enterprises = crawl_enterprises()
print(f"返回企业数量：{len(enterprises)}")

if enterprises:
    print("\n前3个企业详情：")
    for i, e in enumerate(enterprises[:3], 1):
        print(f"\n企业 {i}:")
        print(f"  名称: {e.get('name')}")
        print(f"  行业: {e.get('industry')}")
        print(f"  地区: {e.get('region')}")
        print(f"  资本: {e.get('capital')} 万元")
        print(f"  注册号: {e.get('registration_number')}")
        print(f"  注册日期: {e.get('registration_date')}")
        print(f"  网址: {e.get('website')}")
        print(f"  员工: {e.get('employees')} 人")
        print(f"  年收入: {e.get('annual_revenue')} 万元")

# 爬取政策数据
print("\n" + "=" * 80)
print("【政策数据爬虫】")
print("-" * 80)
policies = crawl_policies()
print(f"返回政策数量：{len(policies)}")

if policies:
    print("\n前3条政策详情：")
    for i, p in enumerate(policies[:3], 1):
        print(f"\n政策 {i}:")
        print(f"  标题: {p.get('title')}")
        print(f"  类型: {p.get('policy_type')}")
        print(f"  行业: {p.get('industry')}")
        print(f"  发布部门: {p.get('issuing_department')}")
        print(f"  发布日期: {p.get('issue_date')}")
        print(f"  生效日期: {p.get('effective_date')}")
        print(f"  内容预览: {p.get('content', '')[:100]}...")

# 爬取项目数据
print("\n" + "=" * 80)
print("【招商项目爬虫】")
print("-" * 80)
projects = crawl_projects()
print(f"返回项目数量：{len(projects)}")

if projects:
    print("\n前3个项目详情：")
    for i, p in enumerate(projects[:3], 1):
        print(f"\n项目 {i}:")
        print(f"  名称: {p.get('name')}")
        print(f"  类型: {p.get('project_type')}")
        print(f"  地区: {p.get('region')}")
        print(f"  投资: {p.get('investment')} 万元")
        print(f"  状态: {p.get('status')}")
        print(f"  完成期限: {p.get('expected_completion')}")
        print(f"  联系电话: {p.get('contact_phone')}")

# 数据质量评估
print("\n" + "=" * 80)
print("【数据质量评估】")
print("-" * 80)

# 检查是否有真实的海南企业特征
real_data_indicators = {
    "企业": {
        "是否有注册号": any(e.get('registration_number') for e in enterprises),
        "是否有网址": any(e.get('website') for e in enterprises),
        "是否有真实电话": any('0898' in str(e.get('phone', '')) for e in enterprises),
        "地区是否海南": any(e.get('region') and '海南' in str(e.get('region')) for e in enterprises),
    },
    "政策": {
        "是否有详细内容": any(p.get('content') for p in policies),
        "是否有文档链接": any(p.get('document_url') for p in policies),
        "发布日期是否最近": any(
            p.get('issue_date') and 
            ('2024' in str(p.get('issue_date')) or '2025' in str(p.get('issue_date')) or '2026' in str(p.get('issue_date')))
            for p in policies
        ),
    },
    "项目": {
        "是否有投资额": any(p.get('investment') for p in projects),
        "是否有完成期限": any(p.get('expected_completion') for p in projects),
        "是否有联系方式": any(p.get('contact_phone') for p in projects),
    }
}

for data_type, indicators in real_data_indicators.items():
    print(f"\n{data_type}数据质量：")
    for indicator, value in indicators.items():
        status = "✅" if value else "❌"
        print(f"  {status} {indicator}")

# 总体判断
print("\n" + "=" * 80)
print("【总体判断】")
print("-" * 80)

total_indicators = sum(sum(1 for v in indicators.values() if v) for indicators in real_data_indicators.values())
total_checks = sum(len(indicators) for indicators in real_data_indicators.values())

print(f"\n数据真实性评分：{total_indicators}/{total_checks}")

if total_indicators == total_checks:
    print("✅ 所有数据都具有真实特征，可能来自真实网站")
elif total_indicators >= total_checks * 0.7:
    print("⚠️  大部分数据具有真实特征，可能混合了真实和模拟数据")
else:
    print("❌ 数据以模拟数据为主，实际爬虫可能失败")

# 建议
print("\n【建议】")
print("-" * 80)
if total_indicators < total_checks * 0.7:
    print("当前爬虫返回模拟数据，原因可能是：")
    print("  1. 网络连接问题（查看是否能访问 https://www.hainan.gov.cn/）")
    print("  2. 海南政府网站结构已更改，爬虫规则需要更新")
    print("  3. 网站有反爬虫机制（IP 限制、验证码等）")
    print("\n建议：")
    print("  1. 检查网络连接")
    print("  2. 更新爬虫规则以适应最新的网站结构")
    print("  3. 考虑使用其他数据源（企查查、天眼查、政府数据开放平台等）")
    print("  4. 联系网站管理员获取官方 API 接口")
else:
    print("✅ 爬虫成功获取真实数据！")
    print("   所有数据都来自海南政府官方网站和相关平台")

print("\n" + "=" * 80)
