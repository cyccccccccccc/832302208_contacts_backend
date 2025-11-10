# 通讯录管理系统 - 后端

## 项目简介
基于Flask的RESTful API后端服务，提供通讯录数据的CRUD操作接口。

## 技术栈
- Python
- Flask
- Flask-SQLAlchemy
- Flask-CORS
- SQLite

## 项目结构
832302208_contacts_backend/
├── src/                            # 源代码目录
│   ├── app.py                      # Flask应用主文件
│   └── contacts.db                 # SQLite数据库文件
├── codestyle.md                    # 代码规范文档
└── README.md                       # 项目说明文档

## API 接口
### 联系人管理
- `GET /api/contacts` - 获取所有联系人
- `GET /api/contacts/<id>` - 获取指定联系人
- `POST /api/contacts` - 创建新联系人
- `PUT /api/contacts/<id>` - 更新联系人
- `DELETE /api/contacts/<id>` - 删除联系人

### 分组管理
- `GET /api/groups` - 获取所有分组

## 快速开始
### 环境要求
- Python 3.8+
- pip 包管理器

### 安装步骤
1. 克隆项目
2. 安装依赖：`pip install -r requirements.txt`
3. 运行应用：`python app.py`

### 依赖安装
bash
pip install flask flask-sqlalchemy flask-cors flask-migrate

## 部署说明
### 开发环境
bash
python app.py

### 生产环境
使用Gunicorn部署：
bash
# 安装gunicorn
pip install gunicorn

# 启动服务（在项目src目录下）
gunicorn -w 4 -b 0.0.0.0:5000 app:app --daemon

# 或者使用nohup保持后台运行
nohup gunicorn -w 4 -b 0.0.0.0:5000 app:app > app.log 2>&1 &

## 数据库配置
使用SQLite，数据库文件自动创建于项目根目录。
