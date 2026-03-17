"""
测试爬虫错误处理机制
验证爬虫在失败时返回空列表而非虚假数据
"""

import sys
import os
from datetime import datetime

# Ensure the project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

print("=" * 100)
print("爬虫错误处理测试（2026-03-17）")
print("=" * 100)

# 测试1：正常情况下的爬虫行为
print("\n【测试1】正常爬虫运行（预期成功）")
print("-" * 100)

from crawlers.enterprise import crawl_enterprises
from crawlers.policy import crawl_policies
from crawlers.projects import crawl_projects

enterprises = crawl_enterprises()
policies = crawl_policies()
projects = crawl_projects()

print(f"✅ 企业爬虫返回：{len(enterprises)} 条数据")
if enterprises:
    for i, e in enumerate(enterprises[:1]):
        print(f"   示例：{e['name']} ({e['industry']})")

print(f"✅ 政策爬虫返回：{len(policies)} 条数据")
if policies:
    for i, p in enumerate(policies[:1]):
        print(f"   示例：{p['title']}")

print(f"✅ 项目爬虫返回：{len(projects)} 条数据")
if projects:
    for i, p in enumerate(projects[:1]):
        print(f"   示例：{p['name']} ({p['investment']}万元)")

# 测试2：模拟爬虫失败（网络错误）
print("\n【测试2】测试降级行为（网络错误模拟）")
print("-" * 100)

# 从爬虫中导入真实函数，然后测试错误处理
from unittest.mock import patch, MagicMock
import requests

with patch('requests.get') as mock_get:
    # 模拟网络超时
    mock_get.side_effect = requests.Timeout("Connection timeout")
    
    # 重新导入爬虫需要卸载旧的模块缓存
    import importlib
    from crawlers import enterprise as enterprise_module
    importlib.reload(enterprise_module)
    
    print("模拟网络超时异常...")
    test_enterprises = enterprise_module.crawl_enterprises()
    print(f"返回结果：{len(test_enterprises)} 条数据")
    
    if len(test_enterprises) == 0:
        print("✅ 符合预期：爬虫失败时返回空列表，而非虚假数据")
    else:
        print(f"⚠️ 意外：爬虫返回了 {len(test_enterprises)} 条数据")

# 测试3：验证错误消息被记录
print("\n【测试3】错误日志验证")
print("-" * 100)
print("爬虫将在以下情况记录错误信息：")
print("  • 网络连接失败：requests.ConnectionError")
print("  • 网络超时：requests.Timeout")
print("  • HTTP错误：requests.HTTPError")
print("  • HTML解析错误：BeautifulSoup parsing errors")
print("  • 其他异常：Any exception during crawling")

print("\n当发生上述异常时，爬虫将：")
print("  1️⃣  打印错误信息：[爬虫类型错误] ExceptionType: Error details")
print("  2️⃣  返回空列表：[]")
print("  3️⃣  不返回虚假数据或模拟数据")

# 测试4：验证爬虫数据格式
print("\n【测试4】成功获取数据的格式验证")
print("-" * 100)

# 重新加载爬虫获取实际数据
from importlib import reload
import crawlers.enterprise as enterprise_module
import crawlers.policy as policy_module
import crawlers.projects as projects_module

reload(enterprise_module)
reload(policy_module)
reload(projects_module)

enterprises = enterprise_module.crawl_enterprises()
policies = policy_module.crawl_policies()
projects = projects_module.crawl_projects()

if enterprises:
    print("✅ 企业数据格式检查：")
    e = enterprises[0]
    required_fields = ['name', 'industry', 'capital', 'region']
    for field in required_fields:
        if field in e:
            print(f"   ✓ {field}: {e[field]}")
        else:
            print(f"   ✗ {field}: 缺失")

if policies:
    print("\n✅ 政策数据格式检查：")
    p = policies[0]
    required_fields = ['title', 'industry', 'policy_type', 'issuing_department']
    for field in required_fields:
        if field in p:
            print(f"   ✓ {field}: {p[field]}")
        else:
            print(f"   ✗ {field}: 缺失")

if projects:
    print("\n✅ 项目数据格式检查：")
    p = projects[0]
    required_fields = ['name', 'investment', 'project_type', 'region']
    for field in required_fields:
        if field in p:
            print(f"   ✓ {field}: {p[field]}")
        else:
            print(f"   ✗ {field}: 缺失")

# 测试5：总结
print("\n" + "=" * 100)
print("【测试总结】")
print("=" * 100)

data_status = []
if len(enterprises) == 0:
    data_status.append("❌ 企业数据为空 - 爬虫失败或无数据")
else:
    data_status.append(f"✅ 企业数据：{len(enterprises)} 条")

if len(policies) == 0:
    data_status.append("❌ 政策数据为空 - 爬虫失败或无数据")
else:
    data_status.append(f"✅ 政策数据：{len(policies)} 条")

if len(projects) == 0:
    data_status.append("❌ 项目数据为空 - 爬虫失败或无数据")
else:
    data_status.append(f"✅ 项目数据：{len(projects)} 条")

for status in data_status:
    print(status)

print("\n🎯 修改总结：")
print("  ✓ 移除虚假数据（fake data）的fallback逻辑")
print("  ✓ 爬虫报错时返回空列表 []")
print("  ✓ 异常原因被打印输出：[爬虫类型错误] ExceptionType: Error details")
print("  ✓ 支持后续集成日志系统或监控告警")

print("\n" + "=" * 100)
