// API 基础配置
//export const apiBaseUrl = 'http://10.92.20.102:8000';  //正式环境
export const apiBaseUrl = 'http://10.92.80.85:5000'; //开发环境

// 添加请求拦截器配置
export const requestConfig = {
    headers: {
        'Content-Type': 'application/json'
    }
};