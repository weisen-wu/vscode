from flask import Blueprint, request, jsonify, g, current_app, send_file
import os
from flask_login import login_required, current_user
from database import db
from models.lightstrip import LightStrip
from models.log import LightStripLog
from models.user import User
from models.config import SystemConfig
from models.estatione import EStatione
from models.test_po import TestPo
import pyodbc
import binascii, base64, json, time
from werkzeug.security import check_password_hash
from functools import wraps
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 记录请求信息
        print('\n[API请求] ->', {
            '时间': time.strftime('%Y-%m-%d %H:%M:%S'),
            '方法': request.method,
            'URL': request.url,
            '参数': {
                'GET': dict(request.args),
                'POST': request.get_json(silent=True) or request.form.to_dict(),
                'Headers': dict(request.headers)
            }
        })

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            error_response = {'error': '未提供认证信息'}
            print('[API错误] ->', {
                '时间': time.strftime('%Y-%m-%d %H:%M:%S'),
                '状态': 401,
                '错误': error_response
            })
            return jsonify(error_response), 401

        try:
            # 解析Basic认证格式
            if ' ' not in auth_header:
                error_response = {'error': '认证头格式错误，缺少空格分隔符'}
                print('[API错误] ->', {
                    '时间': time.strftime('%Y-%m-%d %H:%M:%S'),
                    '状态': 401,
                    '错误': error_response
                })
                return jsonify(error_response), 401

            auth_type, auth_value = auth_header.split(' ', 1)
            if auth_type.lower() != 'basic':
                error_response = {'error': '不支持的认证类型'}
                print('[API错误] ->', {
                    '时间': time.strftime('%Y-%m-%d %H:%M:%S'),
                    '状态': 401,
                    '错误': error_response
                })
                return jsonify(error_response), 401
            
            try:
                decoded = base64.b64decode(auth_value).decode('utf-8')
                username, password = decoded.split(':', 1)
                print('[认证信息] ->', {
                    '时间': time.strftime('%Y-%m-%d %H:%M:%S'),
                    '用户名': username,
                    '认证类型': auth_type
                })
            except (UnicodeDecodeError, ValueError) as e:
                error_response = {'error': f'认证信息解码失败: {str(e)}'}
                print('[API错误] ->', {
                    '时间': time.strftime('%Y-%m-%d %H:%M:%S'),
                    '状态': 401,
                    '错误': error_response,
                    '异常': str(e)
                })
                return jsonify(error_response), 401
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                print('[认证成功] ->', {
                    '时间': time.strftime('%Y-%m-%d %H:%M:%S'),
                    '用户': username
                })
                return f(*args, **kwargs)

            error_response = {'error': '认证失败'}
            print('[API错误] ->', {
                '时间': time.strftime('%Y-%m-%d %H:%M:%S'),
                '状态': 401,
                '错误': error_response
            })
            return jsonify(error_response), 401

        except (ValueError, UnicodeDecodeError, binascii.Error) as e:
            error_response = {'error': f'无效的认证格式: {str(e)}'}
            print('[API错误] ->', {
                '时间': time.strftime('%Y-%m-%d %H:%M:%S'),
                '状态': 401,
                '错误': error_response,
                '异常': str(e)
            })
            return jsonify(error_response), 401

        except Exception as e:
            import traceback
            error_response = {'error': '服务器处理认证时发生错误'}
            print('[API错误] ->', {
                '时间': time.strftime('%Y-%m-%d %H:%M:%S'),
                '状态': 500,
                '错误': error_response,
                '异常': str(e),
                '堆栈': traceback.format_exc()
            })
            return jsonify(error_response), 500

    return decorated_function

def extract_operator_name(auth_header):
    try:
        # 提取并解码base64凭证
        auth_value = auth_header.split(' ', 1)[1]
        decoded = base64.b64decode(auth_value).decode('utf-8')
        print(f'[DEBUG] 解码后的凭证: {decoded}')  # 调试日志
        
        # 分割用户名和密码
        username, _ = decoded.split(':', 1)
        return username.strip()
    except (IndexError, AttributeError, binascii.Error, UnicodeDecodeError, ValueError) as e:
        print(f'[ERROR] 解析操作员名称失败: {str(e)}')
        return 'unknown_operator'

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/check-version', methods=['GET'])
@api_login_required

