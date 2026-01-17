# -*- coding: utf-8 -*-
"""
金融智能分析系统 - 完整版 (Final Version)
Financial Intelligent Analysis System

新增功能:
1. 用户登录与权限管理
2. 数据采集与管理模块
3. AI 智能问答 (Text-to-Chart + Text-to-Excel)
4. 系统管理中心 (仅管理员)
5. 操作日志记录
"""

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

from core.model_factory import ModelEngine
from core.llm_agent import DoubaoAgent
from utils.spark_processor import SparkDataManager
from utils.db_manager import DatabaseManager

# 导入页面模块
from pages.data_admin import show_data_admin_page
from pages.system_admin import show_system_admin_page
from pages.ai_chat import show_ai_chat_page


# ==================== 页面配置 ====================
st.set_page_config(
    page_title="金融智能分析系统 - 完整版",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 登录系统 ====================
def show_login_page():
    """登录页面"""
    st.markdown('<div class="main-header">🔐 金融智能分析系统</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">请登录以继续</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.subheader("用户登录")
            
            username = st.text_input("用户名", placeholder="请输入用户名")
            password = st.text_input("密码", type="password", placeholder="请输入密码")
            
            submitted = st.form_submit_button("登录", use_container_width=True, type="primary")
            
            if submitted:
                db = DatabaseManager()
                user = db.verify_user(username, password)
                
                if user:
                    st.session_state.user = user
                    st.session_state.logged_in = True
                    
                    # 记录登录日志
                    db.log_action(username, "用户登录", "成功登录系统")
                    
                    st.success(f"✅ 欢迎回来, {username}!")
                    st.rerun()
                else:
                    st.error("❌ 用户名或密码错误！")
        
        st.info("""
        **默认账号**:
        - 管理员: admin / 123456
        - 普通用户: 请联系管理员创建
        """)


# ==================== 初始化 ====================
@st.cache_resource
def init_system():
    """初始化系统组件"""
    engine = ModelEngine()
    llm = DoubaoAgent(use_mock=True)
    return engine, llm

# 检查登录状态
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login_page()
    st.stop()

# 已登录，初始化系统
engine, llm = init_system()


# ==================== 辅助函数 ====================
def create_gauge_chart(value, title, max_value=100):
    """创建仪表盘图表"""
    if value < 30:
        color = "green"
    elif value < 70:
        color = "orange"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        delta={'reference': 50, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': 'lightgreen'},
                {'range': [30, 70], 'color': 'lightyellow'},
                {'range': [70, 100], 'color': 'lightcoral'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig


def load_dashboard_data():
    """加载仪表盘数据"""
    try:
        data_manager = SparkDataManager()
        
        _, y_corp = data_manager.load_corporate_data('data.csv')
        corp_risk_rate = (y_corp.sum() / len(y_corp)) * 100
        
        _, y_pers, _ = data_manager.load_personal_data('german_credit_data.csv')
        pers_risk_rate = (y_pers.sum() / len(y_pers)) * 100
        
        avg_risk = (corp_risk_rate + pers_risk_rate) / 2
        
        return {
            'corporate_risk': corp_risk_rate,
            'personal_risk': pers_risk_rate,
            'average_risk': avg_risk,
            'engine_info': data_manager.get_engine_info()
        }
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return None


# ==================== 页面函数 ====================
def show_dashboard():
    """数据驾驶舱"""
    st.markdown('<div class="main-header">📊 金融智能分析系统 - 数据驾驶舱</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">基于 AI 大模型与大数据技术的智能风控平台</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    dashboard_data = load_dashboard_data()
    
    if dashboard_data:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🖥️ 计算引擎",
                value=dashboard_data['engine_info']['engine'],
                delta=dashboard_data['engine_info']['status']
            )
        
        with col2:
            st.metric(
                label="🏢 企业风险率",
                value=f"{dashboard_data['corporate_risk']:.1f}%",
                delta="-3.2%" if dashboard_data['corporate_risk'] < 10 else "+2.1%",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                label="👤 个人违约率",
                value=f"{dashboard_data['personal_risk']:.1f}%",
                delta="-1.5%" if dashboard_data['personal_risk'] < 35 else "+0.8%",
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                label="📈 系统平均风险",
                value=f"{dashboard_data['average_risk']:.1f}%",
                delta="稳定"
            )
        
        st.markdown("---")
        
        st.subheader("🎯 实时风险监控仪表盘")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig1 = create_gauge_chart(dashboard_data['corporate_risk'], "企业破产风险指数")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = create_gauge_chart(dashboard_data['personal_risk'], "个人违约风险指数")
            st.plotly_chart(fig2, use_container_width=True)
        
        with col3:
            fig3 = create_gauge_chart(dashboard_data['average_risk'], "系统综合风险指数")
            st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("---")
        
        st.subheader("🌅 风险构成旭日图")
        
        sunburst_data = pd.DataFrame({
            'labels': ['总风险', '企业风险', '个人风险', '高风险企业', '低风险企业', '高风险个人', '低风险个人'],
            'parents': ['', '总风险', '总风险', '企业风险', '企业风险', '个人风险', '个人风险'],
            'values': [
                100,
                dashboard_data['corporate_risk'],
                dashboard_data['personal_risk'],
                dashboard_data['corporate_risk'] * 0.6,
                dashboard_data['corporate_risk'] * 0.4,
                dashboard_data['personal_risk'] * 0.7,
                dashboard_data['personal_risk'] * 0.3
            ]
        })
        
        fig_sunburst = px.sunburst(
            sunburst_data,
            names='labels',
            parents='parents',
            values='values',
            color='values',
            color_continuous_scale='RdYlGn_r',
            title="风险层级分布图"
        )
        
        fig_sunburst.update_layout(height=500)
        st.plotly_chart(fig_sunburst, use_container_width=True)


def show_corporate_assessment():
    """企业风险评估"""
    st.markdown('<div class="main-header">🏢 企业破产风险智能评估</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### 📋 请输入企业财务指标")
    
    with st.form("corporate_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            roa = st.number_input("ROA (资产回报率)", -1.0, 1.0, 0.4, 0.01)
            debt_ratio = st.number_input("Debt Ratio (负债比率)", 0.0, 1.0, 0.2, 0.01)
            net_income = st.number_input("Net Income Ratio (净收入比率)", -1.0, 1.0, 0.15, 0.01)
        
        with col2:
            gross_margin = st.number_input("Gross Margin (毛利率)", 0.0, 1.0, 0.6, 0.01)
            liability_ratio = st.number_input("Liability to Assets (流动负债比率)", 0.0, 1.0, 0.15, 0.01)
        
        submitted = st.form_submit_button("🔍 开始智能评估", use_container_width=True)
    
    if submitted:
        try:
            input_data = {
                'ROA': roa,
                'Debt_Ratio': debt_ratio,
                'Net_Income_Ratio': net_income,
                'Gross_Margin': gross_margin,
                'Liability_Assets_Ratio': liability_ratio
            }
            
            with st.spinner("🤖 AI 正在分析中..."):
                prob, risk_label = engine.predict_corporate(input_data)
                risk_percentage = prob * 100
            
            st.markdown("---")
            st.subheader("📈 智能评估结果")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = create_gauge_chart(risk_percentage, "企业破产风险概率")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.metric("风险评级", risk_label, f"{risk_percentage:.2f}%")
                
                if prob > 0.7:
                    st.error("🚨 极高风险！")
                elif prob > 0.4:
                    st.warning("⚠️ 中等风险")
                else:
                    st.success("✅ 低风险")
            
            st.markdown("---")
            st.subheader("🤖 AI 投资顾问分析报告")
            
            with st.spinner("AI 正在生成专业分析报告..."):
                ai_report = llm.generate_analysis_report(prob, 'corporate', input_data)
            
            st.markdown(ai_report)
            
            # 记录日志
            if 'user' in st.session_state:
                db = DatabaseManager()
                db.log_action(
                    st.session_state.user['username'],
                    "企业风险评估",
                    f"评估结果: {risk_percentage:.2f}%"
                )
            
        except FileNotFoundError:
            st.warning("⚠️ 模型文件未找到，请先训练模型。")
        except Exception as e:
            st.error(f"预测失败: {str(e)}")


def show_personal_assessment():
    """个人信贷评估"""
    st.markdown('<div class="main-header">👤 个人信贷违约智能评估</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### 📋 请输入个人信贷信息")
    
    with st.form("personal_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("年龄 (Age)", 18, 100, 35, 1)
            credit_amount = st.number_input("信贷金额 (Credit Amount)", 0, 100000, 5000, 100)
            duration = st.number_input("贷款期限 (Duration, 月)", 1, 72, 24, 1)
        
        with col2:
            sex = st.selectbox("性别 (Sex)", ['male : single', 'female : divorced/separated/married', 'male : married/widowed'])
            housing = st.selectbox("住房情况 (Housing)", ['own', 'rent', 'for free'])
        
        submitted = st.form_submit_button("🔍 开始智能评估", use_container_width=True)
    
    if submitted:
        try:
            input_data = {
                'Age': age,
                'Credit_amount': credit_amount,
                'Duration': duration,
                'Sex': sex,
                'Housing': housing
            }
            
            with st.spinner("🤖 AI 正在分析中..."):
                prob, risk_label = engine.predict_personal(input_data)
                risk_percentage = prob * 100
            
            st.markdown("---")
            st.subheader("📈 智能评估结果")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = create_gauge_chart(risk_percentage, "个人违约风险概率")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.metric("风险评级", risk_label, f"{risk_percentage:.2f}%")
                
                if prob > 0.7:
                    st.error("🚨 极高风险！")
                elif prob > 0.4:
                    st.warning("⚠️ 中等风险")
                else:
                    st.success("✅ 低风险")
            
            st.markdown("---")
            st.subheader("🤖 AI 信贷审批分析报告")
            
            with st.spinner("AI 正在生成专业分析报告..."):
                ai_report = llm.generate_analysis_report(prob, 'personal', input_data)
            
            st.markdown(ai_report)
            
            # 记录日志
            if 'user' in st.session_state:
                db = DatabaseManager()
                db.log_action(
                    st.session_state.user['username'],
                    "个人信贷评估",
                    f"评估结果: {risk_percentage:.2f}%"
                )
            
        except FileNotFoundError:
            st.warning("⚠️ 模型文件未找到，请先训练模型。")
        except Exception as e:
            st.error(f"预测失败: {str(e)}")


# ==================== 主程序 ====================
def main():
    """主函数"""
    
    # 侧边栏
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/financial-growth-analysis.png", width=80)
        st.title("金融智能分析系统")
        
        # 显示当前用户
        st.info(f"👤 当前用户: **{st.session_state.user['username']}**\n\n角色: {st.session_state.user['role']}")
        
        st.markdown("---")
        
        # 导航菜单
        menu_options = ["数据驾驶舱", "企业风险评估", "个人信贷评估", "AI智能问答", "数据管理"]
        menu_icons = ["speedometer2", "building", "person", "robot", "database"]
        
        # 管理员额外菜单
        if st.session_state.user['role'] == 'admin':
            menu_options.append("系统管理")
            menu_icons.append("gear")
        
        selected = option_menu(
            menu_title="导航菜单",
            options=menu_options,
            icons=menu_icons,
            menu_icon="cast",
            default_index=0,
        )
        
        st.markdown("---")
        
        # 模型管理
        st.subheader("🔧 模型管理")
        
        if st.button("🚀 重新训练模型", use_container_width=True):
            with st.spinner("正在训练模型..."):
                try:
                    engine.train_all_models()
                    st.success("✅ 训练完成!")
                    st.balloons()
                except Exception as e:
                    st.error(f"训练失败: {str(e)}")
        
        model_exists = os.path.exists('models/corporate_model.pkl') and os.path.exists('models/personal_model.pkl')
        
        if model_exists:
            st.success("✅ 模型已就绪")
        else:
            st.warning("⚠️ 模型未初始化")
        
        st.markdown("---")
        
        # 退出登录
        if st.button("🚪 退出登录", use_container_width=True):
            # 记录日志
            db = DatabaseManager()
            db.log_action(st.session_state.user['username'], "用户登出", "退出系统")
            
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
    
    # 页面路由
    if selected == "数据驾驶舱":
        show_dashboard()
    elif selected == "企业风险评估":
        show_corporate_assessment()
    elif selected == "个人信贷评估":
        show_personal_assessment()
    elif selected == "AI智能问答":
        show_ai_chat_page()
    elif selected == "数据管理":
        show_data_admin_page()
    elif selected == "系统管理":
        show_system_admin_page()


if __name__ == "__main__":
    main()
