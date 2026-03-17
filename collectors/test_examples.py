"""
快速参考和测试脚本 - 数据收集和汇总/增量功能
"""

import sys
import os
import json
from datetime import datetime

# 确保导入路径
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from collectors.summary_incremental import (
    DataCollector,
    get_all_summaries,
    get_daily_increments,
    get_weekly_increments,
    get_enterprise_summary,
    get_policy_summary,
    get_project_summary,
)


# ==================== 快速使用示例 ====================

def example_1_get_all_summaries():
    """示例 1：获取所有汇总数据"""
    print("\n" + "="*80)
    print("示例 1：获取所有汇总数据")
    print("="*80)
    
    summaries = get_all_summaries()
    print(json.dumps(summaries, indent=2, ensure_ascii=False))


def example_2_get_daily_increments():
    """示例 2：获取过去24小时的增量数据"""
    print("\n" + "="*80)
    print("示例 2：获取过去24小时的增量数据")
    print("="*80)
    
    increments = get_daily_increments()
    print(json.dumps(increments, indent=2, ensure_ascii=False))


def example_3_get_weekly_increments():
    """示例 3：获取过去7天的增量数据"""
    print("\n" + "="*80)
    print("示例 3：获取过去7天的增量数据")
    print("="*80)
    
    increments = get_weekly_increments()
    print(json.dumps(increments, indent=2, ensure_ascii=False))


def example_4_individual_summaries():
    """示例 4：获取各类别的单独汇总"""
    print("\n" + "="*80)
    print("示例 4：获取各类别的单独汇总")
    print("="*80)
    
    print("\n【企业汇总】")
    print(json.dumps(get_enterprise_summary(), indent=2, ensure_ascii=False))
    
    print("\n【政策汇总】")
    print(json.dumps(get_policy_summary(), indent=2, ensure_ascii=False))
    
    print("\n【项目汇总】")
    print(json.dumps(get_project_summary(), indent=2, ensure_ascii=False))


def example_5_detailed_collector():
    """示例 5：使用 DataCollector 类获取详细数据"""
    print("\n" + "="*80)
    print("示例 5：使用 DataCollector 类获取详细数据")
    print("="*80)
    
    collector = DataCollector()
    
    # 获取企业的行业分布
    ent_summary = collector.get_enterprise_summary()
    print("\n【企业按行业分布】")
    for industry, stats in ent_summary['industry_breakdown'].items():
        print(f"  {industry}: {stats['count']} 家企业, 平均收入 {stats['avg_annual_revenue']:.2f} 万元")
    
    # 获取企业的地区分布
    print("\n【企业按地区分布】")
    for region, stats in ent_summary['region_breakdown'].items():
        print(f"  {region}: {stats['count']} 家企业, 总员工 {stats['total_employees']} 人")
    
    # 获取政策的部门分布
    pol_summary = collector.get_policy_summary()
    print("\n【政策按部门发布】")
    for dept, count in pol_summary['department_distribution'].items():
        print(f"  {dept}: {count} 条政策")
    
    # 获取项目的投资分布
    proj_summary = collector.get_project_summary()
    print("\n【项目按投资规模分布】")
    for status, stats in proj_summary['status_distribution'].items():
        print(f"  {status}: {stats['count']} 个项目, 投资 {stats['total_investment']:.0f} 万元")


def example_6_custom_queries():
    """示例 6：自定义时间范围查询"""
    print("\n" + "="*80)
    print("示例 6：自定义时间范围查询")
    print("="*80)
    
    collector = DataCollector()
    
    # 获取过去 7 天的企业增量
    print("\n【过去7天的新增企业】")
    enterprises_7d = collector.get_enterprise_incremental(hours=168)
    print(f"时间范围：{enterprises_7d['time_range']}")
    print(f"新增企业数：{enterprises_7d['count']}")
    for e in enterprises_7d['enterprises'][:3]:
        print(f"  - {e['name']} ({e['industry']}, {e['region']})")
    
    # 获取过去 30 天的政策增量
    print("\n【过去30天的新增政策】")
    policies_30d = collector.get_policy_incremental(days=30)
    print(f"时间范围：{policies_30d['time_range']}")
    print(f"新增政策数：{policies_30d['count']}")
    for p in policies_30d['policies'][:3]:
        print(f"  - {p['title']} ({p['issuing_department']})")
    
    # 获取过去 30 天的项目增量
    print("\n【过去30天的新增项目】")
    projects_30d = collector.get_project_incremental(days=30)
    print(f"时间范围：{projects_30d['time_range']}")
    print(f"新增项目数：{projects_30d['count']}")
    print(f"总投资规模：{projects_30d['total_investment']:.0f} 万元")
    for p in projects_30d['projects'][:3]:
        print(f"  - {p['name']} ({p['region']}, 投资 {p['investment']:.0f}万元)")


# ==================== API 使用示例 ====================

