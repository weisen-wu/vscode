from database import db
from datetime import datetime
from models.company import Company

class EStatione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mac_id = db.Column(db.String(50), unique=True, nullable=False)
    ip_address = db.Column(db.String(50))
    location = db.Column(db.String(100))
    description = db.Column(db.String(200))
    connection_status = db.Column(db.Boolean, default=False)
    last_connected = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', backref=db.backref('estationes', lazy=True))

    def __repr__(self):
        return f'<EStatione {self.mac_id}>'