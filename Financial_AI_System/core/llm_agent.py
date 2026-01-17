# -*- coding: utf-8 -*-
"""
AI 大模型智能分析引擎 - 豆包版本 (Volcengine Doubao)
接入火山引擎豆包大模型，实现真实的 AI 对话和图表生成
使用 OpenAI SDK 兼容接口
"""

import json
import re
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class DoubaoAgent:
    """豆包 AI 智能分析引擎（基于 OpenAI SDK）"""
    
    def __init__(self, api_key=None, endpoint_id=None, model_name=None, use_mock=False):
        """
        初始化豆包 AI 引擎
        
        Args:
            api_key: 火山引擎 ARK API Key (必填)
            endpoint_id: 豆包推理接入点 ID (必填，格式: ep-20260117181412-r9r6m)
            model_name: 模型名称 (默认: deepseekapiv3.2)
            use_mock: 是否使用 Mock 模式 (默认 False)
        """
        self.api_key = api_key or "117aeeb4-df58-4e55-bebd-1e5aeab6a1e4"  # 🔑 您的 API Key
        self.endpoint_id = endpoint_id or "ep-20260117181412-r9r6m"  # 🔑 您的 Endpoint ID
        self.model_name = model_name or "deepseekapiv3.2"  # 🔑 模型名称
        self.use_mock = use_mock
        
        # 初始化客户端
        if not use_mock:
            try:
                from openai import OpenAI
                
                self.client = OpenAI(
                    base_url='https://ark.cn-beijing.volces.com/api/v3',
                    api_key=self.api_key
                )
                print("✓ 豆包 AI 引擎已启动: 真实 API 模式 (OpenAI SDK)")
                print(f"✓ Model: {self.model_name}")
                print(f"✓ Endpoint ID: {self.endpoint_id}")
            except ImportError:
                print("⚠️ openai 库未安装，降级使用 Mock 模式")
                print("   安装命令: pip install --upgrade 'openai>=1.0'")
                self.use_mock = True
            except Exception as e:
                print(f"⚠️ 豆包 API 初始化失败: {str(e)}")
                print("   降级使用 Mock 模式")
                self.use_mock = True
        
        if self.use_mock:
            print("✓ AI 引擎已启动: Mock 模拟模式")
    
    def chat(self, query, dataframe_context=None, stream=False):
        """
        智能对话接口 (支持数据上下文和图表生成)
        
        Args:
            query: 用户查询
            dataframe_context: DataFrame 上下文 (可选)
            stream: 是否流式输出 (默认 False)
            
        Returns:
            dict: {
                'answer': str,           # 文本回答
                'show_chart': bool,      # 是否显示图表
                'chart_type': str,       # 图表类型 ('bar'|'line'|'pie'|'scatter'|null)
                'chart_col': str,        # 数据列名
                'raw_response': str      # 原始响应
            }
            或 generator (当 stream=True 时)
        """
        if self.use_mock:
            return self._mock_chat(query, dataframe_context)
        else:
            # 确保 stream 参数正确传递
            result = self._real_chat(query, dataframe_context, stream=stream)
            return result
    
    def _build_system_prompt(self, dataframe_context=None):
        """构建系统提示词"""
        base_prompt = """你是一个专业的金融数据分析助手，擅长数据分析和可视化。

你的任务是：
1. 理解用户的问题
2. 提供专业的分析回答
3. 判断是否需要生成图表来辅助说明

**重要规则**：
- 你必须以 JSON 格式返回结果
- JSON 格式如下：
```json
{
    "answer": "你的文本回答",
    "show_chart": true/false,
    "chart_type": "bar/line/pie/scatter/null",
    "chart_col": "数据列名或null"
}
```

**图表生成规则**：
- 当用户要求"画图"、"可视化"、"展示图表"、"分析趋势"时，设置 show_chart=true
- 根据数据类型选择合适的图表类型：
  - bar: 柱状图，适合比较不同类别
  - line: 折线图，适合展示趋势
  - pie: 饼图，适合展示占比
  - scatter: 散点图，适合展示相关性
- chart_col 应该是数据中存在的列名
"""
        
        if dataframe_context is not None:
            columns = dataframe_context.columns.tolist()
            sample_data = dataframe_context.head(3).to_dict('records')
            
            context_info = f"""

**当前数据上下文**：
- 数据列: {', '.join(columns)}
- 数据样例: {json.dumps(sample_data, ensure_ascii=False, indent=2)}
- 数据行数: {len(dataframe_context)}

请基于这些数据回答用户问题。
"""
            base_prompt += context_info
        
        return base_prompt
    
    def _real_chat(self, query, dataframe_context=None, stream=False):
        """真实 API 调用（使用 OpenAI SDK 兼容接口）"""
        if stream:
            return self._real_chat_stream(query, dataframe_context)
        else:
            return self._real_chat_normal(query, dataframe_context)
    
    def _real_chat_normal(self, query, dataframe_context=None):
        """非流式 API 调用"""
        try:
            # 构建消息
            system_prompt = self._build_system_prompt(dataframe_context)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            # 调用 API
            response = self.client.chat.completions.create(
                model=self.endpoint_id,  # 使用 endpoint_id 作为 model
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content
            
            # 解析响应
            result = self._parse_response(response_text)
            return result
        
        except Exception as e:
            print(f"豆包 API 调用失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'answer': f"抱歉，AI 服务暂时不可用。错误信息: {str(e)}",
                'show_chart': False,
                'chart_type': None,
                'chart_col': None,
                'raw_response': ''
            }
    
    def _real_chat_stream(self, query, dataframe_context=None):
        """流式 API 调用"""
        try:
            # 构建消息
            system_prompt = self._build_system_prompt(dataframe_context)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            # 调用 API - 流式输出
            response_text = ""
            stream_response = self.client.chat.completions.create(
                model=self.endpoint_id,  # 使用 endpoint_id 作为 model
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                stream=True
            )
            
            for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    response_text += content
                    yield content
            
            # 解析最终结果
            result = self._parse_response(response_text)
            yield result
        
        except Exception as e:
            print(f"豆包 API 调用失败: {str(e)}")
            import traceback
            traceback.print_exc()
            yield {
                'answer': f"抱歉，AI 服务暂时不可用。错误信息: {str(e)}",
                'show_chart': False,
                'chart_type': None,
                'chart_col': None,
                'raw_response': ''
            }
    
    def _parse_response(self, response_text):
        """解析 AI 响应"""
        try:
            # 尝试提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                return {
                    'answer': data.get('answer', response_text),
                    'show_chart': data.get('show_chart', False),
                    'chart_type': data.get('chart_type'),
                    'chart_col': data.get('chart_col'),
                    'raw_response': response_text
                }
            else:
                # 如果没有 JSON，返回纯文本
                return {
                    'answer': response_text,
                    'show_chart': False,
                    'chart_type': None,
                    'chart_col': None,
                    'raw_response': response_text
                }
        
        except Exception as e:
            print(f"响应解析失败: {str(e)}")
            return {
                'answer': response_text,
                'show_chart': False,
                'chart_type': None,
                'chart_col': None,
                'raw_response': response_text
            }
    
    def _mock_chat(self, query, dataframe_context=None):
        """Mock 模式 (用于测试)"""
        query_lower = query.lower()
        
        # 判断是否需要图表
        chart_keywords = ['画', '绘制', '图', 'chart', 'plot', '可视化', '展示图表', '趋势']
        show_chart = any(kw in query_lower for kw in chart_keywords)
        
        # 判断图表类型
        chart_type = None
        chart_col = None
        
        if show_chart and dataframe_context is not None:
            # 选择图表类型
            if '柱状图' in query_lower or 'bar' in query_lower:
                chart_type = 'bar'
            elif '折线图' in query_lower or 'line' in query_lower or '趋势' in query_lower:
                chart_type = 'line'
            elif '饼图' in query_lower or 'pie' in query_lower:
                chart_type = 'pie'
            elif '散点图' in query_lower or 'scatter' in query_lower:
                chart_type = 'scatter'
            else:
                chart_type = 'bar'  # 默认
            
            # 选择数据列
            numeric_cols = dataframe_context.select_dtypes(include=['float64', 'int64']).columns.tolist()
            
            if 'roa' in query_lower and 'ROA' in dataframe_context.columns:
                chart_col = 'ROA'
            elif '负债' in query_lower or 'debt' in query_lower:
                chart_col = 'Debt_Ratio' if 'Debt_Ratio' in dataframe_context.columns else numeric_cols[0]
            elif '净收入' in query_lower:
                chart_col = 'Net_Income_Ratio' if 'Net_Income_Ratio' in dataframe_context.columns else numeric_cols[0]
            else:
                chart_col = numeric_cols[0] if numeric_cols else None
        
        # 生成回答
        if show_chart:
            answer = f"好的，我为您生成了 {chart_col} 的{chart_type}图表。从数据中可以看出，该指标的分布情况如图所示。"
        else:
            # 普通对话
            if '你好' in query_lower or 'hello' in query_lower:
                answer = "您好！我是豆包 AI 金融分析助手。我可以帮您分析数据、生成图表、回答问题。请问有什么可以帮您？"
            elif '帮助' in query_lower or 'help' in query_lower:
                answer = """
我可以帮您完成以下任务：

📊 **数据分析**：
- "分析一下企业的财务状况"
- "ROA 指标的含义是什么"

📈 **图表生成**：
- "画出 ROA 的柱状图"
- "展示负债率的趋势图"

💬 **智能问答**：
- 回答金融相关问题
- 提供专业建议

请直接输入您的需求！
                """
            else:
                answer = f"我理解您想了解「{query}」。基于当前数据，我建议您可以尝试更具体的问题，或者要求我生成相关图表来辅助分析。"
        
        return {
            'answer': answer,
            'show_chart': show_chart,
            'chart_type': chart_type,
            'chart_col': chart_col,
            'raw_response': answer
        }
    
    def generate_chart(self, data_df, chart_type, chart_col):
        """
        生成图表
        
        Args:
            data_df: 数据 DataFrame
            chart_type: 图表类型
            chart_col: 数据列名
            
        Returns:
            plotly.graph_objects.Figure: 图表对象
        """
        try:
            if chart_col not in data_df.columns:
                return None
            
            # 限制数据量
            plot_df = data_df.head(20)
            
            if chart_type == 'bar':
                fig = px.bar(
                    plot_df,
                    y=chart_col,
                    title=f"{chart_col} 柱状图",
                    labels={chart_col: chart_col}
                )
            
            elif chart_type == 'line':
                fig = px.line(
                    plot_df,
                    y=chart_col,
                    title=f"{chart_col} 趋势图",
                    labels={chart_col: chart_col}
                )
            
            elif chart_type == 'pie':
                # 饼图需要分组
                value_counts = data_df[chart_col].value_counts().head(10)
                fig = px.pie(
                    values=value_counts.values,
                    names=value_counts.index,
                    title=f"{chart_col} 分布饼图"
                )
            
            elif chart_type == 'scatter':
                numeric_cols = data_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                if len(numeric_cols) >= 2:
                    fig = px.scatter(
                        plot_df,
                        x=numeric_cols[0],
                        y=chart_col,
                        title=f"{numeric_cols[0]} vs {chart_col} 散点图"
                    )
                else:
                    return None
            
            else:
                return None
            
            fig.update_layout(height=400)
            return fig
        
        except Exception as e:
            print(f"图表生成失败: {str(e)}")
            return None
    
    def generate_analysis_report(self, risk_score, risk_type, input_features):
        """
        生成风险分析报告 (保留原有功能)
        
        Args:
            risk_score: 风险评分 (0-1)
            risk_type: 风险类型 ('corporate' or 'personal')
            input_features: 输入特征字典
            
        Returns:
            str: AI 生成的分析报告
        """
        risk_percentage = risk_score * 100
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 构建 Prompt
        if risk_type == 'corporate':
            prompt = f"""
请作为专业的金融风险分析师，分析以下企业的破产风险：

**风险评分**: {risk_percentage:.1f}%
**财务指标**:
- ROA (资产回报率): {input_features.get('ROA', 0):.3f}
- 负债比率: {input_features.get('Debt_Ratio', 0):.1%}
- 净收入比率: {input_features.get('Net_Income_Ratio', 0):.3f}
- 毛利率: {input_features.get('Gross_Margin', 0):.1%}
- 流动负债比率: {input_features.get('Liability_Assets_Ratio', 0):.1%}

请提供：
1. 风险等级判定
2. 核心指标分析
3. 风险因素识别
4. 投资建议

要求：专业、简洁、可操作。
            """
        else:
            prompt = f"""
请作为专业的信贷审批专家，分析以下个人的信贷违约风险：

**风险评分**: {risk_percentage:.1f}%
**申请人信息**:
- 年龄: {input_features.get('Age', 0)} 岁
- 信贷金额: {input_features.get('Credit_amount', 0):,.0f} 元
- 贷款期限: {input_features.get('Duration', 0)} 个月

请提供：
1. 风险等级判定
2. 申请人画像分析
3. 审批建议

要求：专业、简洁、可操作。
            """
        
        # 如果是真实 API，调用豆包
        if not self.use_mock:
            try:
                result = self.chat(prompt)
                return result['answer']
            except:
                pass
        
        # Mock 模式或 API 失败时的降级处理
        return self._generate_mock_report(risk_score, risk_type, input_features)
    
    def _generate_mock_report(self, risk_score, risk_type, input_features):
        """Mock 报告生成 (降级方案)"""
        risk_percentage = risk_score * 100
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if risk_type == 'corporate':
            roa = input_features.get('ROA', 0)
            debt_ratio = input_features.get('Debt_Ratio', 0)
            
            if risk_score > 0.7:
                return f"""
🚨 **高风险预警**

**分析时间**: {current_time}  
**风险等级**: 🔴 极高风险 ({risk_percentage:.1f}%)

### 核心指标诊断
- ROA: {roa:.3f} {'⚠️ 偏低' if roa < 0.3 else '✓ 尚可'}
- 负债比率: {debt_ratio:.1%} {'🔴 过高' if debt_ratio > 0.5 else '⚠️ 偏高'}

### AI 建议
🚫 **不建议投资**：破产风险高达 {risk_percentage:.1f}%，建议规避。
"""
            else:
                return f"""
✅ **低风险优质标的**

**分析时间**: {current_time}  
**风险等级**: 🟢 低风险 ({risk_percentage:.1f}%)

### 核心指标诊断
- ROA: {roa:.3f} ✨ 优秀
- 负债比率: {debt_ratio:.1%} ✓ 合理

### AI 建议
✅ **推荐投资**：财务稳健，违约风险仅 {risk_percentage:.1f}%。
"""
        else:
            age = input_features.get('Age', 0)
            
            if risk_score > 0.7:
                return f"""
🚨 **高违约风险**

**风险等级**: 🔴 高风险 ({risk_percentage:.1f}%)

### 申请人画像
- 年龄: {age} 岁

### AI 建议
🚫 **不建议批准**：违约概率 {risk_percentage:.1f}%，风险过高。
"""
            else:
                return f"""
✅ **优质客户**

**风险等级**: 🟢 低风险 ({risk_percentage:.1f}%)

### 申请人画像
- 年龄: {age} 岁

### AI 建议
✅ **推荐批准**：违约风险仅 {risk_percentage:.1f}%，可快速批准。
"""


# 向后兼容：保留 FinancialLLM 类名
class FinancialLLM(DoubaoAgent):
    """向后兼容的类名"""
    pass
