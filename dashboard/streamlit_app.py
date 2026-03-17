
import os
import sys
import pandas as pd
import json

# Ensure the project root is on sys.path so imports like `database.models` resolve.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st

from database.models import DailyReport, Enterprise, Policy, Project
from database.postgres import get_session
from collectors.summary_incremental import DataCollector


# 页面配置
st.set_page_config(page_title="海南商业情报仪表板", layout="wide")

st.title("🎯 海南商业情报仪表板")
st.markdown("---")

# 初始化数据收集器
@st.cache_resource
def get_collector():
    return DataCollector()

collector = get_collector()
session = get_session()

# ==================== 标签页导航 ====================
tab1, tab2, tab3, tab4 = st.tabs(["📊 汇总统计", "📈 增量数据", "📋 详细列表", "📊 图表分析"])

# ==================== 第一标签：汇总统计 ====================
with tab1:
    st.header("汇总数据概览")
    
    # 获取汇总数据
    @st.cache_data(ttl=300)
    def get_summary():
        return collector.get_daily_summary_report()
    
    summary = get_summary()
    
    # 关键指标卡片
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "企业总数",
            summary['enterprises']['total_enterprises'],
            delta=f"{summary['enterprises']['active_enterprises']} 存续"
        )
    
    with col2:
        st.metric(
            "有效政策数",
            summary['policies']['total_valid_policies'],
            help="有效状态的政策数量"
        )
    
    with col3:
        st.metric(
            "招商项目数",
            summary['projects']['total_projects'],
            delta=f"{summary['projects']['total_investment']:.0f}万元投资"
        )
    
    st.markdown("---")
    
    # 企业统计详情
    st.subheader("企业统计")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("总员工数", f"{summary['enterprises']['total_employees']:,}")
    with col2:
        st.metric("总注册资本", f"{summary['enterprises']['total_capital_sum']:,.0f} 万元")
    with col3:
        st.metric("总年营收", f"{summary['enterprises']['total_revenue_sum']:,.0f} 万元")
    
    # 企业行业分布
    if summary['enterprises']['industry_breakdown']:
        st.subheader("企业行业分布")
        industry_data = summary['enterprises']['industry_breakdown']
        industry_df = pd.DataFrame([
            {
                '行业': ind,
                '企业数': stat['count'],
                '平均年收入(万元)': stat['avg_annual_revenue']
            }
            for ind, stat in sorted(
                industry_data.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:10]
        ])
        st.bar_chart(industry_df.set_index('行业')['企业数'])
        st.dataframe(industry_df, use_container_width=True)
    
    # 企业地区分布
    if summary['enterprises']['region_breakdown']:
        st.subheader("企业地区分布")
        region_data = summary['enterprises']['region_breakdown']
        region_df = pd.DataFrame([
            {
                '地区': region,
                '企业数': stat['count'],
                '总员工数': stat['total_employees']
            }
            for region, stat in sorted(
                region_data.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )
        ])
        st.dataframe(region_df, use_container_width=True)
    
    st.markdown("---")
    
    # 政策统计
    st.subheader("政策统计")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**按政策类型分布**")
        if summary['policies']['policy_type_distribution']:
            type_data = summary['policies']['policy_type_distribution']
            type_df = pd.DataFrame(list(type_data.items()), columns=['政策类型', '数量'])
            st.bar_chart(type_df.set_index('政策类型')['数量'])
    
    with col2:
        st.write("**按发布部门分布**")
        if summary['policies']['department_distribution']:
            dept_data = summary['policies']['department_distribution']
            dept_df = pd.DataFrame(
                sorted(list(dept_data.items()), key=lambda x: x[1], reverse=True)[:10],
                columns=['部门', '政策数']
            )
            st.bar_chart(dept_df.set_index('部门')['政策数'])
    
    st.markdown("---")
    
    # 项目统计
    st.subheader("招商项目统计")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**按项目状态分布**")
        if summary['projects']['status_distribution']:
            status_data = summary['projects']['status_distribution']
            status_df = pd.DataFrame([
                {
                    '状态': status,
                    '项目数': stat['count'],
                    '投资额(万元)': stat['total_investment']
                }
                for status, stat in status_data.items()
            ])
            st.bar_chart(status_df.set_index('状态')['投资额(万元)'])
    
    with col2:
        st.write("**按项目类型分布**")
        if summary['projects']['type_distribution']:
            type_data = summary['projects']['type_distribution']
            type_df = pd.DataFrame([
                {
                    '项目类型': ptype,
                    '数量': stat['count']
                }
                for ptype, stat in type_data.items()
            ])
            st.bar_chart(type_df.set_index('项目类型')['数量'])

