# -*- coding: utf-8 -*-
"""
AI 智能问答页面 - 豆包 AI 版本
支持自然语言查询、智能图表生成、流式响应
"""

import streamlit as st
import pandas as pd
import time
from core.llm_agent import DoubaoAgent
from utils.spark_processor import SparkDataManager
from utils.db_manager import DatabaseManager


def show_ai_chat_page():
    """AI 智能问答页面"""
    st.markdown('<div class="main-header">🤖 豆包 AI 智能问答助手</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 初始化
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'doubao_agent' not in st.session_state:
        # 初始化豆包 AI (默认使用 Mock 模式)
        st.session_state.doubao_agent = DoubaoAgent(use_mock=True)
    
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = SparkDataManager()
    
    if 'corporate_data' not in st.session_state:
        # 预加载企业数据
        try:
            X_corp, y_corp = st.session_state.data_manager.load_corporate_data('data.csv')
            st.session_state.corporate_data = X_corp.copy()
            st.session_state.corporate_data['Bankrupt?'] = y_corp
        except Exception as e:
            st.session_state.corporate_data = None
            print(f"企业数据加载失败: {str(e)}")
    
    if 'personal_data' not in st.session_state:
        # 预加载个人数据
        try:
            X_pers, y_pers, _ = st.session_state.data_manager.load_personal_data('german_credit_data.csv')
            st.session_state.personal_data = X_pers.copy()
            st.session_state.personal_data['Risk'] = y_pers
        except Exception as e:
            st.session_state.personal_data = None
            print(f"个人数据加载失败: {str(e)}")
    
    agent = st.session_state.doubao_agent
    db = DatabaseManager()
    
    # 侧边栏 - 功能说明
    with st.sidebar:
        st.subheader("💡 使用指南")
        st.markdown("""
        **支持的功能**:
        
        📈 **智能图表生成**
        - "画出企业ROA的柱状图"
        - "绘制负债率的折线图"
        - "展示净收入的饼图"
        - "显示ROA的散点图"
        
        💬 **智能问答**
        - "你好"
        - "帮助"
        - "分析一下企业财务状况"
        - "ROA指标是什么意思"
        
        🎯 **数据分析**
        - "企业的平均负债率是多少"
        - "有多少家企业处于高风险"
        """)
        
        st.markdown("---")
        
        # 数据集选择
        st.subheader("📊 数据集选择")
        dataset_choice = st.radio(
            "选择分析数据集:",
            ["企业数据", "个人数据"],
            key="dataset_choice"
        )
        
        st.markdown("---")
        
        # AI 模式切换
        st.subheader("🤖 AI 模式")
        current_mode = "Mock 模式" if agent.use_mock else "真实 API 模式"
        st.info(f"当前模式: **{current_mode}**")
        
        if st.button("🔄 切换模式"):
            agent.use_mock = not agent.use_mock
            new_mode = "Mock 模式" if agent.use_mock else "真实 API 模式"
            st.success(f"已切换到: {new_mode}")
            st.rerun()
        
        st.markdown("---")
        
        if st.button("🗑️ 清空对话历史"):
            st.session_state.chat_history = []
            st.rerun()
    
    # 显示对话历史
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # 如果有图表，显示
            if "chart" in message and message["chart"] is not None:
                st.plotly_chart(message["chart"], use_container_width=True)
    
    # 用户输入
    user_input = st.chat_input("请输入您的问题...")
    
    if user_input:
        # 添加用户消息到历史
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # AI 处理
        with st.chat_message("assistant"):
            # 选择数据集
            if 'dataset_choice' in st.session_state and st.session_state.dataset_choice == "个人数据":
                dataframe_context = st.session_state.personal_data
            else:
                dataframe_context = st.session_state.corporate_data
            
            # 调用豆包 AI
            with st.spinner("🤖 豆包 AI 正在思考..."):
                try:
                    # 调用 chat 方法
                    result = agent.chat(user_input, dataframe_context=dataframe_context)
                    
                    # 流式显示文本 (模拟打字机效果)
                    answer_text = result['answer']
                    
                    # 创建占位符用于流式输出
                    text_placeholder = st.empty()
                    displayed_text = ""
                    
                    # 逐字显示
                    for char in answer_text:
                        displayed_text += char
                        text_placeholder.markdown(displayed_text)
                        time.sleep(0.01)  # 打字机效果延迟
                    
                    # 如果需要显示图表
                    chart_obj = None
                    if result['show_chart'] and result['chart_type'] and result['chart_col']:
                        if dataframe_context is not None:
                            chart_obj = agent.generate_chart(
                                dataframe_context,
                                result['chart_type'],
                                result['chart_col']
                            )
                            
                            if chart_obj:
                                st.plotly_chart(chart_obj, use_container_width=True)
                            else:
                                st.warning("⚠️ 图表生成失败，请检查数据列名。")
                    
                    # 保存到历史
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer_text,
                        "chart": chart_obj
                    })
                    
                    # 记录日志
                    if 'user' in st.session_state:
                        action_type = "AI图表生成" if result['show_chart'] else "AI对话"
                        db.log_action(
                            st.session_state.user['username'],
                            action_type,
                            user_input
                        )
                
                except Exception as e:
                    error_text = f"❌ AI 处理失败: {str(e)}"
                    st.error(error_text)
                    
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_text
                    })
        
        st.rerun()
    
    # 快捷示例
    st.markdown("---")
    st.subheader("💡 快捷示例")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👋 你好"):
            st.session_state.chat_history.append({
                "role": "user",
                "content": "你好"
            })
            st.rerun()
    
    with col2:
        if st.button("📈 画ROA柱状图"):
            st.session_state.chat_history.append({
                "role": "user",
                "content": "画出企业ROA的柱状图"
            })
            st.rerun()
    
    with col3:
        if st.button("📊 画负债率折线图"):
            st.session_state.chat_history.append({
                "role": "user",
                "content": "绘制负债率的折线图"
            })
            st.rerun()
    
    with col4:
        if st.button("❓ 帮助"):
            st.session_state.chat_history.append({
                "role": "user",
                "content": "帮助"
            })
            st.rerun()
