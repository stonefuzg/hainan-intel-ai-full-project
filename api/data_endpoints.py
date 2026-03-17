"""
API 端点 - 提供汇总和增量数据的访问接口
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from collectors.summary_incremental import DataCollector

# 创建蓝图
data_bp = Blueprint('data', __name__, url_prefix='/api/data')


# ==================== 汇总数据端点 ====================

@data_bp.route('/summary/enterprises', methods=['GET'])
def get_enterprises_summary():
    """获取企业数据汇总"""
    try:
        collector = DataCollector()
        summary = collector.get_enterprise_summary()
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': summary
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@data_bp.route('/summary/policies', methods=['GET'])
def get_policies_summary():
    """获取政策数据汇总"""
    try:
        collector = DataCollector()
        summary = collector.get_policy_summary()
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': summary
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@data_bp.route('/summary/projects', methods=['GET'])
def get_projects_summary():
    """获取招商项目汇总"""
    try:
        collector = DataCollector()
        summary = collector.get_project_summary()
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': summary
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@data_bp.route('/summary/all', methods=['GET'])
def get_all_summary():
    """获取所有汇总数据"""
    try:
        collector = DataCollector()
        summary = collector.get_daily_summary_report()
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': summary
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 增量数据端点 ====================

@data_bp.route('/incremental/enterprises', methods=['GET'])
def get_enterprises_incremental():
    """
    获取增量企业数据
    参数：
      - hours: 过去N小时内的数据（默认 24）
    """
    try:
        hours = request.args.get('hours', default=24, type=int)
        collector = DataCollector()
        incremental = collector.get_enterprise_incremental(hours=hours)
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': incremental
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@data_bp.route('/incremental/policies', methods=['GET'])
def get_policies_incremental():
    """
    获取增量政策数据
    参数：
      - days: 过去N天内的数据（默认 7）
    """
    try:
        days = request.args.get('days', default=7, type=int)
        collector = DataCollector()
        incremental = collector.get_policy_incremental(days=days)
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': incremental
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@data_bp.route('/incremental/projects', methods=['GET'])
def get_projects_incremental():
    """
    获取增量招商项目数据
    参数：
      - days: 过去N天内的数据（默认 14）
    """
    try:
        days = request.args.get('days', default=14, type=int)
        collector = DataCollector()
        incremental = collector.get_project_incremental(days=days)
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': incremental
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@data_bp.route('/incremental/daily', methods=['GET'])
def get_daily_incremental():
    """获取过去24小时的全量增量数据"""
    try:
        collector = DataCollector()
        incremental = collector.get_daily_incremental_report()
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': incremental
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@data_bp.route('/incremental/weekly', methods=['GET'])
def get_weekly_incremental():
    """获取过去7天的全量增量数据"""
    try:
        collector = DataCollector()
        incremental = collector.get_weekly_incremental_report()
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': incremental
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 综合统计端点 ====================

@data_bp.route('/stats/overview', methods=['GET'])
def get_stats_overview():
    """获取统计概览（汇总 + 增量）"""
    try:
        collector = DataCollector()
        
        summary = collector.get_daily_summary_report()
        daily_incremental = collector.get_daily_incremental_report()
        
        # 组合统计数据
        overview = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'enterprises': {
                    'total': summary['enterprises']['total_enterprises'],
                    'active': summary['enterprises']['active_enterprises'],
                    'total_employees': summary['enterprises']['total_employees'],
                    'top_industries': sorted(
                        summary['enterprises']['industry_breakdown'].items(),
                        key=lambda x: x[1]['count'],
                        reverse=True
                    )[:5]
                },
                'policies': {
                    'total': summary['policies']['total_valid_policies'],
                    'count_by_type': summary['policies']['policy_type_distribution'],
                    'count_by_industry': summary['policies']['industry_distribution']
                },
                'projects': {
                    'total': summary['projects']['total_projects'],
                    'total_investment': summary['projects']['total_investment'],
                    'by_status': summary['projects']['status_distribution'],
                    'by_region': sorted(
                        summary['projects']['region_distribution'].items(),
                        key=lambda x: x[1]['total_investment'],
                        reverse=True
                    )[:5]
                }
            },
            'today_additions': {
                'enterprises': daily_incremental['enterprises']['count'],
                'policies': daily_incremental['policies']['count'],
                'projects': daily_incremental['projects']['count'],
            },
            'growth_rate': {
                'enterprises_percent': (
                    (daily_incremental['enterprises']['count'] / 
                     summary['enterprises']['total_enterprises'] * 100)
                    if summary['enterprises']['total_enterprises'] > 0 else 0
                ),
                'policies_percent': (
                    (daily_incremental['policies']['count'] / 
                     summary['policies']['total_valid_policies'] * 100)
                    if summary['policies']['total_valid_policies'] > 0 else 0
                ),
                'projects_percent': (
                    (daily_incremental['projects']['count'] / 
                     summary['projects']['total_projects'] * 100)
                    if summary['projects']['total_projects'] > 0 else 0
                ),
            }
        }
        
        return jsonify({
            'success': True,
            'data': overview
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@data_bp.route('/export/csv', methods=['GET'])
def export_csv():
    """
    导出为本地CSV文件
    参数：
      - type: 'enterprises', 'policies', 'projects', 'all'（默认 all）
      - days: 过去多少天的增量数据（默认 7）
    """
    try:
        import csv
        from io import StringIO
        from database.postgres import get_session, get_engine
        from database.models import Enterprise, Policy, Project
        
        data_type = request.args.get('type', default='all')
        days = request.args.get('days', default=7, type=int)
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        session = get_session(get_engine())
        
        output = StringIO()
        
        if data_type in ['enterprises', 'all']:
            writer = csv.writer(output)
            writer.writerow(['企业名称', '行业', '地区', '注册资本', '员工数', '年收入'])
            
            enterprises = session.query(Enterprise).filter(
                Enterprise.created_at >= cutoff
            ).all()
            
            for e in enterprises:
                writer.writerow([
                    e.name, e.industry, e.region, e.capital, e.employees, e.annual_revenue
                ])
        
        return output.getvalue(), 200, {
            'Content-Disposition': 'attachment; filename="data_export.csv"',
            'Content-Type': 'text/csv; charset=utf-8'
        }
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 健康检查 ====================

@data_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        collector = DataCollector()
        # 尝试查询一条数据以验证数据库连接
        collector.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 503


# 注册蓝图的函数
def register_data_api(app):
    """向 Flask 应用注册数据 API"""
    app.register_blueprint(data_bp)
    print("✅ 数据 API 已注册")
    print("   POST /api/data/summary/enterprises - 获取企业汇总")
    print("   POST /api/data/summary/policies - 获取政策汇总")
    print("   POST /api/data/summary/projects - 获取项目汇总")
    print("   POST /api/data/summary/all - 获取全量汇总")
    print("   POST /api/data/incremental/enterprises - 获取企业增量")
    print("   POST /api/data/incremental/policies - 获取政策增量")
    print("   POST /api/data/incremental/projects - 获取项目增量")
    print("   POST /api/data/incremental/daily - 获取日增量")
    print("   POST /api/data/incremental/weekly - 获取周增量")
    print("   POST /api/data/stats/overview - 获取统计概览")