# ==================== 第二标签：增量数据 ====================
with tab2:
    st.header("增量数据分析")
    
    # 时间范围选择
    col1, col2, col3 = st.columns(3)
    with col1:
        enterprise_hours = st.number_input("企业增量(小时)", value=24, min_value=1)
    with col2:
        policy_days = st.number_input("政策增量(天)", value=7, min_value=1)
    with col3:
        project_days = st.number_input("项目增量(天)", value=14, min_value=1)
    
    # 获取增量数据
    @st.cache_data(ttl=300)
    def get_incremental(ent_hours, pol_days, proj_days):
        return {
            'enterprises': collector.get_enterprise_incremental(hours=ent_hours),
            'policies': collector.get_policy_incremental(days=pol_days),
            'projects': collector.get_project_incremental(days=proj_days)
        }
    
    incremental = get_incremental(enterprise_hours, policy_days, project_days)
    
    # 增量数据指标
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            f"新增企业(过去{enterprise_hours}小时)",
            incremental['enterprises']['count'],
            help="新注册或新入库的企业数量"
        )
    
    with col2:
        st.metric(
            f"新增政策(过去{policy_days}天)",
            incremental['policies']['count'],
            help="新发布的政策数量"
        )
    
    with col3:
        st.metric(
            f"新增项目(过去{project_days}天)",
            incremental['projects']['count'],
            delta=f"{incremental['projects']['total_investment']:.0f}万元"
        )
    
    st.markdown("---")
    
    # 新增企业列表
    if incremental['enterprises']['count'] > 0:
        st.subheader(f"新增企业 ({incremental['enterprises']['count']}家)")
        ent_df = pd.DataFrame(incremental['enterprises']['enterprises'])
        if not ent_df.empty:
            st.dataframe(
                ent_df[['name', 'industry', 'region', 'capital', 'employees']],
                use_container_width=True,
                column_config={
                    'name': '企业名称',
                    'industry': '行业',
                    'region': '地区',
                    'capital': '注册资本(万元)',
                    'employees': '员工数'
                }
            )
    
    # 新增政策列表
    if incremental['policies']['count'] > 0:
        st.subheader(f"新增政策 ({incremental['policies']['count']}条)")
        pol_df = pd.DataFrame(incremental['policies']['policies'])
        if not pol_df.empty:
            for _, policy in pol_df.iterrows():
                with st.expander(f"📋 {policy['title']}"):
                    st.write(f"**发布部门**: {policy['issuing_department']}")
                    st.write(f"**政策类型**: {policy['type']}")
                    st.write(f"**发布日期**: {policy['issue_date']}")
                    st.write(f"**内容**: {policy['content_preview']}")
    
    # 新增项目列表
    if incremental['projects']['count'] > 0:
        st.subheader(f"新增项目 ({incremental['projects']['count']}个)")
        proj_df = pd.DataFrame(incremental['projects']['projects'])
        if not proj_df.empty:
            st.dataframe(
                proj_df[['name', 'investment', 'region', 'type', 'status']],
                use_container_width=True,
                column_config={
                    'name': '项目名称',
                    'investment': '投资额(万元)',
                    'region': '地区',
                    'type': '项目类型',
                    'status': '状态'
                }
            )

