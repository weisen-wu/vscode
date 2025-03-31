from flask_jwt_extended import JWTManager
from datetime import timedelta
import os  # 新增导入

def create_app():
    app = Flask(__name__)
    
    # 修正JWT配置（确保加载顺序）
    app.config.from_object('config')
    app.config.update(
        JWT_SECRET_KEY=os.getenv('JWT_SECRET', os.urandom(32)),  # 优先使用环境变量
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1),
        JWT_ALGORITHM='HS256',
        JWT_TOKEN_LOCATION=['headers', 'cookies']  # 新增多位置验证
    )
    
    # 确保在所有插件初始化前配置
    jwt = JWTManager(app)
    # 其他初始化代码...