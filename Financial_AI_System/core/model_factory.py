# -*- coding: utf-8 -*-
"""
模型工厂模块 - Model Factory (升级版)
负责模型训练、保存和预测
集成 PySpark 大数据处理
"""

import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.spark_processor import SparkDataManager


class ModelEngine:
    """模型引擎类 - 集成大数据处理"""
    
    def __init__(self):
        self.model_dir = 'models'
        # 确保模型目录存在
        os.makedirs(self.model_dir, exist_ok=True)
        
        # 初始化大数据管理器
        self.data_manager = SparkDataManager()
    
    def get_engine_status(self):
        """获取计算引擎状态"""
        return self.data_manager.get_engine_info()
    
    def train_all_models(self):
        """
        训练所有模型 (企业风险 + 个人信贷)
        使用 PySpark 进行数据处理
        """
        print("\n" + "=" * 60)
        print("🚀 开始训练模型 (使用 {} 引擎)".format(self.data_manager.mode))
        print("=" * 60)
        
        # 1. 训练企业破产风险模型
        print("\n[1/2] 训练企业破产风险模型...")
        try:
            X_corp, y_corp = self.data_manager.load_corporate_data('data.csv')
            
            # 划分训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X_corp, y_corp, test_size=0.2, random_state=42, stratify=y_corp
            )
            
            # 训练随机森林
            print("  → 正在训练随机森林模型...")
            rf_corp = RandomForestClassifier(
                n_estimators=100, 
                random_state=42, 
                max_depth=10,
                min_samples_split=5,
                n_jobs=-1
            )
            rf_corp.fit(X_train, y_train)
            
            # 评估
            y_pred = rf_corp.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            print(f"  ✓ 企业模型训练完成! 准确率: {accuracy:.4f}")
            
            # 保存模型
            model_path = os.path.join(self.model_dir, 'corporate_model.pkl')
            joblib.dump(rf_corp, model_path)
            print(f"  ✓ 模型已保存至: {model_path}")
            
        except Exception as e:
            print(f"  ✗ 企业模型训练失败: {str(e)}")
        
        # 2. 训练个人信贷风险模型
        print("\n[2/2] 训练个人信贷风险模型...")
        try:
            X_pers, y_pers, encoders = self.data_manager.load_personal_data('german_credit_data.csv')
            
            # 划分训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X_pers, y_pers, test_size=0.2, random_state=42, stratify=y_pers
            )
            
            # 训练随机森林
            print("  → 正在训练随机森林模型...")
            rf_pers = RandomForestClassifier(
                n_estimators=100, 
                random_state=42, 
                max_depth=10,
                min_samples_split=5,
                n_jobs=-1
            )
            rf_pers.fit(X_train, y_train)
            
            # 评估
            y_pred = rf_pers.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            print(f"  ✓ 个人模型训练完成! 准确率: {accuracy:.4f}")
            
            # 保存模型和编码器
            model_path = os.path.join(self.model_dir, 'personal_model.pkl')
            encoders_path = os.path.join(self.model_dir, 'encoders.pkl')
            joblib.dump(rf_pers, model_path)
            joblib.dump(encoders, encoders_path)
            print(f"  ✓ 模型已保存至: {model_path}")
            print(f"  ✓ 编码器已保存至: {encoders_path}")
            
        except Exception as e:
            print(f"  ✗ 个人模型训练失败: {str(e)}")
        
        print("\n" + "=" * 60)
        print("✅ 所有模型训练完成!")
        print("=" * 60 + "\n")
    
    def predict_corporate(self, input_dict):
        """
        企业破产风险预测
        
        Args:
            input_dict: 输入特征字典
            
        Returns:
            probability: 破产概率 (0.0-1.0)
            risk_label: 风险标签
        """
        model_path = os.path.join(self.model_dir, 'corporate_model.pkl')
        
        if not os.path.exists(model_path):
            raise FileNotFoundError("模型文件不存在! 请先训练模型。")
        
        # 加载模型
        model = joblib.load(model_path)
        
        # 转换输入为DataFrame
        feature_order = ['ROA', 'Debt_Ratio', 'Net_Income_Ratio', 'Gross_Margin', 'Liability_Assets_Ratio']
        input_data = pd.DataFrame([[float(input_dict[k]) for k in feature_order]], columns=feature_order)
        
        # 预测
        prob = model.predict_proba(input_data)[0][1]  # 破产概率
        risk_label = '高风险' if prob > 0.5 else '低风险'
        
        return prob, risk_label
    
    def predict_personal(self, input_dict):
        """
        个人信贷风险预测
        
        Args:
            input_dict: 输入特征字典
            
        Returns:
            probability: 违约概率 (0.0-1.0)
            risk_label: 风险标签
        """
        model_path = os.path.join(self.model_dir, 'personal_model.pkl')
        encoders_path = os.path.join(self.model_dir, 'encoders.pkl')
        
        if not os.path.exists(model_path) or not os.path.exists(encoders_path):
            raise FileNotFoundError("模型文件不存在! 请先训练模型。")
        
        # 加载模型和编码器
        model = joblib.load(model_path)
        encoders = joblib.load(encoders_path)
        
        # 准备输入数据
        input_data = {
            'Age': int(input_dict['Age']),
            'Credit_amount': float(input_dict['Credit_amount']),
            'Duration': int(input_dict['Duration']),
            'Sex': input_dict['Sex'],
            'Housing': input_dict['Housing']
        }
        
        # 编码分类变量
        for col in ['Sex', 'Housing']:
            try:
                input_data[col] = encoders[col].transform([input_data[col]])[0]
            except:
                input_data[col] = 0
        
        # 转换为DataFrame
        feature_order = ['Age', 'Credit_amount', 'Duration', 'Sex', 'Housing']
        df = pd.DataFrame([[input_data[k] for k in feature_order]], columns=feature_order)
        
        # 预测
        prob = model.predict_proba(df)[0][1]  # 违约概率
        risk_label = '高风险' if prob > 0.5 else '低风险'
        
        return prob, risk_label


if __name__ == "__main__":
    # 直接运行此文件时，执行模型训练
    engine = ModelEngine()
    engine.train_all_models()
