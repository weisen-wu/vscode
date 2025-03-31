from database import db

class SystemConfig(db.Model):
    __tablename__ = 'system_config'
    
    id = db.Column(db.Integer, primary_key=True)
    check_lightstrip_duplicate = db.Column(db.Boolean, default=True, nullable=False)
    
    @staticmethod
    def get_config():
        config = SystemConfig.query.first()
        if not config:
            config = SystemConfig(check_lightstrip_duplicate=True)
            db.session.add(config)
            db.session.commit()
        return config