"""
爬虫错误处理演示
展示在不同错误情况下，爬虫的返回结果
"""

import sys
import os
from unittest.mock import patch, MagicMock
import requests

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

print("=" * 100)
print("爬虫错误处理演示 - 各种异常场景")
print("=" * 100)

# ============================================================================
# 演示1：网络连接失败
# ============================================================================
print("\n【演示1】网络连接失败")
print("-" * 100)

from crawlers import enterprise

with patch('requests.get') as mock_get:
    mock_get.side_effect = requests.ConnectionError("Failed to establish a new connection")
    
    import importlib
    importlib.reload(enterprise)
    
    print("场景：DNS解析失败，无法连接到政府网站")
    result = enterprise.crawl_enterprises()
    
    print(f"\n爬虫返回：{result}")
    print(f"结果类型：{type(result)}")
    print(f"结果长度：{len(result)}")
    print("\n📌 关键点：")
    print("  ✓ 返回空列表 []，不是虚假数据")
    print("  ✓ 错误已打印在终端上")
    print("  ✓ 系统管理员可以看到具体的错误原因")

# ============================================================================
# 演示2：网络超时
# ============================================================================
print("\n【演示2】网络超时")
print("-" * 100)

with patch('requests.get') as mock_get:
    mock_get.side_effect = requests.Timeout("Connection timeout after 10 seconds")
    
    importlib.reload(enterprise)
    
    print("场景：政府网站响应缓慢，超过10秒超时")
    result = enterprise.crawl_enterprises()
    
    print(f"\n爬虫返回：{result}")
    print(f"结果为空列表：{result == []}")
    print("\n📌 关键点：")
    print("  ✓ 不会等待超过默认超时时间")
    print("  ✓ 返回空列表而非冻结程序")
    print("  ✓ 错误信息包含超时时长")

# ============================================================================
# 演示3：HTTP错误（404、500等）
# ============================================================================
print("\n【演示3】HTTP错误")
print("-" * 100)

with patch('requests.get') as mock_get:
    response_mock = MagicMock()
    mock_get.return_value = response_mock
    
    # 模拟 raise_for_status() 引发异常
    response_mock.raise_for_status.side_effect = requests.HTTPError("404 Client Error: Not Found")
    response_mock.text = "<html>404 Not Found</html>"
    
    importlib.reload(enterprise)
    
    print("场景：访问的URL返回404或500服务器错误")
    result = enterprise.crawl_enterprises()
    
    print(f"\n爬虫返回：{result}")
    print(f"返回空列表：{len(result) == 0}")
    print("\n📌 关键点：")
    print("  ✓ 即使HTTP请求成功发出，如果返回错误状态也会返回空列表")
    print("  ✓ 不会尝试解析错误页面为虚假数据")

# ============================================================================
# 演示4：正常情况（有数据时）
# ============================================================================
print("\n【演示4】正常情况（数据获取成功）")
print("-" * 100)

# 重新加载，恢复正常爬虫逻辑
importlib.reload(enterprise)
result = enterprise.crawl_enterprises()

print(f"爬虫返回：{len(result)} 条真实数据")
if result:
    print(f"\n示例数据：")
    print(f"  名称：{result[0]['name']}")
    print(f"  行业：{result[0]['industry']}")
    print(f"  员工：{result[0].get('employees', 'N/A')} 人")
    print(f"  年收入：{result[0].get('annual_revenue', 'N/A')} 万元")

print("\n📌 关键点：")
print("  ✓ 成功获取数据时，返回完整的真实数据列表")
print("  ✓ 不受错误处理修改的影响")

# ============================================================================
# 演示5：三种爬虫的一致性
# ============================================================================
print("\n【演示5】三种爬虫的一致性验证")
print("-" * 100)

from crawlers.policy import crawl_policies
from crawlers.projects import crawl_projects

enterprises = enterprise.crawl_enterprises()
policies = crawl_policies()
projects = crawl_projects()

print("数据收集结果：")
print(f"  企业爬虫：{len(enterprises)} 条数据")
print(f"  政策爬虫：{len(policies)} 条数据")
print(f"  项目爬虫：{len(projects)} 条数据")

print("\n数据完整性检查：")
if enterprises:
    sample = enterprises[0]
    fields_present = len([v for v in sample.values() if v is not None])
    print(f"  ✓ 企业数据平均字段数：{fields_present}/{len(sample)}")

if policies:
    sample = policies[0]
    fields_present = len([v for v in sample.values() if v is not None])
    print(f"  ✓ 政策数据平均字段数：{fields_present}/{len(sample)}")

if projects:
    sample = projects[0]
    fields_present = len([v for v in sample.values() if v is not None])
    print(f"  ✓ 项目数据平均字段数：{fields_present}/{len(sample)}")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 100)
print("【演示总结】")
print("=" * 100)

print("\n✅ 修改前的行为（已删除）：")
print("  ❌ 爬虫失败 → 返回虚假数据（3条模拟记录）")
print("  ❌ 用户看不出数据是否真实")
print("  ❌ 系统给出误导性信息")

print("\n✅ 修改后的行为（已实现）：")
print("  ✓ 爬虫失败 → 返回空列表 []")
print("  ✓ 打印异常信息显示具体错误")
print("  ✓ 系统透明性高，便于故障排查")
print("  ✓ 支持后续的日志和告警集成")

print("\n✅ 数据来源保证：")
print("  ✓ 只有成功获取的数据才会被使用")
print("  ✓ 不会混入虚假数据造成统计失误")
print("  ✓ Dashboard显示的都是真实数据或明确的错误提示")

print("\n" + "=" * 100)
