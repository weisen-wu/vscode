from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from models.company import Company

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    department = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = db.relationship('Company', backref=db.backref('users', lazy=True))
    colors = db.Column(db.String(20), nullable=True)
    time = db.Column(db.Integer, nullable=True)
    titles = db.Column(db.String(200), nullable=True)
    ap_mac = db.Column(db.String(50), nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'