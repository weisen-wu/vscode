from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models.log import LightStripLog
from database import db

log_bp = Blueprint('log', __name__)

@log_bp.route('/logs')
def list():
    # 获取筛选参数
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    operation_type = request.args.get('operation_type')

    # 构建查询
    query = LightStripLog.query

    # 应用筛选条件
    if start_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(LightStripLog.operation_time >= start_datetime)

    if end_date:
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        # 设置结束时间为当天的最后一秒
        end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
        query = query.filter(LightStripLog.operation_time <= end_datetime)

    if operation_type:
        query = query.filter(LightStripLog.operation_type == operation_type)

    # 按时间倒序排序
    logs = query.order_by(LightStripLog.operation_time.desc()).all()

    return render_template('log/log_list.html', logs=logs)

@log_bp.route('/logs/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    if not current_user.is_admin:
        flash('权限不足')
        return redirect(url_for('login'))
    
    log = LightStripLog.query.get_or_404(id)
    db.session.delete(log)
    db.session.commit()
    flash('日志删除成功', 'success')
    return redirect(url_for('log.list'))