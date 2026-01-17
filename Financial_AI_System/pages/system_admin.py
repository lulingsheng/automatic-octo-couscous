# -*- coding: utf-8 -*-
"""
系统管理页面 - System Administration
仅管理员可见，提供用户管理和日志查看功能
"""

import streamlit as st
import pandas as pd
from utils.db_manager import DatabaseManager


def show_system_admin_page():
    """系统管理页面 (仅管理员)"""
    
    # 权限检查
    if 'user' not in st.session_state or st.session_state.user['role'] != 'admin':
        st.error("⛔ 权限不足！此页面仅管理员可访问。")
        return
    
    st.markdown('<div class="main-header">⚙️ 系统管理中心</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    db = DatabaseManager()
    
    # 选项卡
    tab1, tab2 = st.tabs(["👥 用户管理", "📋 操作日志"])
    
    # Tab 1: 用户管理
    with tab1:
        st.subheader("用户管理")
        
        # 添加新用户
        with st.expander("➕ 添加新用户", expanded=False):
            with st.form("add_user_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    new_username = st.text_input("用户名")
                
                with col2:
                    new_password = st.text_input("密码", type="password")
                
                with col3:
                    new_role = st.selectbox("角色", ["user", "admin"])
                
                submitted = st.form_submit_button("添加用户", type="primary")
                
                if submitted:
                    if new_username and new_password:
                        success = db.add_user(new_username, new_password, new_role)
                        
                        if success:
                            st.success(f"✅ 用户 {new_username} 添加成功！")
                            
                            # 记录日志
                            db.log_action(
                                st.session_state.user['username'],
                                "添加用户",
                                f"添加了新用户: {new_username} ({new_role})"
                            )
                            
                            st.rerun()
                        else:
                            st.error("❌ 用户名已存在！")
                    else:
                        st.warning("请填写完整信息")
        
        st.markdown("---")
        
        # 用户列表
        st.subheader("现有用户列表")
        
        users = db.get_all_users()
        
        if users:
            users_df = pd.DataFrame(
                users,
                columns=['ID', '用户名', '角色', '创建时间']
            )
            
            st.dataframe(users_df, use_container_width=True)
            
            # 删除用户
            st.markdown("---")
            st.subheader("删除用户")
            
            user_to_delete = st.selectbox(
                "选择要删除的用户",
                [u[1] for u in users if u[1] != 'admin']
            )
            
            if st.button("🗑️ 删除选中用户", type="secondary"):
                if user_to_delete:
                    success = db.delete_user(user_to_delete)
                    
                    if success:
                        st.success(f"✅ 用户 {user_to_delete} 已删除")
                        
                        # 记录日志
                        db.log_action(
                            st.session_state.user['username'],
                            "删除用户",
                            f"删除了用户: {user_to_delete}"
                        )
                        
                        st.rerun()
                    else:
                        st.error("❌ 删除失败")
        else:
            st.info("暂无用户")
    
    # Tab 2: 操作日志
    with tab2:
        st.subheader("系统操作日志")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            log_limit = st.slider("显示记录数", 10, 500, 100, 10)
        
        with col2:
            if st.button("🗑️ 清空日志", type="secondary"):
                db.clear_logs()
                st.success("✅ 日志已清空")
                st.rerun()
        
        # 获取日志
        logs = db.get_logs(limit=log_limit)
        
        if logs:
            logs_df = pd.DataFrame(
                logs,
                columns=['时间', '用户', '操作', '详情']
            )
            
            # 筛选功能
            col1, col2 = st.columns(2)
            
            with col1:
                user_filter = st.multiselect(
                    "筛选用户",
                    options=logs_df['用户'].unique().tolist(),
                    default=[]
                )
            
            with col2:
                action_filter = st.multiselect(
                    "筛选操作类型",
                    options=logs_df['操作'].unique().tolist(),
                    default=[]
                )
            
            # 应用筛选
            filtered_df = logs_df.copy()
            
            if user_filter:
                filtered_df = filtered_df[filtered_df['用户'].isin(user_filter)]
            
            if action_filter:
                filtered_df = filtered_df[filtered_df['操作'].isin(action_filter)]
            
            # 显示日志表格
            st.dataframe(filtered_df, use_container_width=True)
            
            # 统计信息
            st.markdown("---")
            st.subheader("📊 日志统计")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("总操作数", len(logs_df))
            
            with col2:
                st.metric("活跃用户数", logs_df['用户'].nunique())
            
            with col3:
                st.metric("操作类型数", logs_df['操作'].nunique())
            
            # 下载日志
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 下载日志 (CSV)",
                data=csv,
                file_name=f"system_logs_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("暂无操作日志")
