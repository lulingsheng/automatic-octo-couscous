# -*- coding: utf-8 -*-
"""
数据处理模块 - Data Processor Module
负责数据加载、清洗和特征工程
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os


class DataProcessor:
    """数据处理器类"""
    
    def __init__(self):
        pass
    
    def load_corporate_data(self, filepath='data.csv'):
        """
        加载企业破产数据 (Taiwan Economic Journal)
        
        Args:
            filepath: CSV文件路径
            
        Returns:
            X: 特征数据
            y: 目标变量 (Bankrupt?)
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"找不到文件: {filepath}")
        
        # 读取数据
        df = pd.read_csv(filepath)
        
        # 目标列
        target_col = 'Bankrupt?'
        
        # 定义需要的5个特征列 (使用模糊匹配)
        feature_mapping = {
            'ROA(C) before interest and depreciation before interest': 'ROA',
            'Debt ratio %': 'Debt_Ratio',
            'Net Income to Total Assets': 'Net_Income_Ratio',
            'Operating Gross Margin': 'Gross_Margin',
            'Current Liability to Assets': 'Liability_Assets_Ratio'
        }
        
        # 查找匹配的列名
        selected_cols = []
        rename_dict = {}
        
        for original_name, new_name in feature_mapping.items():
            # 精确匹配
            if original_name in df.columns:
                selected_cols.append(original_name)
                rename_dict[original_name] = new_name
            else:
                # 模糊匹配 (查找包含关键词的列)
                for col in df.columns:
                    if original_name.lower() in col.lower():
                        selected_cols.append(col)
                        rename_dict[col] = new_name
                        break
        
        # 提取特征和目标
        X = df[selected_cols].copy()
        X.rename(columns=rename_dict, inplace=True)
        y = df[target_col]
        
        # 处理缺失值
        X.fillna(X.mean(), inplace=True)
        
        return X, y
    
    def load_personal_data(self, filepath='german_credit_data.csv'):
        """
        加载个人信贷数据 (German Credit Risk)
        
        Args:
            filepath: CSV文件路径
            
        Returns:
            X: 特征数据
            y: 目标变量 (Risk: 0=Low, 1=High)
            encoders: 编码器字典 (用于UI输入转换)
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"找不到文件: {filepath}")
        
        # 读取数据
        df = pd.read_csv(filepath)
        
        # 目标列映射: good -> 0 (低风险), bad -> 1 (高风险)
        target_col = 'target'
        df['Risk'] = df[target_col].map({'good': 0, 'bad': 1})
        
        # 处理缺失值
        if 'status_savings' in df.columns:
            df['status_savings'].fillna('unknown/ no savings account', inplace=True)
        if 'status_account' in df.columns:
            df['status_account'].fillna('unknown/ no savings account', inplace=True)
        
        # 选择5个关键特征
        feature_cols = ['age', 'credit_amount', 'month_duration', 'status_and_sex', 'housing']
        
        # 重命名以匹配UI
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
        
        return X, y, encoders