def check_version():
    try:
        current_version = '1.0.4'  # 当前后端版本号
        update_logs = {
            '1.0.4': '1.1.调整自动输入焦点，限制了绑定长度'
        }
        response = {
            'code': 200,
            'message': 'success',
            'data': {
                'version': current_version,
                'update_logs': update_logs,
                'download_url': f'{request.host_url}api/download/STDT{current_version}.apk'
            }
        }
        return jsonify(response)
    except Exception as e:
        import traceback
        error_message = f'获取版本信息失败: {str(e)}'
        print('[API错误] ->', {
            '时间': time.strftime('%Y-%m-%d %H:%M:%S'),
            '状态': 500,
            '错误': error_message,
            '异常': str(e),
            '堆栈': traceback.format_exc()
        })
        return jsonify({
            'code': 500,
            'message': error_message,
            'data': None
        }), 500
            # 在这里添加更多版本的更新日志


@api_bp.route('/download/<filename>', methods=['GET'])
@api_login_required
def download_app(filename):
    try:
        # 获取下载目录的绝对路径
        download_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'download'))
        file_path = os.path.join(download_dir, filename)
        
        print('[下载调试] ->', {
            '时间': time.strftime('%Y-%m-%d %H:%M:%S'),
            '请求文件': filename,
            '计算路径': file_path,
            '文件存在': os.path.exists(file_path)
        })
        
        if not os.path.exists(file_path):
            return jsonify({'error': '下载文件不存在'}), 404
            
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print('[下载错误] ->', {
            '时间': time.strftime('%Y-%m-%d %H:%M:%S'),
            '错误': str(e)
        })
        return jsonify({'error': f'下载失败：{str(e)}'}), 500

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return jsonify({
            'message': '登录成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'department': user.department
            }
        })
    return jsonify({'error': '用户名或密码错误'}), 401

@api_bp.route('/lightstrip/bind', methods=['POST'])
@api_login_required
def bind_lightstrip():
    data = request.get_json()
    mac_address = data.get('mac_address')
    work_order = data.get('work_order')
    
    if not mac_address or not work_order:
        return jsonify({'error': '灯条码和绑定号不能为空'}), 400
    
    # 获取当前用户信息
    auth_header = request.headers.get('Authorization')
    operator_name = extract_operator_name(auth_header)
    current_user = User.query.filter_by(username=operator_name).first()
    if not current_user:
        return jsonify({'error': '无法获取用户信息'}), 400
    
    # 检查MAC地址是否已存在
    existing_strip = LightStrip.query.filter_by(mac_address=mac_address).first()
    if existing_strip:
        # 记录解绑操作日志
        unbind_log = LightStripLog(
            operation_type='unbind',
            operator_name=operator_name,
            mac_address=mac_address,
            work_order=existing_strip.work_order,
            details='自动解绑灯条（重新绑定）'
        )
        db.session.add(unbind_log)
        
        # 删除原有绑定记录
        db.session.delete(existing_strip)
    
    # 根据系统配置检查工单号是否重复
    config = SystemConfig.get_config()
    if config.check_lightstrip_duplicate:
        existing_work_order = LightStrip.query.filter_by(work_order=work_order).first()
        if existing_work_order:
            return jsonify({'error': '该绑定号已被使用'}), 400
    
    try:
        strip = LightStrip(
            mac_address=mac_address,
            work_order=work_order,
            operator_name=operator_name,
            company_id=current_user.company_id
        )
        db.session.add(strip)
        
        # 记录操作日志
        log = LightStripLog(
            operation_type='create',
            operator_name=strip.operator_name,
            mac_address=mac_address,
            work_order=work_order,
            details='通过APP绑定灯条'
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': '灯条绑定成功',
            'data': {
                'id': strip.id,
                'strip_id': strip.strip_id,
                'mac_address': strip.mac_address,
                'work_order': strip.work_order
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'绑定失败：{str(e)}'}), 500

@api_bp.route('/lightstrip/light', methods=['POST'])
@api_login_required
def light_lightstrip():
    data = request.get_json()
    work_orders = data.get('work_order')
    
    # 获取当前用户信息
    auth_header = request.headers.get('Authorization')
    operator_name = extract_operator_name(auth_header)
    current_user = User.query.filter_by(username=operator_name).first()
    if not current_user:
        return jsonify({'error': '无法获取用户信息'}), 400
    
    # 确保operator_name变量已定义
    operator_name = current_user.username
    
    if not work_orders:
        return jsonify({'error': '工单码不能为空'}), 400
    
    # 将单个工单转换为列表
    if isinstance(work_orders, str):
        work_orders = [work_orders]
    
    # 获取所有工单对应的灯条信息
    strips = LightStrip.query.filter(
        LightStrip.work_order.in_(work_orders),
        LightStrip.company_id == current_user.company_id
    ).all()
    
    if not strips:
        return jsonify({'error': '未找到对应的灯条或无权限访问'}), 404
    
    # 获取公司的基站列表
    estationes = EStatione.query.filter_by(company_id=current_user.company_id).all()
    if not estationes:
        return jsonify({'error': '未找到可用的基站'}), 404
    
    # 获取用户配置的颜色和时长
    color_map = {
        'red': {'R': True, 'G': False, 'B': False},
        'green': {'R': False, 'G': True, 'B': False},
        'blue': {'R': False, 'G': False, 'B': True},
        'yellow': {'R': True, 'G': True, 'B': False},
        'cyan': {'R': False, 'G': True, 'B': True},
        'purple': {'R': True, 'G': False, 'B': True},
        'white': {'R': True, 'G': True, 'B': True}
    }
    
    # 创建MQTT客户端
    mqtt_client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id='',
        protocol=mqtt.MQTTv5,
        transport='tcp'
    )
    mqtt_client.username_pw_set('suntop002', '123456')
    
    # 初始化结果变量
    success_details = []
    failed_details = []
    
    # 定义消息回调函数
    def on_message(client, userdata, msg):
        try:
            print(f'[DEBUG] 收到MQTT消息: Topic={msg.topic}')
            payload = msg.payload.decode('utf-8')
            print(f'[DEBUG] 消息内容: {payload}')
            result_data = json.loads(payload)
            print(f'[DEBUG] 解析后的数据: {result_data}')
            
            # 验证消息来源的基站ID是否匹配
            if result_data.get('ID') != estatione.mac_id:
                print(f'[DEBUG] 基站ID不匹配: 期望={estatione.mac_id}, 实际={result_data.get("ID")}')
                return
            
            # 处理每个灯条的结果
            for item in result_data.get('Results', []):
                print(f'[DEBUG] 处理结果项: {item}')
                strip = next((s for s in strips if s.mac_address == item.get('TagID')), None)
                if strip:
                    if item.get('ResultType') == 254:
                        print(f'[DEBUG] 灯条点亮成功: {strip.work_order}')
                        success_details.append({
                            'work_order': strip.work_order,
                            'mac_address': strip.mac_address
                        })
                        # 更新灯条的last_estatione_mac字段和电池电量
                        strip.last_estatione_mac = estatione.mac_id
                        strip.battery = item.get('Battery')  # 从MQTT返回结果中获取电池电量
                    else:
                        print(f'[DEBUG] 灯条点亮失败: {strip.work_order}')
                        failed_details.append({
                            'work_order': strip.work_order,
                            'mac_address': strip.mac_address,
                            'error': f'ResultType={item.get("ResultType")}'
                        })
        except Exception as e:
            print(f'[ERROR] MQTT消息处理错误: {str(e)}')
            current_app.logger.error(f'MQTT消息处理错误: {str(e)}')
    
    mqtt_client.on_message = on_message
    
    try:
        # 连接MQTT服务器
        mqtt_client.connect('10.92.20.102', 1883, 60)
        mqtt_client.loop_start()
        
        # 尝试每个基站
        for estatione in estationes:
            # 构造任务数据
            # 获取用户配置的颜色和时长
            user_color = current_user.colors or 'red'  # 默认为红色
            user_time = current_user.time or 1  # 默认为1秒
            
            # 获取对应的RGB配置
            rgb_config = color_map.get(user_color, color_map['red'])
            
            task_items = [{
                'TagID': strip.mac_address,
                'Beep': True,
                'Flashing': True,
                'Colors': [rgb_config]
            } for strip in strips]
            
            task_data = {
                'Time': user_time,
                'Items': task_items
            }
            
            # 设置主题
            task_topic = f'/estation/{estatione.mac_id}/task'
            result_topic = f'/estation/{estatione.mac_id}/result'
            
            # 订阅结果主题
            mqtt_client.subscribe(result_topic)
            
            # 发送任务
            mqtt_client.publish(task_topic, json.dumps(task_data))
            
            # 等待5秒检查结果
            time.sleep(5)
            
            # 如果所有灯条都有结果，就不需要继续尝试其他基站
            if len(success_details) + len(failed_details) == len(strips):
                break
        
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        
        # 提交数据库更改
        db.session.commit()
        
        return jsonify({
            'message': '灯条点亮操作完成',
            'data': {
                'success_details': success_details,
                'failed_details': failed_details
            }
        })
            
    except Exception as e:
        current_app.logger.error(f'MQTT操作错误: {str(e)}')
        return jsonify({'error': f'操作失败: {str(e)}'}), 500

