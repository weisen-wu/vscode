from flask import Blueprint, jsonify, request
from flask_login import login_required
from models.estatione import EStatione
from models.lightstrip import LightStrip
from models.user import User
from models.company import Company
from functools import wraps
import base64

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': '未提供认证信息'}), 401
        try:
            # 解析Basic认证格式
            if ' ' not in auth_header:
                return jsonify({'error': '认证头格式错误，缺少空格分隔符'}), 401

            auth_type, auth_value = auth_header.split(' ', 1)
            if auth_type.lower() != 'basic':
                return jsonify({'error': '不支持的认证类型'}), 401
            
            try:
                decoded = base64.b64decode(auth_value).decode('utf-8')
                username, password = decoded.split(':', 1)
            except (UnicodeDecodeError, ValueError) as e:
                return jsonify({'error': f'认证信息解码失败: {str(e)}'}), 401
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                return f(*args, **kwargs)
            return jsonify({'error': '认证失败'}), 401
        except Exception as e:
            return jsonify({'error': '服务器处理认证时发生错误'}), 500
    return decorated_function

@dashboard_bp.route('/stats', methods=['GET'])
@api_login_required
def get_dashboard_stats():
    try:
        # 获取当前用户信息
        auth_header = request.headers.get('Authorization')
        auth_value = auth_header.split(' ', 1)[1]
        username = base64.b64decode(auth_value).decode('utf-8').split(':', 1)[0]
        current_user = User.query.filter_by(username=username).first()
        
        # 获取公司的基站和灯条总数
        total_base_stations = EStatione.query.filter_by(company_id=current_user.company_id).count()
        total_light_strips = LightStrip.query.filter_by(company_id=current_user.company_id).count()
        
        return jsonify({
            'totalBaseStations': total_base_stations,
            'totalLightStrips': total_light_strips
        })
    except Exception as e:
        return jsonify({'error': f'获取统计数据失败：{str(e)}'}), 500

@dashboard_bp.route('/company-stations', methods=['GET'])
@api_login_required
def get_company_stations():
    try:
        # 获取当前用户信息
        auth_header = request.headers.get('Authorization')
        auth_value = auth_header.split(' ', 1)[1]
        username = base64.b64decode(auth_value).decode('utf-8').split(':', 1)[0]
        current_user = User.query.filter_by(username=username).first()
        
        # 获取公司的所有基站
        stations = EStatione.query.filter_by(company_id=current_user.company_id).all()
        
        # 转换为JSON格式
        stations_data = [{
            'location': station.location,
            'ip_address': station.ip_address,
            'description': station.description
        } for station in stations]
        
        return jsonify(stations_data)
    except Exception as e:
        return jsonify({'error': f'获取基站列表失败：{str(e)}'}), 500