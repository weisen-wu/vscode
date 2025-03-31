import apiClient from './client'

// 登录函数
const login = (username, password) => {
    // 创建Basic认证token
    const token = btoa(`${username}:${password}`)
    
    return apiClient.post('/api/login', { username, password }, {
        headers: {
            'Authorization': `Basic ${token}`,
            'Content-Type': 'application/json'
        }
    }).then(response => {
        // 登录成功后保存token
        uni.setStorageSync('auth', token)
        return response.data
    })
}

// 获取认证token
const getToken = () => {
    return uni.getStorageSync('auth')
}

// 清除认证token
const clearToken = () => {
    uni.removeStorageSync('auth')
}

// 检查是否已登录
const isAuthenticated = () => {
    return !!getToken()
}

export { login, getToken, clearToken, isAuthenticated }