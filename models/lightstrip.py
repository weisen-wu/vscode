from database import db
from datetime import datetime
from models.company import Company

class LightStrip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strip_id = db.Column(db.String(80), unique=True, nullable=False, default=lambda: f'LS{datetime.now().strftime("%Y%m%d%H%M%S")}{str(int(datetime.now().microsecond/1000)).zfill(3)}')
    mac_address = db.Column(db.String(80), unique=False, nullable=False)  # 移除唯一约束
    work_order = db.Column(db.String(100), nullable=False)
    last_estatione_mac = db.Column(db.String(80), nullable=True)
    operator_name = db.Column(db.String(80), nullable=False)  # 添加操作者用户名字段
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', backref=db.backref('lightstrips', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<LightStrip {self.strip_id}>'