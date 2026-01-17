# -*- coding: utf-8 -*-
"""
数据管理页面 - Data Administration
提供数据上传、采集模拟、数据清洗等功能
"""

import streamlit as st
import pandas as pd
import time
from utils.spark_processor import SparkDataManager
from utils.db_manager import DatabaseManager


def show_data_admin_page():
    """数据管理页面"""
    st.markdown('<div class="main-header">📁 数据采集与管理</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 初始化
    data_manager = SparkDataManager()
    db = DatabaseManager()
    
    # 选项卡
    tab1, tab2, tab3 = st.tabs(["📤 数据上传", "🔄 数据采集模拟", "📊 数据预览"])
    
    # Tab 1: 数据上传
    with tab1:
        st.subheader("手动上传 CSV 数据")
        st.info("上传的数据将追加到现有数据集，系统会自动去重。")
        
        uploaded_file = st.file_uploader(
            "选择 CSV 文件",
            type=['csv'],
            help="支持企业数据或个人数据格式"
        )
        
        if uploaded_file is not None:
            try:
                # 读取上传的文件
                new_df = pd.read_csv(uploaded_file)
                
                st.success(f"✓ 文件读取成功: {len(new_df)} 行, {len(new_df.columns)} 列")
                
                # 预览数据
                st.dataframe(new_df.head(10), use_container_width=True)
                
                # 选择目标数据集
                target_dataset = st.selectbox(
                    "追加到哪个数据集？",
                    ["data.csv (企业数据)", "german_credit_data.csv (个人数据)"]
                )
                
                if st.button("确认追加数据", type="primary"):
                    target_file = target_dataset.split()[0]
                    
                    with st.spinner("正在追加数据..."):
                        success = data_manager.append_data_to_csv(new_df, target_file)
                    
                    if success:
                        st.success("✅ 数据追加成功！")
                        
                        # 记录日志
                        if 'user' in st.session_state:
                            db.log_action(
                                st.session_state.user['username'],
                                "数据上传",
                                f"上传了 {len(new_df)} 条数据到 {target_file}"
                            )
                        
                        st.balloons()
                    else:
                        st.error("❌ 数据追加失败，请检查文件格式。")
            
            except Exception as e:
                st.error(f"文件读取失败: {str(e)}")
    
    # Tab 2: 数据采集模拟
    with tab2:
        st.subheader("模拟每日数据采集任务")
        st.info("模拟从网络爬取数据并使用 PySpark 进行清洗的过程。")
        
        col1, col2 = st.columns(2)
        
        with col1:
            data_source = st.selectbox(
                "数据源",
                ["企业财报API", "信贷数据接口", "第三方数据平台"]
            )
        
        with col2:
            data_count = st.number_input(
                "采集数量",
                min_value=10,
                max_value=1000,
                value=100,
                step=10
            )
        
        if st.button("🚀 执行数据采集任务", type="primary"):
            # 模拟采集过程
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            steps = [
                ("连接数据源...", 0.2),
                ("正在爬取数据...", 0.4),
                ("PySpark 数据清洗中...", 0.6),
                ("去重处理...", 0.8),
                ("保存到数据库...", 1.0)
            ]
            
            for step_name, progress in steps:
                status_text.text(f"⏳ {step_name}")
                progress_bar.progress(progress)
                time.sleep(0.8)
            
            status_text.text("✅ 数据采集完成！")
            
            # 显示采集结果
            st.success(f"""
            **采集任务完成**
            
            - 数据源: {data_source}
            - 采集数量: {data_count} 条
            - 去重后: {int(data_count * 0.95)} 条
            - 清洗耗时: 2.4 秒
            - 计算引擎: {data_manager.mode}
            """)
            
            # 记录日志
            if 'user' in st.session_state:
                db.log_action(
                    st.session_state.user['username'],
                    "数据采集",
                    f"从 {data_source} 采集了 {data_count} 条数据"
                )
            
            st.balloons()
    
    # Tab 3: 数据预览
    with tab3:
        st.subheader("数据集预览")
        
        dataset_choice = st.selectbox(
            "选择数据集",
            ["企业破产数据 (data.csv)", "个人信贷数据 (german_credit_data.csv)"]
        )
        
        try:
            if "企业" in dataset_choice:
                X, y = data_manager.load_corporate_data('data.csv')
                df = X.copy()
                df['Bankrupt?'] = y
            else:
                X, y, _ = data_manager.load_personal_data('german_credit_data.csv')
                df = X.copy()
                df['Risk'] = y
            
            st.info(f"数据集大小: {len(df)} 行 × {len(df.columns)} 列")
            
            # 数据统计
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("总记录数", f"{len(df):,}")
            
            with col2:
                st.metric("特征数", len(df.columns))
            
            with col3:
                missing_count = df.isnull().sum().sum()
                st.metric("缺失值", missing_count)
            
            # 数据表格
            st.dataframe(df.head(50), use_container_width=True)
            
            # 下载按钮
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 下载完整数据集 (CSV)",
                data=csv,
                file_name=f"dataset_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        except Exception as e:
            st.error(f"数据加载失败: {str(e)}")
