from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models.company import Company

company_bp = Blueprint('company', __name__, url_prefix='/company')

@company_bp.route('/list')
def list_companies():
    companies = Company.query.all()
    return render_template('company/company_list.html', companies=companies)

@company_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        contact_person = request.form.get('contact_person')
        phone = request.form.get('phone')
        email = request.form.get('email')
        
        if not name:
            flash('公司名称是必填的', 'error')
            return redirect(url_for('company.create'))
        
        if Company.query.filter_by(name=name).first():
            flash('公司名称已存在', 'error')
            return redirect(url_for('company.create'))
        
        company = Company(name=name, address=address, contact_person=contact_person,
                         phone=phone, email=email)
        db.session.add(company)
        db.session.commit()
        
        flash('公司创建成功', 'success')
        return redirect(url_for('company.list_companies'))
    
    return render_template('company/company_create.html')

@company_bp.route('/edit/<int:company_id>', methods=['GET', 'POST'])
def edit(company_id):
    company = Company.query.get_or_404(company_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        contact_person = request.form.get('contact_person')
        phone = request.form.get('phone')
        email = request.form.get('email')
        
        if not name:
            flash('公司名称是必填的', 'error')
            return redirect(url_for('company.edit', company_id=company_id))
        
        existing_company = Company.query.filter_by(name=name).first()
        if existing_company and existing_company.id != company_id:
            flash('公司名称已存在', 'error')
            return redirect(url_for('company.edit', company_id=company_id))
        
        company.name = name
        company.address = address
        company.contact_person = contact_person
        company.phone = phone
        company.email = email
        
        db.session.commit()
        flash('公司信息更新成功', 'success')
        return redirect(url_for('company.list_companies'))
    
    return render_template('company/company_edit.html', company=company)

@company_bp.route('/delete/<int:company_id>', methods=['POST'])
def delete(company_id):
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    flash('公司已删除', 'success')
    return redirect(url_for('company.list_companies'))