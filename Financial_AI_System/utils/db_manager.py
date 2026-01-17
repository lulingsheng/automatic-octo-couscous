# -*- coding: utf-8 -*-
"""
数据库管理模块 - Database Manager
负责用户管理和操作日志记录
"""

import sqlite3
import hashlib
from datetime import datetime
import os


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path='database.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建操作日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        # 检查是否存在默认管理员账号
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            # 创建默认管理员账号
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ('admin', '123456', 'admin')
            )
            print("✓ 默认管理员账号已创建: admin/123456")
        
        conn.commit()
        conn.close()
    
    def verify_user(self, username, password):
        """
        验证用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            dict: 用户信息 (包含 username, role) 或 None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT username, role FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'username': result[0],
                'role': result[1]
            }
        return None
    
    def add_user(self, username, password, role='user'):
        """
        添加新用户
        
        Args:
            username: 用户名
            password: 密码
            role: 角色 (admin/user)
            
        Returns:
            bool: 是否成功
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role)
            )
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def delete_user(self, username):
        """
        删除用户
        
        Args:
            username: 用户名
            
        Returns:
            bool: 是否成功
        """
        if username == 'admin':
            return False  # 不允许删除管理员
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        
        conn.commit()
        conn.close()
        return True
    
    def get_all_users(self):
        """
        获取所有用户列表
        
        Returns:
            list: 用户列表
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, role, created_at FROM users")
        users = cursor.fetchall()
        
        conn.close()
        return users
    
    def log_action(self, user, action, details=''):
        """
        记录用户操作日志
        
        Args:
            user: 用户名
            action: 操作类型
            details: 操作详情
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO logs (user, action, details) VALUES (?, ?, ?)",
            (user, action, details)
        )
        
        conn.commit()
        conn.close()
    
    def get_logs(self, limit=100):
        """
        获取操作日志
        
        Args:
            limit: 返回记录数
            
        Returns:
            list: 日志列表
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT timestamp, user, action, details FROM logs ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        
        logs = cursor.fetchall()
        conn.close()
        return logs
    
    def clear_logs(self):
        """清空日志"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM logs")
        
        conn.commit()
        conn.close()


# 装饰器：自动记录操作日志
def log_action(action_name):
    """
    操作日志装饰器
    
    Args:
        action_name: 操作名称
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 从 session_state 获取当前用户
            import streamlit as st
            if 'user' in st.session_state:
                db = DatabaseManager()
                db.log_action(
                    st.session_state.user['username'],
                    action_name,
                    f"执行了 {func.__name__} 操作"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator
