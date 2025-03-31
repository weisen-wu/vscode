import axios from 'axios'

const apiClient = axios.create({
    baseURL: 'http://192.168.3.19:5000',
    timeout: 5000
})

// 请求拦截器
apiClient.interceptors.request.use(
    config => {
        const token = uni.getStorageSync('auth')
        if (token) {
            config.headers['Authorization'] = token  // 直接使用存储的完整token
        }
        // 记录请求日志
        console.log('[API请求] ->', {
            时间: new Date().toLocaleString(),
            方法: config.method.toUpperCase(),
            URL: `${config.baseURL}${config.url}`,
            参数: config.params || config.data,
            请求头: config.headers
        })
        return config
    },
    error => {
        console.error('[API请求错误] ->', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
apiClient.interceptors.response.use(
    response => {
        // 记录响应日志
        console.log('[API响应] ->', {
            时间: new Date().toLocaleString(),
            状态: response.status,
            URL: response.config.url,
            数据: response.data
        })
        return response
    },
    error => {
        // 记录错误日志
        console.error('[API错误] ->', {
            时间: new Date().toLocaleString(),
            状态: error.response?.status,
            URL: error.config?.url,
            错误: error.response?.data || error.message
        })
        if (error.response?.status === 401) {
            uni.removeStorageSync('auth')
            uni.redirectTo({
                url: '/pages/login/index'
            })
        }
        return Promise.reject(error)
    }
)

export default apiClient