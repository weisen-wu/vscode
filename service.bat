@echo off

:: 设置服务名称和描述
set SERVICE_NAME=FlaskWebApp
set SERVICE_DESCRIPTION="Flask Web Application Service"

:: 设置应用路径和Python虚拟环境
set APP_PATH=%~dp0
set PYTHON_PATH=%APP_PATH%venv\Scripts\python.exe
set APP_SCRIPT=%APP_PATH%waitress_server.py

:: 安装NSSM服务
nssm install %SERVICE_NAME% %PYTHON_PATH%
nssm set %SERVICE_NAME% AppParameters %APP_SCRIPT%
nssm set %SERVICE_NAME% Description %SERVICE_DESCRIPTION%
nssm set %SERVICE_NAME% AppDirectory %APP_PATH%
nssm set %SERVICE_NAME% AppStdout %APP_PATH%logs\service.log
nssm set %SERVICE_NAME% AppStderr %APP_PATH%logs\error.log

:: 启动服务
nssm start %SERVICE_NAME%

echo Service installation completed.
pause