# ==================== 第三标签：详细列表 ====================
with tab3:
    st.header("详细数据列表")
    
    list_tab1, list_tab2, list_tab3 = st.tabs(["企业详情", "政策详情", "项目详情"])

    
    with list_tab1:
        st.subheader("企业详情")
        enterprises = session.query(Enterprise).all()
        
        # 筛选选项
        col1, col2 = st.columns(2)
        with col1:
            selected_industry = st.multiselect(
                "按行业筛选",
                options=list(set([e.industry for e in enterprises if e.industry])),
                key="industry_select"
            )
        with col2:
            selected_region = st.multiselect(
                "按地区筛选",
                options=list(set([e.region for e in enterprises if e.region])),
                key="region_select"
            )
        
        # 过滤企业
        filtered_enterprises = enterprises
        if selected_industry:
            filtered_enterprises = [e for e in filtered_enterprises if e.industry in selected_industry]
        if selected_region:
            filtered_enterprises = [e for e in filtered_enterprises if e.region in selected_region]
        
        st.write(f"合计：{len(filtered_enterprises)} 家企业")
        
        # 展示企业详情
        for e in filtered_enterprises:
            with st.expander(f"🏢 {e.name} - {e.industry}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**注册号**: {e.registration_number}")
                    st.write(f"**注册资本**: {e.capital}万元")
                    st.write(f"**法定代表人**: {e.legal_representative}")
                    st.write(f"**注册日期**: {e.registration_date}")
                    st.write(f"**地区**: {e.region}")
                with col2:
                    st.write(f"**企业形式**: {e.legal_form}")
                    st.write(f"**经营范围**: {e.business_scope}")
                    st.write(f"**企业状态**: {e.status}")
                    st.write(f"**联系电话**: {e.phone}")
                    st.write(f"**企业地址**: {e.address}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**网站**: {e.website if e.website else '无'}")
                    st.write(f"**员工数**: {e.employees}")
                with col2:
                    st.write(f"**年营收**: {e.annual_revenue}万元")
                    st.write(f"**创建时间**: {e.created_at.strftime('%Y-%m-%d %H:%M') if e.created_at else '无'}")
    
    with list_tab2:
        st.subheader("政策详情")
        policies = session.query(Policy).all()
        
        # 筛选选项
        col1, col2 = st.columns(2)
        with col1:
            selected_policy_type = st.multiselect(
                "按政策类型筛选",
                options=list(set([p.policy_type for p in policies if p.policy_type])),
                key="policy_type_select"
            )
        with col2:
            selected_policy_dept = st.multiselect(
                "按发布部门筛选",
                options=list(set([p.issuing_department for p in policies if p.issuing_department])),
                key="policy_dept_select"
            )
        
        # 过滤政策
        filtered_policies = policies
        if selected_policy_type:
            filtered_policies = [p for p in filtered_policies if p.policy_type in selected_policy_type]
        if selected_policy_dept:
            filtered_policies = [p for p in filtered_policies if p.issuing_department in selected_policy_dept]
        
        st.write(f"合计：{len(filtered_policies)} 条政策")
        
        # 展示政策详情
        for p in filtered_policies:
            with st.expander(f"📄 {p.title}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**政策类型**: {p.policy_type}")
                    st.write(f"**发布部门**: {p.issuing_department}")
                    st.write(f"**发布日期**: {p.issue_date}")
                    st.write(f"**生效日期**: {p.effective_date}")
                with col2:
                    st.write(f"**应用行业**: {p.industry}")
                    st.write(f"**政策状态**: {p.status}")
                    st.write(f"**创建时间**: {p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else '无'}")
                
                st.write("**政策内容**")
                st.write(p.content if p.content else "无详细内容")
                
                st.write("**目标群体**")
                st.write(p.target_groups if p.target_groups else "无")
                
                st.write("**优惠措施**")
                st.write(p.benefits if p.benefits else "无")
                
                st.write("**申请流程**")
                st.write(p.application_process if p.application_process else "无")
                
                st.write(f"**联系方式**: {p.contact_info}")
                if p.document_url:
                    st.write(f"**文档链接**: [{p.document_url}]({p.document_url})")
    
    with list_tab3:
        st.subheader("项目详情")
        projects = session.query(Project).all()
        
        # 筛选选项
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_project_type = st.multiselect(
                "按项目类型筛选",
                options=list(set([p.project_type for p in projects if p.project_type])),
                key="project_type_select"
            )
        with col2:
            selected_project_region = st.multiselect(
                "按地区筛选",
                options=list(set([p.region for p in projects if p.region])),
                key="project_region_select"
            )
        with col3:
            selected_project_status = st.multiselect(
                "按状态筛选",
                options=list(set([p.status for p in projects if p.status])),
                key="project_status_select"
            )
        
        # 过滤项目
        filtered_projects = projects
        if selected_project_type:
            filtered_projects = [p for p in filtered_projects if p.project_type in selected_project_type]
        if selected_project_region:
            filtered_projects = [p for p in filtered_projects if p.region in selected_project_region]
        if selected_project_status:
            filtered_projects = [p for p in filtered_projects if p.status in selected_project_status]
        
        st.write(f"合计：{len(filtered_projects)} 个项目")
        
        # 展示项目详情
        for p in filtered_projects:
            with st.expander(f"🏗️ {p.name} - {p.investment}万元"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**项目类型**: {p.project_type}")
                    st.write(f"**地区**: {p.region}")
                    st.write(f"**投资金额**: {p.investment}万元")
                    st.write(f"**投资来源**: {p.investment_source}")
                    st.write(f"**建设周期**: {p.construction_period}")
                with col2:
                    st.write(f"**预计完成**: {p.expected_completion}")
                    st.write(f"**土地面积**: {p.land_area}亩" if p.land_area else "**土地面积**: 无")
                    st.write(f"**建筑面积**: {p.building_area}平方米" if p.building_area else "**建筑面积**: 无")
                    st.write(f"**项目状态**: {p.status}")
                    st.write(f"**预期企业数**: {p.expected_enterprises}")
                
                st.write("**目标产业**")
                if p.target_industries:
                    try:
                        industries = json.loads(p.target_industries) if isinstance(p.target_industries, str) else p.target_industries
                        st.write(", ".join(industries) if isinstance(industries, list) else str(industries))
                    except:
                        st.write(p.target_industries)
                
                st.write("**基础设施**")
                if p.infrastructure:
                    try:
                        infra = json.loads(p.infrastructure) if isinstance(p.infrastructure, str) else p.infrastructure
                        st.write(", ".join(infra) if isinstance(infra, list) else str(infra))
                    except:
                        st.write(p.infrastructure)
                
                st.write("**政策支持**")
                if p.policy_support:
                    try:
                        support = json.loads(p.policy_support) if isinstance(p.policy_support, str) else p.policy_support
                        st.write(", ".join(support) if isinstance(support, list) else str(support))
                    except:
                        st.write(p.policy_support)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**联系部门**: {p.contact_department}")
                    st.write(f"**联系电话**: {p.contact_phone}")
                with col2:
                    if p.project_website:
                        st.write(f"**项目网站**: [{p.project_website}]({p.project_website})")
                    st.write(f"**创建时间**: {p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else '无'}")

# ==================== 第四标签：图表分析 ====================
with tab4:
    st.header("趋势分析")
    
    # 获取日报数据
    reports = session.query(DailyReport).order_by(DailyReport.report_date).limit(30).all()
    
    if reports:
        st.subheader("数据趋势")
        
        # 准备数据
        df = pd.DataFrame([
            {
                'date': r.report_date,
                'enterprises': r.enterprise_count,
                'policies': r.policy_count,
                'projects': r.project_count,
                'new_enterprises': r.new_enterprises if r.new_enterprises else 0,
                'new_policies': r.new_policies if r.new_policies else 0,
                'new_projects': r.new_projects if r.new_projects else 0,
            }
            for r in reports
        ])
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # 总数趋势
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("数据总量趋势")
            chart_df = df.set_index('date')[['enterprises', 'policies', 'projects']]
            st.line_chart(chart_df)
        
        with col2:
            st.subheader("日新增趋势")
            new_chart_df = df.set_index('date')[['new_enterprises', 'new_policies', 'new_projects']]
            st.bar_chart(new_chart_df)
        
        # 数据表
        st.subheader("日报详情")
        display_df = df[['date', 'enterprises', 'policies', 'projects', 'new_enterprises', 'new_policies', 'new_projects']].copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                'date': '日期',
                'enterprises': '企业总数',
                'policies': '政策总数',
                'projects': '项目总数',
                'new_enterprises': '新增企业',
                'new_policies': '新增政策',
                'new_projects': '新增项目',
            }
        )
    else:
        st.info("暂无日报数据，请先运行数据爬虫")

st.markdown("---")
st.markdown("**更新时间**: " + (reports[-1].report_date if reports else "未更新") if reports else "未更新", unsafe_allow_html=True)
st.markdown("数据来源：海南政府官方网站、企业信息平台等")
