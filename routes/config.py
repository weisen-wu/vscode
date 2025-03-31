from flask import Blueprint, render_template, request, flash, redirect, url_for
from models.config import SystemConfig
from database import db

bp = Blueprint('config', __name__)

@bp.route('/config')
def index():
    config = SystemConfig.get_config()
    return render_template('config/index.html', config=config)

@bp.route('/config/update', methods=['POST'])
def update():
    config = SystemConfig.get_config()
    config.check_lightstrip_duplicate = 'check_lightstrip_duplicate' in request.form
    db.session.commit()
    flash('配置已更新', 'success')
    return redirect(url_for('config.index'))