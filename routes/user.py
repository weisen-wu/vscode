from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models.user import User
from models.company import Company

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/list')
def list_users():
    users = User.query.all()
    return render_template('user/user_list.html', users=users)

@bp.route('/create', methods=['GET', 'POST'])
def create():
    companies = Company.query.all()
    if request.method == 'POST':
        username = request.form.get('username')
        department = request.form.get('department')
        password = request.form.get('password')
        company_id = request.form.get('company_id')
        colors = request.form.get('colors')
        time = request.form.get('time')
        
        if not username or not department or not password or not company_id:
            flash('所有字段都是必填的', 'error')
            return redirect(url_for('user.create'))
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return redirect(url_for('user.create'))
        
        titles = request.form.get('titles')
        user = User(username=username, department=department, company_id=company_id,
                    colors=colors, time=time if time else None, titles=titles)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('用户创建成功', 'success')
        return redirect(url_for('user.list_users'))
    
    return render_template('user/user_create.html', companies=companies)

@bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit(user_id):
    user = User.query.get_or_404(user_id)
    companies = Company.query.all()
    
    if request.method == 'POST':
        username = request.form.get('username')
        department = request.form.get('department')
        password = request.form.get('password')
        company_id = request.form.get('company_id')
        colors = request.form.get('colors')
        time = request.form.get('time')
        
        if not username or not department or not company_id:
            flash('用户名、部门和所属公司是必填的', 'error')
            return redirect(url_for('user.edit', user_id=user_id))
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            flash('用户名已存在', 'error')
            return redirect(url_for('user.edit', user_id=user_id))
        
        titles = request.form.get('titles')
        user.username = username
        user.department = department
        user.company_id = company_id
        user.colors = colors
        user.time = time if time else None
        user.titles = titles
        if password:
            user.set_password(password)
        
        db.session.commit()
        flash('用户信息更新成功', 'success')
        return redirect(url_for('user.list_users'))
    
    return render_template('user/user_edit.html', user=user, companies=companies)

@bp.route('/delete/<int:user_id>', methods=['POST'])
def delete(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('用户已删除', 'success')
    return redirect(url_for('user.list_users'))