from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'contacts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 数据模型
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    group = db.Column(db.String(50), default='默认分组')
    phones = db.relationship('Phone', backref='contact', cascade='all, delete-orphan', lazy=True)

class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)

# 创建数据库表
with app.app_context():
    db.create_all()

# API路由
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """获取所有联系人"""
    contacts = Contact.query.all()
    result = []
    for contact in contacts:
        contact_data = {
            'id': contact.id,
            'name': contact.name,
            'email': contact.email,
            'address': contact.address,
            'group': contact.group,
            'phones': [phone.number for phone in contact.phones]
        }
        result.append(contact_data)
    return jsonify(result)

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """获取单个联系人"""
    contact = Contact.query.get_or_404(contact_id)
    contact_data = {
        'id': contact.id,
        'name': contact.name,
        'email': contact.email,
        'address': contact.address,
        'group': contact.group,
        'phones': [phone.number for phone in contact.phones]
    }
    return jsonify(contact_data)

@app.route('/api/contacts', methods=['POST'])
def add_contact():
    """添加新联系人"""
    data = request.get_json()

    # 验证必填字段
    if not data.get('name') or not data.get('phones'):
        return jsonify({'error': '姓名和电话号码是必填项'}), 400

    # 创建联系人
    new_contact = Contact(
        name=data['name'],
        email=data.get('email'),
        address=data.get('address'),
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

@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """更新联系人信息"""
    contact = Contact.query.get_or_404(contact_id)
    data = request.get_json()

    # 验证必填字段
    if not data.get('name') or not data.get('phones'):
        return jsonify({'error': '姓名和电话号码是必填项'}), 400

    # 更新联系人信息
    contact.name = data['name']
    contact.email = data.get('email')
    contact.address = data.get('address')
    contact.group = data.get('group', '默认分组')

    # 删除旧电话号码
    Phone.query.filter_by(contact_id=contact_id).delete()

    # 添加新电话号码
    for phone_number in data['phones']:
        phone = Phone(number=phone_number, contact_id=contact_id)
        db.session.add(phone)

    db.session.commit()

    return jsonify({'message': '联系人更新成功'})

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """删除联系人"""
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'message': '联系人删除成功'})

@app.route('/api/groups', methods=['GET'])
def get_groups():
    """获取所有分组"""
    groups = db.session.query(Contact.group).distinct().all()
    group_list = [group[0] for group in groups]
    return jsonify(group_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
