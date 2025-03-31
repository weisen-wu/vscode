@echo off
echo 正在安装Flask应用服务...

:: 检查是否以管理员权限运行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 已获取管理员权限，继续安装...
) else (
    echo 请以管理员权限运行此脚本！
    pause
    exit /b 1
)

:: 安装必要的Python包
echo 正在安装必要的Python包...
pip install pywin32

:: 注册Windows服务
echo 正在注册Windows服务...
python service.py install

:: 启动服务
echo 正在启动服务...
net start FlaskAppService

echo 服务安装完成！
echo 服务名称: FlaskAppService
echo 服务显示名称: Flask Application Service

pause