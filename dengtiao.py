import importlib.util
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext
import logging
import threading
import json  # 添加json模块导入

# 检查并安装缺失的模块
required_modules = ['paho-mqtt', 'msgpack']
for module in required_modules:
    try:
        importlib.import_module(module.replace('-', '.'))
    except ImportError:
        print(f"模块 {module} 未找到，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion  # 适配新版协议
try:
    import msgpack
except ImportError:
    print("正在安装 msgpack 模块...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "msgpack"])
    import msgpack

# ===== 配置参数 =====
MQTT_BROKER = "10.92.20.102"
MQTT_PORT = 1883
MQTT_USER = "suntop002"
MQTT_PASS = "123456"
ESTATION_ID = "90A9F7300205"
PTL_IDS = ["AD10000416D2", "AD100003D5FE"]  # 将灯条ID存储在列表中
TOPIC_TASK = f"/estation/{ESTATION_ID}/task"
TOPIC_RESULT = f"/estation/{ESTATION_ID}/result"  # 新增结果主题

# ===== MQTT客户端 =====
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="",
    protocol=mqtt.MQTTv5,
    transport="tcp"
)
client.session_expiry_interval = 0  # 设置会话过期时间为立即过期
client._msgtime_mutex = threading.Lock()
client._last_result = {}

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        log("MQTT连接成功")
        client.subscribe(TOPIC_RESULT)  # 订阅结果主题
    else:
        log(f"MQTT连接失败，错误码：{rc}")

client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect

# ===== 数据构造 =====
def build_ptl_command(ptl_ids):
    """构造PTL控制命令（JSON格式）"""
    try:
        # 数据结构对应文档中的TaskData和TaskItemData
        task_items = []

        for ptl_id in PTL_IDS:
            task_item = {
                "TagID": ptl_id,  # 使用配置参数中的灯条编号
                "Beep": True,
                "Flashing": True,  # 设置闪烁
                "Colors": [{"R": True, "G": False, "B": False}]  # 红色闪烁
            }
            task_items.append(task_item)
        
        task_data = {
            "Time": 1,  # 闪烁时间 3*5=15秒
            "Items": task_items
        }
        return json.dumps(task_data)  # 使用json进行序列化
    except Exception as e:
        log(f"命令构造失败：{str(e)}")
        return None

# ===== GUI界面 =====
class ControlApp:
    def __init__(self, root):
        self.root = root
        root.title("PTL灯条控制器")
        root.protocol('WM_DELETE_WINDOW', self.on_close)

        # 灯条ID输入
        self.id_frame = ttk.Frame(root)
        self.id_frame.pack(pady=5)
        
        ttk.Label(self.id_frame, text="灯条ID(逗号分隔):").grid(row=0, column=0)
        self.id_entry = ttk.Entry(self.id_frame, width=40)
        self.id_entry.insert(0, ",".join(PTL_IDS))
        self.id_entry.grid(row=0, column=1)

        # 控制按钮
        self.btn_ontrol = ttk.Button(
            root, 
            text="点亮灯条（红）", 
            command=self.send_command
        )
        self.btn_ontrol.pack(pady=10)
        
        # 日志显示
        self.log_area = scrolledtext.ScrolledText(
            root, 
            width=50, 
            height=10,
            state='disabled'
        )
        self.log_area.pack(padx=10, pady=5)
        
        # 初始化MQTT连接
        self.connect_mqtt()

    def on_close(self):
        client.loop_stop()
        client.disconnect()
        self.root.destroy()

    def connect_mqtt(self):
        """异步连接MQTT"""
        def _connect():
            try:
                log("尝试连接到MQTT代理: {}:{}...".format(MQTT_BROKER, MQTT_PORT), self)
                client.connect(MQTT_BROKER, MQTT_PORT, 60)
                client.loop_start()
                log("MQTT连接成功", self)
            except TimeoutError as te:
                log(f"连接超时：{str(te)}", self)
                import traceback
                log(traceback.format_exc(), self)  # 记录堆栈跟踪
            except Exception as e:
                import traceback
                logging.error(f"连接异常：{str(e)}")
                log(f"连接异常：{str(e)}\n{traceback.format_exc()}", self)  # 记录堆栈跟踪
        threading.Thread(target=_connect, daemon=True).start()

    def send_command(self):
        """发送控制命令"""
        try:
            # 从输入框获取最新灯条ID
            current_ids = [x.strip() for x in self.id_entry.get().split(",") if x.strip()]
            payload = build_ptl_command(current_ids)
            if payload:
                print(payload)
                client.publish(TOPIC_TASK, payload)
                log("命令已发送（原始数据长度：{}字节）".format(len(payload)), self)
        except Exception as e:
            log(f"发送失败：{str(e)}", self)

# ===== MQTT消息处理 =====
def on_message(client, userdata, msg):
    try:
        # 记录原始消息
        raw_data = msg.payload
        log(f"原始消息数据（hex）：{raw_data.hex()}")
        
        # 解析JSON数据
        try:
            result_data = json.loads(raw_data.decode('utf-8'))
            
            # 根据开发文档结构调整字段映射
            result_json = {
                "AP_ID": result_data["ID"],
                "TotalTasks": result_data["TotalCount"],
                "SentTasks": result_data["SendCount"],
                "PTLResults": [
                    {
                        "TagID": item["TagID"],
                        "ResultType": hex(item["ResultType"]),
                        "SendPower": f"{item['RfPowerSend']} dBm",
                        "ReceivePower": f"{item['RfPowerRecv']} dBm",
                        "Battery": f"{item['Battery']/10} V" if item['Battery'] else "无数据",
                        "Sequence": item["Sequence"]
                    } for item in result_data["Results"]
                ]
            }
            
            json_str = json.dumps(result_json, indent=2, ensure_ascii=False)
            log(f"解析成功：\n{json_str}")
            
        except json.JSONDecodeError as je:
            log(f"JSON解析失败：{str(je)}")
        except Exception as e:
            logging.error(f"消息处理失败：{str(e)}")
            import traceback
            log(f"完整错误跟踪：\n{traceback.format_exc()}")
            log(f"原始消息内容：{str(raw_data)}")
    except Exception as e:
        logging.error(f"消息处理失败：{str(e)}")
        import traceback
        log(f"完整错误跟踪：\n{traceback.format_exc()}")
        log(f"原始消息内容：{str(raw_data)}")

client.on_message = on_message  # 注册消息回调

# ===== 日志记录 =====
def log(message, app_instance=None):
    logging.info(message)
    # 使用更可靠的方式获取时间戳
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if app_instance:
        app_instance.log_area.configure(state='normal')
        app_instance.log_area.insert(
            tk.END, 
            f"[{timestamp}] {message}\n"
        )
        app_instance.log_area.configure(state='disabled')
        app_instance.log_area.see(tk.END)

# ===== 初始化 =====
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s"
    )
    
    # 启动GUI
    root = tk.Tk()
    app = ControlApp(root)
    root.mainloop()
    
    # 退出时清理
    client.disconnect()
