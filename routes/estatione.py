from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db
from models.estatione import EStatione
from models.company import Company

import subprocess
from flask import jsonify

estatione_bp = Blueprint('estatione', __name__, url_prefix='/estatione')

@estatione_bp.route('/list')
@login_required
def list():
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
    devices = EStatione.query.join(Company).all()
    return render_template('estatione/estatione_list.html', devices=devices)

@estatione_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
    
    companies = Company.query.all()
    if request.method == 'POST':
        mac_id = request.form.get('mac_id')
        ip_address = request.form.get('ip_address')
        location = request.form.get('location')
        description = request.form.get('description')
        company_id = request.form.get('company_id')
        
        if not company_id:
            flash('所属公司是必填的')
            return redirect(url_for('estatione.create'))
        
        if EStatione.query.filter_by(mac_id=mac_id).first():
            flash('MAC ID已存在')
            return redirect(url_for('estatione.create'))
            
        device = EStatione(mac_id=mac_id, ip_address=ip_address, 
                          location=location, description=description,
                          company_id=company_id)
        db.session.add(device)
        db.session.commit()
        flash('基站添加成功')
        return redirect(url_for('estatione.list'))
        
    return render_template('estatione/estatione_create.html', companies=companies)

@estatione_bp.route('/edit/<int:device_id>', methods=['GET', 'POST'])
@login_required
def edit(device_id):
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
        
    device = EStatione.query.get_or_404(device_id)
    companies = Company.query.all()
    if request.method == 'POST':
        mac_id = request.form.get('mac_id')
        ip_address = request.form.get('ip_address')
        location = request.form.get('location')
        description = request.form.get('description')
        company_id = request.form.get('company_id')
        
        if not company_id:
            flash('所属公司是必填的')
            return redirect(url_for('estatione.edit', device_id=device_id))
        
        if mac_id != device.mac_id and EStatione.query.filter_by(mac_id=mac_id).first():
            flash('MAC ID已存在')
            return redirect(url_for('estatione.edit', device_id=device_id))
            
        device.mac_id = mac_id
        device.ip_address = ip_address
        device.location = location
        device.description = description
        device.company_id = company_id
        db.session.commit()
        flash('基站更新成功')
        return redirect(url_for('estatione.list'))
        
    return render_template('estatione/estatione_edit.html', device=device, companies=companies)

@estatione_bp.route('/delete/<int:device_id>', methods=['POST'])
@login_required
def delete(device_id):
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
    
    device = EStatione.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    flash('基站删除成功')
    return redirect(url_for('estatione.list'))

@estatione_bp.route('/api/ping')
def ping_device():
    ip = request.args.get('ip')
    if not ip:
        return jsonify({'status': 'error', 'message': 'IP地址不能为空'})
    
    try:
        # Windows系统下执行ping命令
        result = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            return jsonify({'status': 'online'})
        else:
            return jsonify({'status': 'offline'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})