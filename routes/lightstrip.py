from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from database import db
from models.lightstrip import LightStrip
from models.log import LightStripLog
from models.company import Company
import json

lightstrip_bp = Blueprint('lightstrip', __name__, url_prefix='/lightstrip')

@lightstrip_bp.route('/import_csv', methods=['POST'])
@login_required
def import_csv():
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': '权限不足'}), 403
        
    try:
        data = request.json.get('data', [])
        if not data:
            return jsonify({'status': 'error', 'message': '没有接收到数据'}), 400
            
        success_count = 0
        error_count = 0
        duplicate_count = 0
        error_messages = []
        
        for item in data:
            # 为每条数据创建新的事务
            try:
                mac_address = str(item.get('MAC地址', '')).strip()
                work_order = str(item.get('工单号', '')).strip()
                company_name = str(item.get('所属公司', '')).strip()
                
                # 数据完整性验证
                if not mac_address or not work_order or not company_name:
                    error_count += 1
                    error_messages.append(f'数据不完整: MAC地址={mac_address}, 工单号={work_order}, 所属公司={company_name}')
                    continue
                
                # MAC地址唯一性验证
                if LightStrip.query.filter_by(mac_address=mac_address).first():
                    duplicate_count += 1
                    continue
                
                # 查找公司
                company = Company.query.filter_by(name=company_name).first()
                if not company:
                    error_count += 1
                    error_messages.append(f'公司不存在: {company_name}')
                    continue
                
                # 创建灯条并检查strip_id是否重复
                retry_count = 0
                max_retries = 3
                while retry_count < max_retries:
                    try:
                        lightstrip = LightStrip(
                            mac_address=mac_address,
                            work_order=work_order,
                            operator_name=current_user.username,
                            company_id=company.id
                        )
                        
                        # 创建日志记录
                        log = LightStripLog(
                            operation_type='create',
                            operator_name=current_user.username,
                            mac_address=mac_address,
                            work_order=work_order,
                            details='批量导入灯条'
                        )
                        
                        db.session.add(lightstrip)
                        db.session.add(log)
                        db.session.commit()
                        success_count += 1
                        break
                    except Exception as e:
                        db.session.rollback()
                        if 'Duplicate entry' in str(e) and 'strip_id' in str(e):
                            retry_count += 1
                            if retry_count >= max_retries:
                                error_count += 1
                                error_messages.append(f'生成唯一strip_id失败 (MAC地址: {mac_address})')
                        else:
                            error_count += 1
                            error_messages.append(f'保存数据时出错 (MAC地址: {mac_address}): {str(e)}')
                            break
                
                # 单独提交每条数据的事务已在上面的代码块中完成
                
            except Exception as e:
                error_count += 1
                error_messages.append(f'处理数据时出错: {str(e)}')
                continue
        
        message = f'成功导入 {success_count} 条数据'
        if duplicate_count > 0:
            message += f'，跳过 {duplicate_count} 条重复数据'
        if error_count > 0:
            message += f'，失败 {error_count} 条'

        return jsonify({
            'status': 'success',
            'message': message,
            'success_count': success_count,
            'duplicate_count': duplicate_count,
            'error_count': error_count,
            'errors': error_messages
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'导入过程中发生错误: {str(e)}'}), 500

@lightstrip_bp.route('/import')
@login_required
def import_page():
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
    return render_template('lightstrip/lightstrip_import.html')

@lightstrip_bp.route('/list')
@login_required
def list():
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 获取搜索参数
    mac_address = request.args.get('mac_address', '')
    work_order = request.args.get('work_order', '')
    battery = request.args.get('battery', '')
    
    # 构建查询
    query = LightStrip.query
    
    # 添加搜索条件
    if mac_address:
        query = query.filter(LightStrip.mac_address.ilike(f'%{mac_address}%'))
    if work_order:
        query = query.filter(LightStrip.work_order.ilike(f'%{work_order}%'))
    if battery:
        query = query.filter(LightStrip.battery == int(battery))
        
    # 按创建时间降序排序
    query = query.order_by(LightStrip.created_at.desc())
    
    # 使用分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    lightstrips = pagination.items
    
    # 预先计算分页显示数据
    start_index = (pagination.page - 1) * pagination.per_page + 1
    end_index = min(pagination.page * pagination.per_page, pagination.total)
    
    return render_template('lightstrip/lightstrip_list.html',
                         lightstrips=lightstrips,
                         pagination=pagination,
                         start_index=start_index,
                         end_index=end_index)

