from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'contacts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # 添加数据库迁移支持

# 数据模型
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    birth_date = db.Column(db.String(10))  # 添加生日字段，格式：YYYY-MM-DD
    group = db.Column(db.String(50), default='默认分组')
    phones = db.relationship('Phone', backref='contact', cascade='all, delete-orphan', lazy=True)

class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)

# 创建数据库表（如果不存在）
with app.app_context():
    db.create_all()

# API路由
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """获取所有联系人"""
    try:
        contacts = Contact.query.all()
        result = []
        for contact in contacts:
            contact_data = {
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'address': contact.address,
                'birth_date': contact.birth_date,
                'group': contact.group,
                'phones': [phone.number for phone in contact.phones]
            }
            result.append(contact_data)
        return jsonify(result)
    except Exception as e:
        print(f"Error getting contacts: {e}")
        return jsonify({'error': '获取联系人失败'}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """获取单个联系人"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        contact_data = {
            'id': contact.id,
            'name': contact.name,
            'email': contact.email,
            'address': contact.address,
            'birth_date': contact.birth_date,
            'group': contact.group,
            'phones': [phone.number for phone in contact.phones]
        }
        return jsonify(contact_data)
    except Exception as e:
        print(f"Error getting contact {contact_id}: {e}")
        return jsonify({'error': '获取联系人失败'}), 500

@app.route('/api/contacts', methods=['POST'])
def add_contact():
    """添加新联系人"""
    try:
        data = request.get_json()

        # 验证必填字段
        if not data.get('name') or not data.get('phones'):
            return jsonify({'error': '姓名和电话号码是必填项'}), 400

        # 创建联系人
        new_contact = Contact(
            name=data['name'],
            email=data.get('email'),
            address=data.get('address'),
            birth_date=data.get('birth_date'),
            group=data.get('group', '默认分组')
        )

        db.session.add(new_contact)
        db.session.commit()

        # 添加电话号码
        for phone_number in data['phones']:
            phone = Phone(number=phone_number, contact_id=new_contact.id)
            db.session.add(phone)

        db.session.commit()

        return jsonify({'message': '联系人添加成功', 'id': new_contact.id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error adding contact: {e}")
        return jsonify({'error': '添加联系人失败'}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """更新联系人信息"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        data = request.get_json()

        # 验证必填字段
        if not data.get('name') or not data.get('phones'):
            return jsonify({'error': '姓名和电话号码是必填项'}), 400

        # 更新联系人信息
        contact.name = data['name']
        contact.email = data.get('email')
        contact.address = data.get('address')
        contact.birth_date = data.get('birth_date')
        contact.group = data.get('group', '默认分组')

        # 删除旧电话号码
        Phone.query.filter_by(contact_id=contact_id).delete()

        # 添加新电话号码
        for phone_number in data['phones']:
            phone = Phone(number=phone_number, contact_id=contact_id)
            db.session.add(phone)

        db.session.commit()

        return jsonify({'message': '联系人更新成功'})
    except Exception as e:
        db.session.rollback()
        print(f"Error updating contact {contact_id}: {e}")
        return jsonify({'error': '更新联系人失败'}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """删除联系人"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'message': '联系人删除成功'})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting contact {contact_id}: {e}")
        return jsonify({'error': '删除联系人失败'}), 500

@app.route('/api/groups', methods=['GET'])
def get_groups():
    """获取所有分组"""
    try:
        groups = db.session.query(Contact.group).distinct().all()
        group_list = [group[0] for group in groups if group[0]]  # 过滤掉空值
        return jsonify(group_list)
    except Exception as e:
        print(f"Error getting groups: {e}")
        return jsonify({'error': '获取分组失败'}), 500

@app.route('/api/birthdays', methods=['GET'])
def get_upcoming_birthdays():
    """获取近期生日联系人"""
    try:
        contacts = Contact.query.all()
        today = datetime.now()
        upcoming_birthdays = []

        for contact in contacts:
            if contact.birth_date:
                try:
                    birth_date = datetime.strptime(contact.birth_date, '%Y-%m-%d')
                    # 设置生日为今年的日期
                    this_year_birthday = datetime(today.year, birth_date.month, birth_date.day)

                    # 如果今年的生日已经过去，设置为明年的生日
                    if this_year_birthday < today:
                        next_birthday = datetime(today.year + 1, birth_date.month, birth_date.day)
                    else:
                        next_birthday = this_year_birthday

                    # 检查是否在未来30天内
                    days_diff = (next_birthday - today).days
                    if 0 <= days_diff <= 30:
                        contact_data = {
                            'id': contact.id,
                            'name': contact.name,
                            'birth_date': contact.birth_date,
                            'phones': [phone.number for phone in contact.phones]
                        }
                        upcoming_birthdays.append(contact_data)
                except ValueError:
                    continue

        # 按生日日期排序
        upcoming_birthdays.sort(key=lambda x: x['birth_date'][5:])  # 按月份和日期排序

        return jsonify(upcoming_birthdays)
    except Exception as e:
        print(f"Error getting birthdays: {e}")
        return jsonify({'error': '获取生日数据失败'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
