"""
增量和汇总数据获取的实现模块
包含企业、政策、项目的 summary 和 incremental 功能
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy import func

from database.postgres import get_session, get_engine
from database.models import Enterprise, Policy, Project, DailyReport


class DataCollector:
    """统一的数据收集器 - 获取汇总和增量数据"""
    
    def __init__(self):
        self.session = get_session(get_engine())
    
    # ==================== 企业数据 ====================
    
    def get_enterprise_summary(self) -> Dict[str, Any]:
        """获取企业汇总统计"""
        total_count = self.session.query(Enterprise).count()
        active_count = self.session.query(Enterprise).filter(
            Enterprise.status == '存续'
        ).count()
        
        # 按行业统计
        industry_stats = {}
        industries = self.session.query(
            Enterprise.industry, 
            func.count(Enterprise.id).label('count'),
            func.avg(Enterprise.annual_revenue).label('avg_revenue')
        ).group_by(Enterprise.industry).all()
        
        for ind, count, avg_rev in industries:
            industry_stats[ind] = {
                'count': count,
                'avg_annual_revenue': float(avg_rev) if avg_rev else 0
            }
        
        # 按地区统计
        region_stats = {}
        regions = self.session.query(
            Enterprise.region,
            func.count(Enterprise.id).label('count'),
            func.sum(Enterprise.employees).label('total_employees')
        ).group_by(Enterprise.region).all()
        
        for region, count, total_emp in regions:
            region_stats[region] = {
                'count': count,
                'total_employees': total_emp or 0
            }
        
        return {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'total_enterprises': total_count,
            'active_enterprises': active_count,
            'total_capital_sum': float(
                self.session.query(func.sum(Enterprise.capital)).scalar() or 0
            ),
            'total_revenue_sum': float(
                self.session.query(func.sum(Enterprise.annual_revenue)).scalar() or 0
            ),
            'industry_breakdown': industry_stats,
            'region_breakdown': region_stats,
            'total_employees': int(
                self.session.query(func.sum(Enterprise.employees)).scalar() or 0
            )
        }
    
    def get_enterprise_incremental(self, hours: int = 24) -> Dict[str, Any]:
        """获取增量企业（过去N小时内新增）"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        new_enterprises = self.session.query(Enterprise).filter(
            Enterprise.created_at >= cutoff_time
        ).order_by(Enterprise.created_at.desc()).all()
        
        return {
            'time_range': f'Last {hours} hours',
            'cutoff_time': cutoff_time.isoformat(),
            'count': len(new_enterprises),
            'enterprises': [
                {
                    'name': e.name,
                    'industry': e.industry,
                    'capital': e.capital,
                    'region': e.region,
                    'employees': e.employees,
                    'added_at': e.created_at.isoformat() if e.created_at else None
                }
                for e in new_enterprises
            ]
        }
    
    # ==================== 政策数据 ====================
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """获取政策汇总统计"""
        total_count = self.session.query(Policy).filter(
            Policy.status == '有效'
        ).count()
        
        # 按政策类型统计
        policy_type_stats = {}
        types = self.session.query(
            Policy.policy_type,
            func.count(Policy.id).label('count')
        ).filter(Policy.status == '有效').group_by(Policy.policy_type).all()
        
        for ptype, count in types:
            policy_type_stats[ptype or 'Unknown'] = count
        
        # 按行业统计
        industry_stats = {}
        industries = self.session.query(
            Policy.industry,
            func.count(Policy.id).label('count')
        ).filter(Policy.status == '有效').group_by(Policy.industry).all()
        
        for ind, count in industries:
            industry_stats[ind or 'General'] = count
        
        # 按发布部门统计
        department_stats = {}
        departments = self.session.query(
            Policy.issuing_department,
            func.count(Policy.id).label('count')
        ).filter(Policy.status == '有效').group_by(
            Policy.issuing_department
        ).all()
        
        for dept, count in departments:
            department_stats[dept or 'Unknown'] = count
        
        return {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'total_valid_policies': total_count,
            'policy_type_distribution': policy_type_stats,
            'industry_distribution': industry_stats,
            'department_distribution': department_stats,
            'avg_policies_per_department': total_count / len(departments) if departments else 0
        }
    
    def get_policy_incremental(self, days: int = 7) -> Dict[str, Any]:
        """获取增量政策（过去N天内新发布）"""
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        new_policies = self.session.query(Policy).filter(
            Policy.issue_date >= cutoff_date
        ).order_by(Policy.issue_date.desc()).all()
        
        policies_data = []
        for p in new_policies:
            try:
                target_groups = json.loads(p.target_groups) if p.target_groups else []
                benefits = json.loads(p.benefits) if p.benefits else []
            except:
                target_groups = []
                benefits = []
            
            policies_data.append({
                'title': p.title,
                'industry': p.industry,
                'type': p.policy_type,
                'issuing_department': p.issuing_department,
                'issue_date': p.issue_date,
                'effective_date': p.effective_date,
                'target_groups': target_groups,
                'benefits': benefits,
                'content_preview': p.content[:200] if p.content else '',
                'document_url': p.document_url
            })
        
        return {
            'time_range': f'Last {days} days',
            'cutoff_date': cutoff_date,
            'count': len(new_policies),
            'policies': policies_data
        }
    
    # ==================== 招商项目 ====================
    
    def get_project_summary(self) -> Dict[str, Any]:
        """获取项目汇总统计"""
        from sqlalchemy import func
        
        total_count = self.session.query(Project).count()
        
        # 按状态统计投资
        status_stats = {}
        statuses = self.session.query(
            Project.status,
            func.count(Project.id).label('count'),
            func.sum(Project.investment).label('total_investment')
        ).group_by(Project.status).all()
        
        for status, count, total_inv in statuses:
            status_stats[status or 'Unknown'] = {
                'count': count,
                'total_investment': float(total_inv) if total_inv else 0,
                'avg_investment': float(total_inv / count) if total_inv and count else 0
            }
        
        # 按项目类型统计
        type_stats = {}
        types = self.session.query(
            Project.project_type,
            func.count(Project.id).label('count'),
            func.sum(Project.investment).label('total_investment')
        ).group_by(Project.project_type).all()
        
        for ptype, count, total_inv in types:
            type_stats[ptype or 'Other'] = {
                'count': count,
                'total_investment': float(total_inv) if total_inv else 0
            }
        
        # 按地区统计
        region_stats = {}
        regions = self.session.query(
            Project.region,
            func.count(Project.id).label('count'),
            func.sum(Project.investment).label('total_investment')
        ).group_by(Project.region).all()
        
        for region, count, total_inv in regions:
            region_stats[region or 'Unknown'] = {
                'count': count,
                'total_investment': float(total_inv) if total_inv else 0
            }
        
        total_investment = self.session.query(
            func.sum(Project.investment)
        ).scalar() or 0
        
        return {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'total_projects': total_count,
            'total_investment': float(total_investment),
            'avg_project_investment': float(total_investment / total_count) if total_count else 0,
            'status_distribution': status_stats,
            'type_distribution': type_stats,
            'region_distribution': region_stats,
            'total_land_area': float(
                self.session.query(func.sum(Project.land_area)).scalar() or 0
            ),
            'total_building_area': float(
                self.session.query(func.sum(Project.building_area)).scalar() or 0
            )
        }
    
    def get_project_incremental(self, days: int = 14) -> Dict[str, Any]:
        """获取增量项目（过去N天内新增）"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        new_projects = self.session.query(Project).filter(
            Project.created_at >= cutoff_time
        ).order_by(Project.created_at.desc()).all()
        
        projects_data = []
        for p in new_projects:
            try:
                target_industries = json.loads(p.target_industries) if p.target_industries else []
                infrastructure = json.loads(p.infrastructure) if p.infrastructure else []
                policy_support = json.loads(p.policy_support) if p.policy_support else []
            except:
                target_industries = []
                infrastructure = []
                policy_support = []
            
            projects_data.append({
                'name': p.name,
                'investment': p.investment,
                'type': p.project_type,
                'region': p.region,
                'status': p.status,
                'investment_source': p.investment_source,
                'construction_period': p.construction_period,
                'expected_completion': p.expected_completion,
                'land_area': p.land_area,
                'building_area': p.building_area,
                'target_industries': target_industries,
                'expected_enterprises': p.expected_enterprises,
                'policy_support': policy_support,
                'contact_department': p.contact_department,
                'contact_phone': p.contact_phone,
                'added_at': p.created_at.isoformat() if p.created_at else None
            })
        
        return {
            'time_range': f'Last {days} days',
            'cutoff_time': cutoff_time.isoformat(),
            'count': len(new_projects),
            'total_investment': sum(p['investment'] for p in projects_data),
            'projects': projects_data
        }
    
    # ==================== 综合报告 ====================
    
    def get_daily_summary_report(self) -> Dict[str, Any]:
        """获取每日综合汇总报告"""
        return {
            'generated_at': datetime.now().isoformat(),
            'enterprises': self.get_enterprise_summary(),
            'policies': self.get_policy_summary(),
            'projects': self.get_project_summary()
        }
    
    def get_daily_incremental_report(self) -> Dict[str, Any]:
        """获取每日增量报告"""
        return {
            'generated_at': datetime.now().isoformat(),
            'enterprises': self.get_enterprise_incremental(hours=24),
            'policies': self.get_policy_incremental(days=1),
            'projects': self.get_project_incremental(days=1)
        }
    
    def get_weekly_incremental_report(self) -> Dict[str, Any]:
        """获取周增量报告"""
        return {
            'generated_at': datetime.now().isoformat(),
            'enterprises': self.get_enterprise_incremental(hours=168),
            'policies': self.get_policy_incremental(days=7),
            'projects': self.get_project_incremental(days=7)
        }


# ==================== 快速时用函数 ====================

def get_all_summaries() -> Dict[str, Any]:
    """快速获取所有汇总数据"""
    collector = DataCollector()
    return collector.get_daily_summary_report()


def get_daily_increments() -> Dict[str, Any]:
    """快速获取过去24小时的增量数据"""
    collector = DataCollector()
    return collector.get_daily_incremental_report()


def get_weekly_increments() -> Dict[str, Any]:
    """快速获取过去7天的增量数据"""
    collector = DataCollector()
    return collector.get_weekly_incremental_report()


def get_enterprise_summary() -> Dict[str, Any]:
    """快速获取企业汇总"""
    collector = DataCollector()
    return collector.get_enterprise_summary()


def get_policy_summary() -> Dict[str, Any]:
    """快速获取政策汇总"""
    collector = DataCollector()
    return collector.get_policy_summary()


def get_project_summary() -> Dict[str, Any]:
    """快速获取项目汇总"""
    collector = DataCollector()
    return collector.get_project_summary()


if __name__ == '__main__':
    # 测试使用
    import sys
    sys.path.insert(0, '../')
    
    collector = DataCollector()
    
    print("=" * 80)
    print("企业数据汇总")
    print("=" * 80)
    print(json.dumps(collector.get_enterprise_summary(), 
                     indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("企业数据增量（过去24小时）")
    print("=" * 80)
    print(json.dumps(collector.get_enterprise_incremental(), 
                     indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("政策数据汇总")
    print("=" * 80)
    print(json.dumps(collector.get_policy_summary(), 
                     indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("政策数据增量（过去7天）")
    print("=" * 80)
    print(json.dumps(collector.get_policy_incremental(), 
                     indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("项目数据汇总")
    print("=" * 80)
    print(json.dumps(collector.get_project_summary(), 
                     indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("项目数据增量（过去14天）")
    print("=" * 80)
    print(json.dumps(collector.get_project_incremental(), 
                     indent=2, ensure_ascii=False))
