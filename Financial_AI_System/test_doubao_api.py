# -*- coding: utf-8 -*-
"""
测试豆包 API 真实调用
Test Doubao API with OpenAI SDK
"""

from core.llm_agent import DoubaoAgent
import pandas as pd
from utils.spark_processor import SparkDataManager


def test_api_connection():
    """测试 API 连接"""
    print("=" * 60)
    print("测试 1: API 连接测试")
    print("=" * 60)
    
    # 使用真实 API
    agent = DoubaoAgent(use_mock=False)
    
    if agent.use_mock:
        print("\n⚠️ 系统降级到 Mock 模式，无法测试真实 API")
        print("请确保:")
        print("1. 已安装 openai: pip install --upgrade 'openai>=1.0'")
        print("2. API Key 和 Endpoint ID 配置正确")
        return False
    
    print("\n✓ API 客户端初始化成功")
    print(f"✓ API Key: {agent.api_key[:20]}...")
    print(f"✓ Endpoint ID: {agent.endpoint_id}")
    
    return True


def test_simple_chat():
    """测试简单对话"""
    print("\n" + "=" * 60)
    print("测试 2: 简单对话测试")
    print("=" * 60)
    
    agent = DoubaoAgent(use_mock=False)
    
    if agent.use_mock:
        print("\n⚠️ 跳过测试（Mock 模式）")
        return
    
    try:
        print("\n发送请求: 你好")
        result = agent.chat("你好", stream=False)  # 明确指定 stream=False
        
        print(f"\n✓ API 调用成功!")
        print(f"AI 回答: {result['answer'][:100]}...")  # 只显示前100个字符
        print(f"显示图表: {result['show_chart']}")
        
    except Exception as e:
        print(f"\n❌ API 调用失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_chart_generation():
    """测试图表生成"""
    print("\n" + "=" * 60)
    print("测试 3: 图表生成测试")
    print("=" * 60)
    
    agent = DoubaoAgent(use_mock=False)
    
    if agent.use_mock:
        print("\n⚠️ 跳过测试（Mock 模式）")
        return
    
    try:
        # 加载数据
        data_manager = SparkDataManager()
        X_corp, y_corp = data_manager.load_corporate_data('data.csv')
        df = X_corp.copy()
        df['Bankrupt?'] = y_corp
        
        print(f"\n✓ 数据加载成功: {len(df)} 行")
        print(f"✓ 数据列: {df.columns.tolist()}")
        
        # 测试图表请求
        print("\n发送请求: 画出企业ROA的柱状图")
        result = agent.chat("画出企业ROA的柱状图", dataframe_context=df, stream=False)  # 明确指定 stream=False
        
        print(f"\n✓ API 调用成功!")
        print(f"AI 回答: {result['answer'][:100]}...")  # 只显示前100个字符
        print(f"显示图表: {result['show_chart']}")
        print(f"图表类型: {result['chart_type']}")
        print(f"数据列: {result['chart_col']}")
        
        if result['show_chart']:
            chart = agent.generate_chart(df, result['chart_type'], result['chart_col'])
            if chart:
                print(f"✓ 图表生成成功!")
            else:
                print(f"❌ 图表生成失败")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_mock_mode():
    """测试 Mock 模式（作为对比）"""
    print("\n" + "=" * 60)
    print("测试 4: Mock 模式对比测试")
    print("=" * 60)
    
    agent = DoubaoAgent(use_mock=True)
    
    print("\n发送请求: 你好")
    result = agent.chat("你好")
    
    print(f"\nMock 模式回答: {result['answer']}")
    print(f"显示图表: {result['show_chart']}")


if __name__ == "__main__":
    print("\n🚀 开始测试豆包 API (OpenAI SDK)...\n")
    
    try:
        # 测试 1: API 连接
        api_ok = test_api_connection()
        
        if api_ok:
            # 测试 2: 简单对话
            test_simple_chat()
            
            # 测试 3: 图表生成
            test_chart_generation()
        
        # 测试 4: Mock 模式对比
        test_mock_mode()
        
        print("\n" + "=" * 60)
        print("✅ 测试完成!")
        print("=" * 60)
        
        if api_ok:
            print("\n✓ 真实 API 测试通过")
            print("\n📝 下一步:")
            print("1. 运行 Streamlit 应用: streamlit run app.py")
            print("2. 登录系统 (admin/123456)")
            print("3. 进入 'AI智能问答' 页面")
            print("4. 在侧边栏切换到 '真实 API 模式'")
            print("5. 测试对话和图表生成功能")
        else:
            print("\n⚠️ 真实 API 测试未执行（降级到 Mock 模式）")
            print("\n📝 解决方法:")
            print("1. 安装 OpenAI SDK: pip install --upgrade 'openai>=1.0'")
            print("2. 检查 API Key 和 Endpoint ID 配置")
            print("3. 确认网络连接正常")
    
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
