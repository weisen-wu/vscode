import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import os

class AppService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FlaskAppService"
    _svc_display_name_ = "Flask Application Service"
    _svc_description_ = "Flask应用服务，提供Web API和管理界面"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        try:
            # 设置工作目录
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            
            # 配置日志
            import logging
            logging.basicConfig(
                filename='service.log',
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # 导入应用并启动服务器
            from waitress import serve
            from app import create_app
            
            app = create_app()
            serve(app, host='0.0.0.0', port=8000, threads=4)
            
        except Exception as e:
            logging.error(f'服务启动失败: {str(e)}')
            servicemanager.LogErrorMsg(str(e))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AppService)