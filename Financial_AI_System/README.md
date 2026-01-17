# 金融智能分析系统 - 本科毕业设计

**基于 AI 大模型与大数据技术的智能风控平台**

---

## 📋 项目简介

本系统是一个完整的金融风险评估解决方案，采用**大数据处理 + 机器学习 + AI 大模型**的技术架构，提供两大核心功能：

1. **企业风险评估 (B-Side)**: 基于台湾经济期刊破产数据，预测企业破产风险
2. **个人信贷评估 (C-Side)**: 基于德国信贷数据，预测个人信贷违约风险

### 🎯 核心亮点

- ✅ **大数据处理**: 集成 PySpark 分布式计算引擎，支持大规模数据处理
- ✅ **智能降级**: 自动检测 Java 环境，无 PySpark 时降级使用 Pandas
- ✅ **AI 智能分析**: 集成 AI 大模型生成专业的金融分析报告
- ✅ **高级可视化**: 使用 Plotly 绘制仪表盘、旭日图等高级图表
- ✅ **现代化 UI**: 基于 Streamlit + streamlit-option-menu 的美观界面

---

## 🛠️ 技术栈

### 核心技术

| 技术领域 | 技术选型 | 说明 |
|---------|---------|------|
| **开发语言** | Python 3.9+ | 主流数据科学语言 |
| **大数据引擎** | PySpark 3.4+ | 分布式数据处理 |
| **前端框架** | Streamlit + streamlit-option-menu | 快速构建数据应用 |
| **机器学习** | Scikit-learn (RandomForest) | 经典集成学习算法 |
| **AI 大模型** | OpenAI/DeepSeek API | 智能分析报告生成 |
| **可视化** | Plotly Express + Graph Objects | 交互式图表 |
| **数据处理** | Pandas + Numpy | 数据清洗与特征工程 |

---

## 📁 项目结构

```
.
├── data.csv                          # 台湾企业破产数据集 (6,819 条)
├── german_credit_data.csv            # 德国个人信贷数据集 (1,000 条)
├── requirements.txt                  # 依赖包列表
├── README.md                         # 项目说明文档
│
├── utils/
│   └── spark_processor.py            # 🔥 PySpark 大数据处理模块 (核心)
│
├── core/
│   ├── model_factory.py              # 模型训练和预测引擎
│   └── llm_agent.py                  # 🤖 AI 大模型智能分析引擎
│
├── app.py                            # 🎨 Streamlit 主应用 (高级 UI)
│
└── models/                           # 模型文件目录 (自动生成)
    ├── corporate_model.pkl           # 企业风险模型
    ├── personal_model.pkl            # 个人信贷模型
    └── encoders.pkl                  # 特征编码器
```

---

## 🚀 快速开始

### 1. 环境准备

#### 方式一：完整安装 (推荐用于演示)

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Java (PySpark 依赖)
# Windows: 下载 JDK 8/11 并配置 JAVA_HOME
# macOS: brew install openjdk@11
# Linux: sudo apt install openjdk-11-jdk
```

#### 方式二：轻量安装 (无 Java 环境)

```bash
# 只安装基础依赖 (系统会自动降级使用 Pandas)
pip install streamlit streamlit-option-menu pandas numpy scikit-learn plotly joblib
```

### 2. 训练模型

有两种方式训练模型：

**方式一：命令行训练**
```bash
python core/model_factory.py
```

**方式二：在 Web 界面训练**
- 启动应用后，在侧边栏点击「重新训练模型」按钮

### 3. 启动应用

```bash
streamlit run app.py
```

应用将在浏览器中自动打开 (默认地址: http://localhost:8501)

---

## 📊 数据集说明

### 1. 企业破产数据 (data.csv)

- **来源**: Taiwan Economic Journal (1999-2009)
- **样本数**: 6,819 家企业
- **原始特征数**: 95 个财务指标
- **目标变量**: Bankrupt? (0=正常, 1=破产)

**选用的 5 个核心特征**:
1. **ROA** - 资产回报率 (盈利能力指标)
2. **Debt_Ratio** - 负债比率 (偿债能力指标)
3. **Net_Income_Ratio** - 净收入比率 (盈利质量指标)
4. **Gross_Margin** - 毛利率 (经营效率指标)
5. **Liability_Assets_Ratio** - 流动负债比率 (短期偿债能力)

### 2. 个人信贷数据 (german_credit_data.csv)

- **来源**: German Credit Risk Dataset
- **样本数**: 1,000 个信贷申请
- **原始特征数**: 21 个个人和信贷特征
- **目标变量**: Risk (good=低风险, bad=高风险)

**选用的 5 个核心特征**:
1. **Age** - 年龄 (还款能力相关)
2. **Credit_amount** - 信贷金额 (风险敞口)
3. **Duration** - 贷款期限 (风险累积时间)
4. **Sex** - 性别 (人口统计学特征)
5. **Housing** - 住房情况 (资产状况)

---

## 🎯 功能模块

### 1. 数据驾驶舱 (Dashboard)

**核心功能**:
- 📊 实时显示系统计算引擎状态 (PySpark/Pandas)
- 📈 三个并排的仪表盘图表展示风险指数
- 🌅 旭日图展示风险层级构成
- 💡 系统关键指标监控

**技术实现**:
- 使用 `plotly.graph_objects.Indicator` 绘制仪表盘
- 使用 `plotly.express.sunburst` 绘制旭日图
- 实时计算企业和个人风险率

### 2. 企业风险评估 (B-Side)

**核心功能**:
- 📝 输入 5 个财务指标
- 🤖 RandomForest 模型预测破产概率
- 📊 大型仪表盘可视化风险评分
- 🧠 AI 大模型生成专业分析报告

**AI 分析报告内容**:
- 风险等级判定 (高/中/低)
- 核心指标诊断
- 风险因素识别
- 投资建议 (是否投资/放贷)

### 3. 个人信贷评估 (C-Side)

**核心功能**:
- 📝 输入个人基本信息和信贷信息
- 🤖 RandomForest 模型预测违约概率
- 📊 大型仪表盘可视化风险评分
- 🧠 AI 大模型生成专业审批建议

**AI 分析报告内容**:
- 申请人画像分析
- 风险因素识别
- 审批建议 (批准/拒绝/附条件批准)
- 风控措施建议

---

## 🔧 核心模块详解

### 1. `utils/spark_processor.py` - 大数据处理模块

**核心特性**:
- ✅ 自动检测 PySpark 环境
- ✅ 启动失败时自动降级使用 Pandas
- ✅ 统一的数据处理接口
- ✅ 支持分布式数据清洗和特征工程

**关键代码**:
```python
class SparkDataManager:
    def __init__(self):
        # 尝试初始化 Spark
        try:
            self.spark = SparkSession.builder \
                .appName("FinancialAnalysisSystem") \
                .master("local[*]") \
                .getOrCreate()
            self.mode = "PySpark"
        except:
            self.mode = "Pandas"  # 降级