@api_bp.route('/lightstrip/search-po', methods=['POST'])
@api_login_required
def search_po():
    try:
        data = request.get_json()
        po_order = data.get('po_order')
        
        if not po_order:
            return jsonify({'error': '领料单号不能为空'}), 400
        
        # 获取当前用户信息
        auth_header = request.headers.get('Authorization')
        operator_name = extract_operator_name(auth_header)
        current_user = User.query.filter_by(username=operator_name).first()
        if not current_user:
            return jsonify({'error': '无法获取用户信息'}), 400
        
        # 连接MSSQL数据库
        try:
            conn = pyodbc.connect('DRIVER={SQL Server};SERVER=10.92.20.180,1433;DATABASE=YUN;UID=SUNTOP;PWD=SUNTOP123')
            cursor = conn.cursor()
        except pyodbc.Error as e:
            return jsonify({'error': f'数据库连接失败：{str(e)}'}), 500
        
        # 查询视图
        query = "SELECT work_order, work_ph, work_sl FROM [YUN].[dbo].[五金二齐套领料明细] WHERE po_order = ? AND work_order IS NOT NULL AND work_order != ''"
        cursor.execute(query, (po_order,))
        
        # 获取结果
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not records:
            print(f'[查询失败] -> 未找到领料单号: {po_order} 的工单信息')
            return jsonify({'error': '未找到对应的工单信息'}), 404
            
        # 获取当前公司已绑定的所有工单
        bound_work_orders = set(strip.work_order for strip in LightStrip.query.filter_by(company_id=current_user.company_id).all())
        
        # 转换查询结果为字典列表并添加绑定状态
        result = [{
            'work_order': record[0],
            'work_ph': record[1],
            'work_sl': record[2],
            'is_bound': record[0] in bound_work_orders
        } for record in records]
        
        print(f'[查询成功] -> 领料单号: {po_order}, 找到 {len(result)} 条工单记录')
        return jsonify(result)
        
    except Exception as e:
        import traceback
        error_msg = f'查询工单信息时发生错误: {str(e)}'
        print(f'[查询异常] -> {error_msg}\n{traceback.format_exc()}')
        return jsonify({'error': error_msg}), 500

