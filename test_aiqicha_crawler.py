"""
测试爱企查爬虫
爬取：海南新成立企业
数据源：https://aiqicha.baidu.com/s?q=海南
"""

import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

print("=" * 100)
print("爱企查爬虫测试（2026-03-17）")
print("=" * 100)

from crawlers.enterprise import crawl_enterprises
import json

print("\n【测试】从爱企查爬取海南新成立企业...")
print("-" * 100)

enterprises = crawl_enterprises()

print(f"\n✅ 爬取结果：{len(enterprises)} 家企业")

if enterprises:
    print(f"\n【企业数据展示】")
    print("-" * 100)
    
    for i, enterprise in enumerate(enterprises[:5], 1):
        print(f"\n企业 #{i}")
        print(f"  企业名称：{enterprise.get('name')}")
        print(f"  成立日期：{enterprise.get('registration_date')}")
        print(f"  注册资本：{enterprise.get('capital')} 万元")
        print(f"  行业：{enterprise.get('industry')}")
        print(f"  地址：{enterprise.get('address')}")
        print(f"  地区：{enterprise.get('region')}")
        print(f"  数据来源：{enterprise.get('data_source')}")
    
    print(f"\n【爬虫字段检查】")
    print("-" * 100)
    
    if enterprises:
        sample = enterprises[0]
        required_fields = ['name', 'registration_date', 'capital', 'industry', 'address']
        
        print("必需字段：")
        for field in required_fields:
            value = sample.get(field)
            status = "✓" if value else "✗"
            print(f"  {status} {field}: {value}")
else:
    print("\n⚠️  无法从爱企查获取数据，可能的原因：")
    print("  1. 网络连接问题")
    print("  2. 爱企查网站结构变化")
    print("  3. IP被限制")
    print("\n建议使用本地JSON文件作为备选数据源")

print("\n" + "=" * 100)
