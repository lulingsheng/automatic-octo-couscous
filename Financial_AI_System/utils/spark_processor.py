# -*- coding: utf-8 -*-
"""
大数据处理模块 - PySpark Data Processor
负责使用 PySpark 进行大规模数据清洗和特征工程
带有自动降级保护机制
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os
import warnings
warnings.filterwarnings('ignore')

# 尝试导入 PySpark，如果失败则降级使用 Pandas
SPARK_AVAILABLE = False
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, when
    from pyspark.sql.types import DoubleType
    SPARK_AVAILABLE = True
    print("✓ PySpark 环境检测成功")
except Exception as e:
    print(f"⚠️  PySpark 初始化失败: {str(e)}")
    print("⚠️  正在使用本地轻量模式 (Pandas)")


class SparkDataManager:
    """大数据管理器 - 支持 PySpark 和 Pandas 双模式"""
    
    def __init__(self):
        self.spark = None
        self.mode = "Pandas"  # 默认模式
        
        # 尝试初始化 Spark
        if SPARK_AVAILABLE:
            try:
                self.spark = SparkSession.builder \
                    .appName("FinancialAnalysisSystem") \
                    .master("local[*]") \
                    .config("spark.driver.memory", "2g") \
                    .config("spark.sql.shuffle.partitions", "4") \
                    .getOrCreate()
                
                # 设置日志级别
                self.spark.sparkContext.setLogLevel("ERROR")
                self.mode = "PySpark"
                print(f"✓ 计算引擎已启动: {self.mode} (分布式模式)")
            except Exception as e:
                print(f"⚠️  Spark 启动失败: {str(e)}")
                print("⚠️  降级使用 Pandas 本地模式")
                self.spark = None
                self.mode = "Pandas"
        else:
            print(f"✓ 计算引擎已启动: {self.mode} (本地模式)")
    
    def get_engine_info(self):
        """获取当前计算引擎信息"""
        return {
            "engine": self.mode,
            "status": "运行中",
            "description": "分布式大数据引擎" if self.mode == "PySpark" else "本地轻量引擎"
        }
    
    def append_data_to_csv(self, new_data_df, target_file='data.csv'):
        """
        追加新数据到现有数据集
        
        Args:
            new_data_df: 新数据 DataFrame
            target_file: 目标文件路径
        """
        try:
            import pandas as pd
            
            # 读取现有数据
            existing_df = pd.read_csv(target_file)
            
            # 合并数据
            combined_df = pd.concat([existing_df, new_data_df], ignore_index=True)
            
            # 去重
            combined_df = combined_df.drop_duplicates()
            
            # 保存
            combined_df.to_csv(target_file, index=False)
            
            print(f"✓ 数据追加成功: 新增 {len(new_data_df)} 条，去重后总计 {len(combined_df)} 条")
            return True
        except Exception as e:
            print(f"✗ 数据追加失败: {str(e)}")
            return False
    
    def clean_data_with_spark(self, df_spark):
        """
        使用 PySpark 进行数据清洗
        
        Args:
            df_spark: Spark DataFrame
            
        Returns:
            Spark DataFrame: 清洗后的数据
        """
        # 去重
        df_spark = df_spark.dropDuplicates()
        
        # 填充缺失值 (数值列用均值，字符串列用 'Unknown')
        for col_name, col_type in df_spark.dtypes:
            if col_type in ['int', 'double', 'float']:
                mean_val = df_spark.select(col_name).na.drop().agg({col_name: "mean"}).collect()[0][0]
                if mean_val:
                    df_spark = df_spark.fillna({col_name: mean_val})
            else:
                df_spark = df_spark.fillna({col_name: 'Unknown'})
        
        return df_spark
    
    def load_corporate_data(self, filepath='data.csv'):
        """
        加载企业破产数据 (Taiwan Economic Journal)
        使用 PySpark 进行大数据处理
        
        Args:
            filepath: CSV文件路径
            
        Returns:
            X: 特征数据 (Pandas DataFrame)
            y: 目标变量 (Pandas Series)
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"找不到文件: {filepath}")
        
        print(f"\n[企业数据] 使用 {self.mode} 引擎加载数据...")
        
        if self.mode == "PySpark" and self.spark:
            # PySpark 模式
            try:
                # 读取数据
                df_spark = self.spark.read.csv(
                    filepath, 
                    header=True, 
                    inferSchema=True
                )
                
                print(f"✓ 数据加载完成: {df_spark.count()} 行")
                
                # 定义特征映射
                feature_mapping = {
                    'ROA(C) before interest and depreciation before interest': 'ROA',
                    'Debt ratio %': 'Debt_Ratio',
                    'Net Income to Total Assets': 'Net_Income_Ratio',
                    'Operating Gross Margin': 'Gross_Margin',
                    'Current Liability to Assets': 'Liability_Assets_Ratio'
                }
                
                # 选择特征列
                selected_cols = list(feature_mapping.keys()) + ['Bankrupt?']
                df_spark = df_spark.select(*selected_cols)
                
                # 重命名列
                for old_name, new_name in feature_mapping.items():
                    df_spark = df_spark.withColumnRenamed(old_name, new_name)
                
                # 处理缺失值 (使用均值填充)
                feature_cols = list(feature_mapping.values())
                for col_name in feature_cols:
                    mean_val = df_spark.select(col_name).na.drop().agg({col_name: "mean"}).collect()[0][0]
                    df_spark = df_spark.fillna({col_name: mean_val})
                
                # 转换为 Pandas
                df_pandas = df_spark.toPandas()
                
                X = df_pandas[feature_cols]
                y = df_pandas['Bankrupt?']
                
                print(f"✓ 特征工程完成: {len(feature_cols)} 个特征")
                return X, y
                
            except Exception as e:
                print(f"⚠️  PySpark 处理失败，降级使用 Pandas: {str(e)}")
                self.mode = "Pandas"
        
        # Pandas 模式 (降级或默认)
        df = pd.read_csv(filepath)
        
        feature_mapping = {
            'ROA(C) before interest and depreciation before interest': 'ROA',
            'Debt ratio %': 'Debt_Ratio',
            'Net Income to Total Assets': 'Net_Income_Ratio',
            'Operating Gross Margin': 'Gross_Margin',
            'Current Liability to Assets': 'Liability_Assets_Ratio'
        }
        
        # 查找匹配的列名 (支持模糊匹配)
        selected_cols = []
        rename_dict = {}
        
        for original_name, new_name in feature_mapping.items():
            # 精确匹配
            if original_name in df.columns:
                selected_cols.append(original_name)
                rename_dict[original_name] = new_name
            else:
                # 模糊匹配 - 查找包含关键词的列
                found = False
                for col in df.columns:
                    if 'ROA(C)' in col and new_name == 'ROA':
                        selected_cols.append(col)
                        rename_dict[col] = new_name
                        found = True
                        break
                    elif 'Debt ratio' in col and new_name == 'Debt_Ratio':
                        selected_cols.append(col)
                        rename_dict[col] = new_name
                        found = True
                        break
                    elif 'Net Income to Total Assets' in col and new_name == 'Net_Income_Ratio':
                        selected_cols.append(col)
                        rename_dict[col] = new_name
                        found = True
                        break
                    elif 'Operating Gross Margin' in col and new_name == 'Gross_Margin':
                        selected_cols.append(col)
                        rename_dict[col] = new_name
                        found = True
                        break
                    elif 'Current Liability to Assets' in col and new_name == 'Liability_Assets_Ratio':
                        selected_cols.append(col)
                        rename_dict[col] = new_name
                        found = True
                        break
        
        if len(selected_cols) == 0:
            raise ValueError("未找到匹配的特征列，请检查数据集格式")
        
        X = df[selected_cols].copy()
        X.rename(columns=rename_dict, inplace=True)
        y = df['Bankrupt?']
        
        # 处理缺失值
        X.fillna(X.mean(), inplace=True)
        
        print(f"✓ 数据处理完成: {len(X)} 行, {len(X.columns)} 个特征")
        return X, y
    
    def load_personal_data(self, filepath='german_credit_data.csv'):
        """
        加载个人信贷数据 (German Credit Risk)
        使用 PySpark 进行大数据处理
        
        Args:
            filepath: CSV文件路径
            
        Returns:
            X: 特征数据 (Pandas DataFrame)
            y: 目标变量 (Pandas Series)
            encoders: 编码器字典
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"找不到文件: {filepath}")
        
        print(f"\n[个人数据] 使用 {self.mode} 引擎加载数据...")
        
        if self.mode == "PySpark" and self.spark:
            try:
                # PySpark 读取
                df_spark = self.spark.read.csv(
                    filepath, 
                    header=True, 
                    inferSchema=True
                )
                
                print(f"✓ 数据加载完成: {df_spark.count()} 行")
                
                # 转换为 Pandas 进行编码处理
                df = df_spark.toPandas()
                
            except Exception as e:
                print(f"⚠️  PySpark 处理失败，降级使用 Pandas: {str(e)}")
                df = pd.read_csv(filepath)
        else:
            df = pd.read_csv(filepath)
        
        # 目标变量映射
        df['Risk'] = df['target'].map({'good': 0, 'bad': 1})
        
        # 处理缺失值
        if 'status_savings' in df.columns:
            df['status_savings'].fillna('unknown/ no savings account', inplace=True)
        if 'status_account' in df.columns:
            df['status_account'].fillna('unknown/ no savings account', inplace=True)
        
        # 选择特征
        feature_cols = ['age', 'credit_amount', 'month_duration', 'status_and_sex', 'housing']
        rename_dict = {
            'age': 'Age',
            'credit_amount': 'Credit_amount',
            'month_duration': 'Duration',
            'status_and_sex': 'Sex',
            'housing': 'Housing'
        }
        
        X = df[feature_cols].copy()
        X.rename(columns=rename_dict, inplace=True)
        y = df['Risk']
        
        # 编码分类变量
        encoders = {}
        categorical_cols = ['Sex', 'Housing']
        
        for col in categorical_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le
        
        print(f"✓ 数据处理完成: {len(X)} 行, {len(X.columns)} 个特征")
        return X, y, encoders
    
    def stop(self):
        """停止 Spark 会话"""
        if self.spark:
            self.spark.stop()
            print("✓ Spark 会话已关闭")
