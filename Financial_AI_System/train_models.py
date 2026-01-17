# -*- coding: utf-8 -*-
"""
快速训练脚本 - Quick Training Script
运行此脚本可快速训练所有模型
"""

from core.model_factory import ModelEngine

if __name__ == "__main__":
    print("\n" + "="*60)
    print("金融智能分析系统 - 模型训练")
    print("Financial Intelligent Analysis System - Model Training")
    print("="*60 + "\n")
    
    engine = ModelEngine()
    engine.train_all_models()
    
    print("\n" + "="*60)
    print("训练完成! 现在可以运行: streamlit run app.py")
    print("Training Complete! Now run: streamlit run app.py")
    print("="*60 + "\n")
