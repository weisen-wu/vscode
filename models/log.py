from datetime import datetime
from database import db

class LightStripLog(db.Model):
    __tablename__ = 'lightstrip_logs'

    id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.String(20), nullable=False)  # 'create' or 'delete'
    operation_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    operator_name = db.Column(db.String(100), nullable=False)
    mac_address = db.Column(db.String(100), nullable=False)
    work_order = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)

    def __init__(self, operation_type, operator_name, mac_address, work_order, details=None):
        self.operation_type = operation_type
        self.operator_name = operator_name
        self.mac_address = mac_address
        self.work_order = work_order
        self.details = details

    def __repr__(self):
        return f'<LightStripLog {self.operation_type} by {self.operator_name} at {self.operation_time}>'