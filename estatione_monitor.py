import subprocess
import time
import logging
from database import db
from models.eStatione import EStatione
from app import app

# 配置日志记录
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def ping_device(ip_address):
    try:
        # 增加ping次数和超时时间，提高检测准确性
        result = subprocess.run(['ping', '-n', '3', '-w', '3000', ip_address],
                              capture_output=True,
                              text=True,
                              timeout=10)  # 添加总体超时限制
        
        # 详细记录ping结果
        logging.info(f'Ping {ip_address} - Return Code: {result.returncode}')
        logging.info(f'Ping Output: {result.stdout}')
        
        # 优化成功判断逻辑
        if result.returncode == 0:
            # 检查是否有成功的响应
            if '字节=' in result.stdout or 'bytes=' in result.stdout:
                # 检查是否有响应时间信息
                if 'ms' in result.stdout:
                    logging.info(f'Device {ip_address} is responding normally')
                    return True
        
        logging.warning(f'Device {ip_address} is not responding properly')
        return False
    except subprocess.TimeoutExpired:
        logging.error(f'Ping timeout for {ip_address}')
        return False
    except Exception as e:
        logging.error(f'Ping error for {ip_address}: {e}')
        return False

def update_device_status():
    with app.app_context():
        try:
            devices = EStatione.query.all()
            for device in devices:
                previous_status = device.connection_status
                current_status = ping_device(device.ip_address)
                
                if previous_status != current_status:
                    logging.info(f'Device {device.ip_address} status changed: {previous_status} -> {current_status}')
                    device.connection_status = current_status
                    try:
                        db.session.commit()
                        logging.info(f'Successfully updated status for device {device.ip_address}')
                    except Exception as e:
                        logging.error(f'Failed to update status for device {device.ip_address}: {e}')
                        db.session.rollback()
                else:
                    logging.info(f'Device {device.ip_address} status unchanged: {current_status}')
        except Exception as e:
            logging.error(f'Error in update_device_status: {e}')

def monitor_devices():
    logging.info('Starting device status monitoring...')
    while True:
        try:
            logging.info('Updating device status...')
            update_device_status()
            logging.info('Device status update completed')
        except Exception as e:
            logging.error(f'Monitor error: {e}')
        time.sleep(30)  # 每30秒检测一次

if __name__ == '__main__':
    monitor_devices()