@api_bp.route('/lightstrip/today-records', methods=['GET'])
@api_login_required
def get_today_records():
    from datetime import datetime, timedelta
    
    # 获取今天的开始时间
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 获取当前操作员的今日绑定记录
    operator_name = extract_operator_name(request.headers.get('Authorization'))
    records = LightStrip.query.filter(
        LightStrip.operator_name == operator_name,
        LightStrip.created_at >= today
    ).order_by(LightStrip.created_at.desc()).all()
    
    # 转换记录为JSON格式
    records_json = [{
        'id': record.id,
        'mac_address': record.mac_address,
        'work_order': record.work_order,
        'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for record in records]
    
    return jsonify(records_json)

@api_bp.route('/user/info', methods=['GET'])
@api_login_required
def get_user_info():
    # 获取当前用户信息
    auth_header = request.headers.get('Authorization')
    operator_name = extract_operator_name(auth_header)
    user = User.query.filter_by(username=operator_name).first()
    
    if not user:
        return jsonify({'error': '无法获取用户信息'}), 404
    
    # 获取用户所属公司信息
    from models.company import Company
    company = Company.query.get(user.company_id)
    company_name = company.name if company else '未知公司'
    
    return jsonify({
        'username': user.username,
        'department': user.department,
        'company': company_name,
        'colors': user.colors,
        'time': user.time,
        'titles': user.titles
    })

@api_bp.route('/lightstrip/list', methods=['GET'])
@api_login_required
def get_lightstrip_list():
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = request.args.get('query', '')
    
    # 获取当前用户信息
    auth_header = request.headers.get('Authorization')
    operator_name = extract_operator_name(auth_header)
    current_user = User.query.filter_by(username=operator_name).first()
    if not current_user:
        return jsonify({'error': '无法获取用户信息'}), 404
    
    # 构建查询
    query_filter = LightStrip.company_id == current_user.company_id
    if query:
        query_filter = db.and_(
            query_filter,
            db.or_(
                LightStrip.mac_address.ilike(f'%{query}%'),
                LightStrip.work_order.ilike(f'%{query}%')
            )
        )
    
    # 执行分页查询
    pagination = LightStrip.query.filter(query_filter)\
        .order_by(LightStrip.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    # 格式化返回数据
    items = [{
        'mac_address': strip.mac_address,
        'work_order': strip.work_order,
        'operator_name': strip.operator_name,
        'created_at': strip.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for strip in pagination.items]
    
    return jsonify({
        'items': items,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@api_bp.route('/user/update-settings', methods=['POST'])
@api_login_required
def update_user_settings():
    data = request.get_json()
    colors = data.get('colors')
    time = data.get('time')
    titles = data.get('titles')
    
    if colors is None or time is None:
        return jsonify({'error': '颜色和时长不能为空'}), 400
    
    # 获取当前用户
    auth_header = request.headers.get('Authorization')
    operator_name = extract_operator_name(auth_header)
    user = User.query.filter_by(username=operator_name).first()
    
    if not user:
        return jsonify({'error': '无法获取用户信息'}), 404
    
    try:
        user.colors = colors
        user.time = time
        if titles is not None:
            user.titles = titles
        db.session.commit()
        return jsonify({'message': '设置更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'设置更新失败：{str(e)}'}), 500

@api_bp.route('/lightstrip/unbind', methods=['POST'])
@api_login_required
def unbind_lightstrip():
    data = request.get_json()
    identifiers = data.get('identifiers', [])  # 支持批量解绑
    identifier = data.get('identifier')  # 兼容单个解绑
    
    if not identifiers and not identifier:
        return jsonify({'error': '灯条码或工单码不能为空'}), 400
    
    # 如果是单个解绑，转换为列表格式
    if identifier:
        identifiers = [identifier]
    
    # 获取当前用户信息
    auth_header = request.headers.get('Authorization')
    operator_name = extract_operator_name(auth_header)
    current_user = User.query.filter_by(username=operator_name).first()
    if not current_user:
        return jsonify({'error': '无法获取用户信息'}), 400
    
    # 确保operator_name变量已定义
    operator_name = current_user.username
    
    success_unbinds = []
    failed_unbinds = []
    
    for identifier in identifiers:
        strip = LightStrip.query.filter(
            (LightStrip.mac_address == identifier) |
            (LightStrip.work_order == identifier)
        ).first()
        
        if not strip:
            failed_unbinds.append({
                'identifier': identifier,
                'error': '未找到对应的灯条'
            })
            continue
            
        # 检查灯条是否属于当前用户所在公司
        if strip.company_id != current_user.company_id:
            failed_unbinds.append({
                'identifier': identifier,
                'error': '无权解绑其他公司的灯条'
            })
            continue
        
        try:
            # 记录操作日志
            log = LightStripLog(
                operation_type='delete',
                operator_name=operator_name,
                mac_address=strip.mac_address,
                work_order=strip.work_order,
                details='通过APP解绑灯条'
            )
            db.session.add(log)
            
            # 删除灯条记录
            db.session.delete(strip)
            success_unbinds.append({
                'mac_address': strip.mac_address,
                'work_order': strip.work_order
            })
        except Exception as e:
            failed_unbinds.append({
                'identifier': identifier,
                'error': str(e)
            })
            db.session.rollback()
            continue
    
    try:
        db.session.commit()
        return jsonify({
            'message': '灯条解绑操作完成',
            'data': {
                'success_unbinds': success_unbinds,
                'failed_unbinds': failed_unbinds
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'解绑失败：{str(e)}'}), 500