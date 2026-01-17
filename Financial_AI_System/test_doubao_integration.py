# -*- coding: utf-8 -*-
"""
测试豆包 AI 集成
Test Doubao AI Integration
"""

import pandas as pd
from core.llm_agent import DoubaoAgent
from utils.spark_processor import SparkDataManager


def test_basic_chat():
    """测试基本对话功能"""
    print("=" * 60)
    print("测试 1: 基本对话功能")
    print("=" * 60)
    
    agent = DoubaoAgent(use_mock=True)
    
    # 测试问候
    result = agent.chat("你好")
    print(f"\n用户: 你好")
    print(f"AI: {result['answer']}")
    print(f"显示图表: {result['show_chart']}")
    
    # 测试帮助
    result = agent.chat("帮助")
    print(f"\n用户: 帮助")
    print(f"AI: {result['answer']}")
    print(f"显示图表: {result['show_chart']}")


def test_chart_generation():
    """测试图表生成功能"""
    print("\n" + "=" * 60)
    print("测试 2: 图表生成功能")
    print("=" * 60)
    
    agent = DoubaoAgent(use_mock=True)
    
    # 加载数据
    try:
        data_manager = SparkDataManager()
        X_corp, y_corp = data_manager.load_corporate_data('data.csv')
        df = X_corp.copy()
        df['Bankrupt?'] = y_corp
        
        print(f"\n数据加载成功: {len(df)} 行, {len(df.columns)} 列")
        print(f"列名: {df.columns.tolist()}")
        
        # 测试图表请求
        queries = [
            "画出企业ROA的柱状图",
            "绘制负债率的折线图",
            "展示净收入的饼图"
        ]
        
        for query in queries:
            result = agent.chat(query, dataframe_context=df)
            print(f"\n用户: {query}")
            print(f"AI: {result['answer']}")
            print(f"显示图表: {result['show_chart']}")
            print(f"图表类型: {result['chart_type']}")
            print(f"数据列: {result['chart_col']}")
            
            if result['show_chart']:
                chart = agent.generate_chart(df, result['chart_type'], result['chart_col'])
                if chart:
                    print(f"✅ 图表生成成功!")
                else:
                    print(f"❌ 图表生成失败")
    
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")


def test_data_context():
    """测试数据上下文传递"""
    print("\n" + "=" * 60)
    print("测试 3: 数据上下文传递")
    print("=" * 60)
    
    agent = DoubaoAgent(use_mock=True)
    
    # 创建测试数据
    test_df = pd.DataFrame({
        'ROA': [0.5, 0.3, 0.7, 0.2],
        'Debt_Ratio': [0.3, 0.5, 0.2, 0.6],
        'Net_Income_Ratio': [0.1, 0.05, 0.15, 0.03]
    })
    
    print(f"\n测试数据:")
    print(test_df)
    
    # 测试带上下文的对话
    result = agent.chat("分析一下这些企业的财务状况", dataframe_context=test_df)
    print(f"\n用户: 分析一下这些企业的财务状况")
    print(f"AI: {result['answer']}")


def test_report_generation():
    """测试风险报告生成"""
    print("\n" + "=" * 60)
    print("测试 4: 风险报告生成")
    print("=" * 60)
    
    agent = DoubaoAgent(use_mock=True)
    
    # 测试企业风险报告
    corporate_features = {
        'ROA': 0.15,
        'Debt_Ratio': 0.65,
        'Net_Income_Ratio': 0.05,
        'Gross_Margin': 0.25,
        'Liability_Assets_Ratio': 0.45
    }
    
    report = agent.generate_analysis_report(0.85, 'corporate', corporate_features)
    print(f"\n企业风险报告 (风险分: 85%):")
    print(report)
    
    # 测试个人风险报告
    personal_features = {
        'Age': 35,
        'Credit_amount': 5000,
        'Duration': 24
    }
    
    report = agent.generate_analysis_report(0.25, 'personal', personal_features)
    print(f"\n个人风险报告 (风险分: 25%):")
    print(report)


if __name__ == "__main__":
    print("\n🚀 开始测试豆包 AI 集成...\n")
    
    try:
        test_basic_chat()
        test_chart_generation()
        test_data_context()
        test_report_generation()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成!")
        print("=" * 60)
        
        print("\n📝 下一步:")
        print("1. 运行 Streamlit 应用: streamlit run app.py")
        print("2. 登录系统 (admin/123456)")
        print("3. 进入 'AI智能问答' 页面")
        print("4. 测试对话和图表生成功能")
        print("5. 如需使用真实 API，请在 core/llm_agent.py 中填写:")
        print("   - ARK_API_KEY (此处填写你的Key)")
        print("   - ENDPOINT_ID (此处填写你的Key)")
        print("   然后在侧边栏切换到 '真实 API 模式'")
    
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