```

### 2. `core/llm_agent.py` - AI 智能分析引擎

**核心特性**:
- ✅ Mock 模式：预设高质量分析模板
- ✅ API 模式：支持 OpenAI/DeepSeek 真实调用
- ✅ 根据风险分数智能生成报告
- ✅ 专业的金融分析师文风

**Mock 模式优势**:
- 无需 API Key，开箱即用
- 响应速度快，演示稳定
- 报告质量高，逻辑清晰

**切换至 API 模式**:
```python
llm = FinancialLLM(
    api_key="your-api-key",
    use_mock=False
)
```

### 3. `app.py` - 高级 UI 主程序

**核心特性**:
- ✅ 使用 `streamlit-option-menu` 创建图标导航
- ✅ 自定义 CSS 样式美化界面
- ✅ Plotly 仪表盘和旭日图
- ✅ 响应式布局设计

---

## 📈 模型性能

### 训练配置

```python
RandomForestClassifier(
    n_estimators=100,      # 100 棵决策树
    max_depth=10,          # 最大深度 10
    min_samples_split=5,   # 最小分裂样本数
    random_state=42,       # 随机种子
    n_jobs=-1              # 并行计算
)
```

### 性能指标

| 模型 | 准确率 | 数据集大小 | 训练时间 |
|-----|-------|----------|---------|
| 企业破产风险模型 | ~96% | 6,819 条 | ~2 秒 |
| 个人信贷风险模型 | ~68% | 1,000 条 | ~1 秒 |

---

## ⚙️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                    │
│  (数据驾驶舱 | 企业风险评估 | 个人信贷评估)                │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  Business Logic Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ ModelEngine  │  │  LLM Agent   │  │ SparkManager │  │
│  │ (模型预测)    │  │ (AI 分析)     │  │ (数据处理)    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Data Processing Layer                  │
│  ┌──────────────┐                    ┌──────────────┐  │
│  │   PySpark    │  ←─ 自动降级 ─→    │    Pandas    │  │
│  │ (分布式处理)  │                    │  (本地处理)   │  │
│  └──────────────┘                    └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                      Data Layer                          │
│     data.csv (企业数据)  |  german_credit_data.csv      │
└─────────────────────────────────────────────────────────┘
```

---

## 🐛 故障排除

### 问题 1: PySpark 启动失败

**现象**:
```
⚠️ PySpark 初始化失败
⚠️ 正在使用本地轻量模式 (Pandas)
```

**原因**: 未安装 Java 或 JAVA_HOME 未配置

**解决方案**:
1. 安装 JDK 8 或 11
2. 配置环境变量 `JAVA_HOME`
3. 重启终端和应用

**注意**: 系统会自动降级使用 Pandas，不影响功能使用

### 问题 2: 模型文件不存在

**现象**:
```
⚠️ 模型文件未找到，请先训练模型
```

**解决方案**:
- 方式一: 运行 `python core/model_factory.py`
- 方式二: 在 Web 界面点击「重新训练模型」按钮

### 问题 3: streamlit-option-menu 未安装

**现象**:
```
ModuleNotFoundError: No module named 'streamlit_option_menu'
```

**解决方案**:
```bash
pip install streamlit-option-menu
```

---

## 📝 开发者信息

- **项目类型**: 本科毕业设计
- **开发语言**: Python 3.9+
- **开发周期**: 2024 年
- **技术难点**: 
  - PySpark 大数据处理与自动降级
  - AI 大模型集成与 Mock 模拟
  - Plotly 高级可视化图表
  - Streamlit 高级 UI 设计

---

## 📄 许可证

本项目仅用于教育和学习目的。

---

## 🙏 致谢

- 数据集来源: UCI Machine Learning Repository
- 技术支持: Streamlit, PySpark, Scikit-learn, Plotly
- AI 模型: OpenAI, DeepSeek

---

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 📧 Email: [your-email@example.com]
- 🌐 GitHub: [your-github-profile]

---

**祝您使用愉快! 🎉**

---

## 附录: 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 训练模型
python core/model_factory.py

# 启动应用
streamlit run app.py

# 查看 PySpark 版本
pyspark --version

# 测试 Java 环境
java -version
```