def example_api_usage():
    """API 使用示例"""
    print("\n" + "="*80)
    print("API 使用示例")
    print("="*80)
    
    print("""
# 1. 获取企业汇总
curl http://localhost:5000/api/data/summary/enterprises

# 2. 获取统计概览
curl http://localhost:5000/api/data/stats/overview

# 3. 获取过去14天的项目增量
curl http://localhost:5000/api/data/incremental/projects?days=14

# 4. 获取过去1个月的企业增量
curl http://localhost:5000/api/data/incremental/enterprises?hours=720

# 5. 获取周增量数据
curl http://localhost:5000/api/data/incremental/weekly

# 6. 导出CSV数据
curl http://localhost:5000/api/export/csv?type=enterprises&days=7 > enterprises.csv

# 7. 健康检查
curl http://localhost:5000/api/data/health
    """)


# ==================== 性能对比 ====================

def performance_comparison():
    """性能对比测试"""
    print("\n" + "="*80)
    print("性能对比测试")
    print("="*80)
    
    import time
    
    collector = DataCollector()
    
    # 测试汇总数据获取
    print("\n【汇总数据性能】")
    
    start = time.time()
    ent_summary = collector.get_enterprise_summary()
    ent_time = time.time() - start
    print(f"  企业汇总：{ent_time*1000:.2f}ms")
    
    start = time.time()
    pol_summary = collector.get_policy_summary()
    pol_time = time.time() - start
    print(f"  政策汇总：{pol_time*1000:.2f}ms")
    
    start = time.time()
    proj_summary = collector.get_project_summary()
    proj_time = time.time() - start
    print(f"  项目汇总：{proj_time*1000:.2f}ms")
    
    # 测试增量数据获取
    print("\n【增量数据性能】")
    
    start = time.time()
    ent_inc = collector.get_enterprise_incremental(hours=24)
    ent_inc_time = time.time() - start
    print(f"  企业增量(24h)：{ent_inc_time*1000:.2f}ms - {ent_inc['count']} 条记录")
    
    start = time.time()
    pol_inc = collector.get_policy_incremental(days=7)
    pol_inc_time = time.time() - start
    print(f"  政策增量(7d)：{pol_inc_time*1000:.2f}ms - {pol_inc['count']} 条记录")
    
    start = time.time()
    proj_inc = collector.get_project_incremental(days=14)
    proj_inc_time = time.time() - start
    print(f"  项目增量(14d)：{proj_inc_time*1000:.2f}ms - {proj_inc['count']} 条记录")
    
    # 测试组合报告
    print("\n【组合报告性能】")
    
    start = time.time()
    daily_report = collector.get_daily_summary_report()
    daily_time = time.time() - start
    print(f"  每日汇总报告：{daily_time*1000:.2f}ms")
    
    start = time.time()
    daily_inc_report = collector.get_daily_incremental_report()
    daily_inc_time = time.time() - start
    print(f"  每日增量报告：{daily_inc_time*1000:.2f}ms")


# ==================== 主程序 ====================

def main():
    """主程序 - 运行所有示例"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║         数据收集系统 - 汇总和增量数据功能演示                                  ║
│                                                                               │
│ 项目：海南智能AI全景商业情报系统                                               │
│ 功能：企业数据、政策数据、招商项目的汇总与增量获取                                │
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # 运行示例
        example_1_get_all_summaries()
        example_2_get_daily_increments()
        # example_3_get_weekly_increments()  # 可选，数据较多
        example_4_individual_summaries()
        example_5_detailed_collector()
        example_6_custom_queries()
        
        # 性能测试
        performance_comparison()
        
        # API 使用示例
        example_api_usage()
        
        print("\n" + "="*80)
        print("✅ 所有示例运行完成！")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # 允许通过命令行参数选择运行哪个示例
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num == '1':
            example_1_get_all_summaries()
        elif example_num == '2':
            example_2_get_daily_increments()
        elif example_num == '3':
            example_3_get_weekly_increments()
        elif example_num == '4':
            example_4_individual_summaries()
        elif example_num == '5':
            example_5_detailed_collector()
        elif example_num == '6':
            example_6_custom_queries()
        elif example_num == 'perf':
            performance_comparison()
        elif example_num == 'api':
            example_api_usage()
        else:
            main()
    else:
        main()

# ==================== 快速命令参考 ====================
"""
快速命令参考：

# 运行所有示例
python collectors/test_examples.py

# 运行特定示例
python collectors/test_examples.py 1    # 示例1：获取所有汇总
python collectors/test_examples.py 2    # 示例2：获取每日增量
python collectors/test_examples.py 4    # 示例4：单独汇总
python collectors/test_examples.py 5    # 示例5：详细查询
python collectors/test_examples.py 6    # 示例6：自定义查询
python collectors/test_examples.py perf # 性能测试
python collectors/test_examples.py api  # API使用说明
"""