@lightstrip_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        mac_address = request.form.get('mac_address')
        work_order = request.form.get('work_order')
        
        from models.config import SystemConfig
        config = SystemConfig.get_config()
        
        errors = {}
        if config.check_lightstrip_duplicate:
            # 检查 MAC 地址是否已存在
            if LightStrip.query.filter_by(mac_address=mac_address).first():
                errors['mac_address'] = 'MAC地址已存在'
                
            # 检查工单号是否已存在
            if LightStrip.query.filter_by(work_order=work_order).first():
                errors['work_order'] = '工单号已存在'
                
            if errors:
                flash('保存失败，请检查输入', 'danger')
                return render_template('lightstrip/lightstrip_create.html', errors=errors)
            
        lightstrip = LightStrip(mac_address=mac_address, work_order=work_order, operator_name=current_user.username)
        db.session.add(lightstrip)
        # 创建日志记录
        log = LightStripLog(
            operation_type='create',
            operator_name=current_user.username,
            mac_address=mac_address,
            work_order=work_order,
            details='新增灯条'
        )
        db.session.add(log)
        db.session.commit()
        flash('灯条添加成功', 'success')
        return redirect(url_for('lightstrip.list'))
        
    return render_template('lightstrip/lightstrip_create.html')

@lightstrip_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    lightstrip = LightStrip.query.get_or_404(id)
    companies = Company.query.all()
    
    if request.method == 'POST':
        mac_address = request.form.get('mac_address')
        work_order = request.form.get('work_order')
        last_estatione_mac = request.form.get('last_estatione_mac')
        company_id = request.form.get('company_id')
        
        from models.config import SystemConfig
        config = SystemConfig.get_config()
        
        errors = {}
        # 检查MAC地址是否已存在（排除当前记录）
        existing_mac = LightStrip.query.filter(
            LightStrip.mac_address == mac_address,
            LightStrip.id != id
        ).first()
        if existing_mac:
            errors['mac_address'] = 'MAC地址已存在'
            
        # 根据配置决定是否检查工单号重复
        if config.check_lightstrip_duplicate:
            # 检查工单号是否已存在（排除当前记录）
            existing_work_order = LightStrip.query.filter(
                LightStrip.work_order == work_order,
                LightStrip.id != id
            ).first()
            if existing_work_order:
                errors['work_order'] = '工单号已存在'
            
        if errors:
            flash('保存失败，请检查输入', 'danger')
            return render_template('lightstrip/lightstrip_edit.html', lightstrip=lightstrip, errors=errors, companies=companies)
            
        lightstrip.mac_address = mac_address
        lightstrip.work_order = work_order
        lightstrip.last_estatione_mac = last_estatione_mac
        lightstrip.company_id = company_id
        
        db.session.commit()
        flash('灯条信息已更新', 'success')
        return redirect(url_for('lightstrip.list'))
    
    return render_template('lightstrip/lightstrip_edit.html', lightstrip=lightstrip, companies=companies)

@lightstrip_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
    
    lightstrip = LightStrip.query.get_or_404(id)
    # 创建删除日志记录
    log = LightStripLog(
        operation_type='delete',
        operator_name=current_user.username,
        mac_address=lightstrip.mac_address,
        work_order=lightstrip.work_order,
        details='删除灯条'
    )
    db.session.add(log)
    db.session.delete(lightstrip)
    db.session.commit()
    flash('灯条删除成功', 'success')
    return redirect(url_for('lightstrip.list'))

@lightstrip_bp.route('/batch', methods=['POST'])
def batch_operation():
    try:
        operation = request.form.get('operation')
        ids = request.form.getlist('ids[]')
        
        if operation == 'delete':
            for id in ids:
                lightstrip = db.session.get(LightStrip, id)
                if lightstrip:
                    db.session.delete(lightstrip)
            db.session.commit()
            flash('批量删除成功', 'success')
        
        elif operation == 'import':
            data = json.loads(request.form.get('data', '[]'))
            for item in data:
                new_lightstrip = LightStrip(
                    mac_address=item['mac_address'],
                    work_order=item['work_order']
                )
                db.session.add(new_lightstrip)
            db.session.commit()
            flash('批量导入成功', 'success')
            
        if operation == 'delete':
            return redirect(url_for('lightstrip.list'))
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@lightstrip_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        strip_id = request.form.get('strip_id')
        mac_address = request.form.get('mac_address')
        work_no = request.form.get('work_no')
        
        # 检查是否存在重复的灯条ID
        existing_strip = LightStrip.query.filter_by(strip_id=strip_id).first()
        if existing_strip:
            flash('灯条ID已存在，请使用其他ID')
            return redirect(url_for('lightstrip.add'))
            
        # 检查是否存在重复的MAC地址
        existing_mac = LightStrip.query.filter_by(mac_address=mac_address).first()
        if existing_mac:
            flash('MAC地址已存在，请检查输入')
            return redirect(url_for('lightstrip.add'))
            
        strip = LightStrip(strip_id=strip_id, mac_address=mac_address, work_no=work_no)
        db.session.add(strip)
        try:
            db.session.commit()
            flash('灯条添加成功', 'success')
            return redirect(url_for('lightstrip.index'))
        except Exception as e:
            db.session.rollback()
            flash('添加失败：' + str(e))
            return redirect(url_for('lightstrip.add'))
            
    return render_template('add_lightstrip.html')