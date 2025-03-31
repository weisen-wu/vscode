from database import db

class TestPo(db.Model):
    __tablename__ = 'test_po'
    
    id = db.Column(db.Integer, primary_key=True)
    po_order = db.Column(db.String(100), nullable=False)
    work_order = db.Column(db.String(100), nullable=False)
    work_ph = db.Column(db.String(100), nullable=False)
    work_sl = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<TestPo {self.po_order}>'