# 后端代码规范

## 来源说明
本规范基于以下主流标准制定：
- PEP 8 - Python代码风格指南
- Flask官方最佳实践
- Google Python Style Guide

## Python 代码规范
### 导入顺序
1. 标准库导入
2. 第三方库导入
3. 本地应用导入
   python
   import os
   import sys
   from flask import Flask, request
   from sqlalchemy import Column, String
   from models import Contact

### 命名约定
- 模块名：小写，下划线分隔（snake_case）
- 类名：驼峰命名法（CamelCase）
- 函数/变量名：小写，下划线分隔
- 常量名：大写，下划线分隔

### 代码格式
- 每行最大79字符
- 使用4个空格缩进
- 类/函数间空两行
- 方法间空一行

## Flask 规范
### 路由定义
python
@app.route('/api/endpoint', methods=['GET'])
def get_endpoint():
"""端点功能描述"""
try:

# 业务逻辑
return jsonify(result)
except Exception as e:
return jsonify({'error': str(e)}), 500

### 错误处理
- 使用合适的HTTP状态码
- 统一错误响应格式
- 记录异常日志

## 数据库规范
### 模型定义
python
class Contact(db.Model):
"""联系人数据模型"""
id = db.Column(db.Integer, primary_key=True)
name = db.Column(db.String(100), nullable=False)
def to_dict(self):
"""转换为字典格式"""
return {
'id': self.id,
'name': self.name
}

### 查询优化
- 使用合适的索引
- 避免N+1查询问题
- 合理使用事务

## 安全规范
### 输入验证
python
def validate_contact_data(data):
"""验证联系人数据"""
if not data.get('name') or not data.get('phones'):
raise ValueError('姓名和电话为必填项')

# 更多验证逻辑
### 数据序列化
- 避免直接暴露敏感信息
- 使用合适的序列化方法
- 验证输出数据格式
