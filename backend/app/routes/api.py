from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.lightstrip import PTLBinding
from app import db

@api.route('/api/lightstrip/list', methods=['GET'])
@jwt_required()
def get_lightstrip_list():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        query = request.args.get('query', '')
        
        # 构建查询
        query_obj = PTLBinding.query
        if query:
            query_obj = query_obj.filter(
                db.or_(
                    PTLBinding.ptl_id.ilike(f'%{query}%'),
                    PTLBinding.work_order.ilike(f'%{query}%'),
                    PTLBinding.operator_name.ilike(f'%{query}%')
                )
            )
        
        # 执行分页查询
        pagination = query_obj.paginate(page=page, per_page=per_page)
        
        # 格式化数据
        lightstrips = [{
            'ptl_id': item.ptl_id,
            'work_order': item.work_order,
            'station_mac': item.station_mac,
            'operator_name': item.operator_name,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else None
        } for item in pagination.items]
        
        return jsonify({
            'code': 200,
            'data': {
                'items': lightstrips,
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@api.route('/lightstrip/bind', methods=['POST'])
@jwt_required()  # 新增JWT认证装饰器
def bind_ptl():
    try:
        data = request.json
        # 自动填充隐藏字段
        binding_data = {
            'ptl_id': data['ptl_id'],
            'work_order': data['work_order'],
            'station_mac': data['station_mac'],
            'last_estatione_mac': data.get('station_mac'),  # 自动关联当前基站
            'operator_name': get_jwt_identity()             # 使用登录用户名
        }
        
        new_binding = PTLBinding(**binding_data)
        db.session.add(new_binding)
        db.session.commit()
        return jsonify({'code': 200, 'message': '绑定成功'})
    except KeyError as e:
        return jsonify({'code': 400, 'message': f'缺少必要字段: {e}'})