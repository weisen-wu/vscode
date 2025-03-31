from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from flask_sock import Sock
import json
from database import db
from flask_migrate import Migrate
from models.estatione import EStatione
from models.lightstrip import LightStrip
from routes.lightstrip import lightstrip_bp
from routes.estatione import estatione_bp
from routes.config import bp as config_bp
from routes.user import bp as user_bp
from routes.log import log_bp
from routes.api import api_bp
from routes.company import company_bp
from routes.dashboard import dashboard_bp
from flask import Blueprint
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__)
    
    if test_config is None:
        # 加载配置
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql://root:Aa123456@localhost:3306/deng')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        # 添加这行确保正确处理路由
        app.config['APPLICATION_ROOT'] = '/'
    else:
        app.config.update(test_config)
    
    # 初始化扩展
    CORS(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # 初始化登录管理器
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # 初始化WebSocket
    sock = Sock(app)
    
    # 注册蓝图
    app.register_blueprint(lightstrip_bp)
    app.register_blueprint(estatione_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(dashboard_bp)
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    return app

app = create_app()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    department = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('无效的用户名或密码')
    return render_template('new_login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        # 获取统计数据
        estatione_count = EStatione.query.count()
        lightstrip_count = LightStrip.query.count()
        user_count = User.query.count()
        
        # 获取基站状态统计
        online_estatione_count = EStatione.query.filter_by(connection_status=True).count()
        offline_estatione_count = EStatione.query.filter_by(connection_status=False).count()
        warning_estatione_count = 0  # 这里可以添加告警状态的统计逻辑
        
        # 获取最近活动（示例数据）
        recent_activities = [
            {
                'device_name': '基站 A-101',
                'status': '上线',
                'status_color': '#10b981'
            },
            {
                'device_name': '灯条 L-201',
                'status': '配置更新',
                'status_color': '#6366f1'
            },
            {
                'device_name': '基站 A-102',
                'status': '离线',
                'status_color': '#ef4444'
            }
        ]
        
        return render_template('dashboard/admin_dashboard.html',
                             estatione_count=estatione_count,
                             lightstrip_count=lightstrip_count,
                             user_count=user_count,
                             online_estatione_count=online_estatione_count,
                             offline_estatione_count=offline_estatione_count,
                             warning_estatione_count=warning_estatione_count,
                             recent_activities=recent_activities)
    
    return render_template('user_dashboard.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('dashboard'))
    users = User.query.filter_by(is_admin=False).all()
    return render_template('user/user_list.html', users=users)

@app.route('/estatione')
@login_required
def estatione_dashboard():
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
    devices = EStatione.query.all()
    return render_template('estatione/estatione_list.html', devices=devices)

@app.route('/estatione/add', methods=['GET', 'POST'])
@login_required
def add_estatione():
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        mac_id = request.form.get('mac_id')
        ip_address = request.form.get('ip_address')
        location = request.form.get('location')
        description = request.form.get('description')
        
        if EStatione.query.filter_by(mac_id=mac_id).first():
            flash('MAC ID已存在')
            return redirect(url_for('add_estatione'))
            
        device = EStatione(mac_id=mac_id, ip_address=ip_address, location=location, description=description)
        db.session.add(device)
        db.session.commit()
        flash('设备添加成功')
        return redirect(url_for('estatione_dashboard'))
        
    return render_template('estatione/estatione_create.html')

@app.route('/estatione/edit/<int:device_id>', methods=['GET', 'POST'])
@login_required
def edit_estatione(device_id):
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
        
    device = EStatione.query.get_or_404(device_id)
    
    if request.method == 'POST':
        mac_id = request.form.get('mac_id')
        ip_address = request.form.get('ip_address')
        location = request.form.get('location')
        description = request.form.get('description')
        
        existing_device = EStatione.query.filter_by(mac_id=mac_id).first()
        if existing_device and existing_device.id != device_id:
            flash('MAC ID已存在')
            return redirect(url_for('edit_estatione', device_id=device_id))
            
        device.mac_id = mac_id
        device.ip_address = ip_address
        device.location = location
        device.description = description
        db.session.commit()
        flash('设备更新成功')
        return redirect(url_for('estatione_dashboard'))
        
    return render_template('estatione/estatione_edit.html', device=device)

@app.route('/estatione/delete/<int:device_id>', methods=['POST'])
@login_required
def delete_estatione(device_id):
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
        
    device = EStatione.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    flash('设备删除成功')
    return redirect(url_for('estatione_dashboard'))


    return render_template('admin_dashboard.html', users=users)

@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        department = request.form.get('department')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('add_user'))
            
        user = User(username=username, department=department)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('用户添加成功')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('add_user.html')

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
        
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        username = request.form.get('username')
        department = request.form.get('department')
        password = request.form.get('password')
        
        if username != user.username and User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('edit_user', user_id=user_id))
            
        user.username = username
        user.department = department
        if password:
            user.set_password(password)
        db.session.commit()
        flash('用户信息更新成功')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('edit_user.html', user=user)

@app.route('/admin/delete_user/<int:user_id>', methods=['GET', 'POST'])  # 添加 POST 方法支持
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
    
    if request.method == 'POST':  # 只在 POST 请求时执行删除操作
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('用户删除成功')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 创建默认管理员账户
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', department='管理部', is_admin=True)
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
    app.run(host='0.0.0.0', debug=True)