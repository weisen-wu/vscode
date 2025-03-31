import apiClient from './client'
import { getToken } from './auth'

const bindPTL = (data) => {
    const token = getToken()
    if (!token) {
        return Promise.reject(new Error('未登录或登录已过期'))
    }

    const payload = {
        ...data,
        _timestamp: new Date().toISOString()
    }

    return apiClient.post('/api/lightstrip/bind', payload, {
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

const lightPTL = (data) => {
    const token = getToken()
    if (!token) {
        return Promise.reject(new Error('未登录或登录已过期'))
    }

    return apiClient.post('/api/lightstrip/light', data, {
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

const unbindPTL = (data) => {
    const token = getToken()
    if (!token) {
        return Promise.reject(new Error('未登录或登录已过期'))
    }

    return apiClient.post('/api/lightstrip/unbind', data, {
        headers: {
            'Content-Type': 'application/json'
        }
    })
}

export { bindPTL, lightPTL, unbindPTL }