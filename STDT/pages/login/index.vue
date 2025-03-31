<template>
  <view class="login-container">
    <view class="logo-container">
      <image class="logo" src="/static/logo.png" mode="aspectFit" />
    </view>
    <view class="login-form">
      <view class="form-item">
        <input type="text" v-model="formData.username" placeholder="请输入用户名" />
      </view>
      <view class="form-item">
        <input type="password" v-model="formData.password" placeholder="请输入密码" />
      </view>
      <button class="login-btn" @click="handleLogin">登录</button>
    </view>
  </view>
</template>

<script>
import { apiBaseUrl } from '/config.js'

export default {
  data() {
    return {
      formData: {
        username: '',
        password: ''
      },
      pageReady: false
    }
  },
  onLoad() {
    console.log('登录页面 onLoad 生命周期')
    this.initializePage()
  },
  onShow() {
    console.log('登录页面 onShow 生命周期')
  },
  onReady() {
    console.log('登录页面 onReady 生命周期')
    this.pageReady = true
  },
  methods: {
    initializePage() {
      console.log('初始化登录页面')
      // 清除之前的登录状态
      try {
        uni.removeStorageSync('auth')
        uni.removeStorageSync('userInfo')
        console.log('清除历史登录信息成功')
      } catch (error) {
        console.error('清除历史登录信息失败:', error)
      }
    },
    base64Encode(str) {
      const b64chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
      let encoded = ''
      const bytes = this.stringToBytes(str)
      
      for(let i = 0; i < bytes.length; i += 3) {
        const chunk = (bytes[i] << 16) | ((i + 1 < bytes.length ? bytes[i + 1] : 0) << 8) | (i + 2 < bytes.length ? bytes[i + 2] : 0)
        encoded += b64chars.charAt((chunk & 0xfc0000) >> 18)
        encoded += b64chars.charAt((chunk & 0x03f000) >> 12)
        encoded += i + 1 < bytes.length ? b64chars.charAt((chunk & 0x000fc0) >> 6) : '='
        encoded += i + 2 < bytes.length ? b64chars.charAt((chunk & 0x00003f)) : '='
      }
      
      return encoded
    },
    
    stringToBytes(str) {
      const bytes = []
      for(let i = 0; i < str.length; i++) {
        bytes.push(str.charCodeAt(i))
      }
      return bytes
    },
    
    async handleLogin() {
      console.log('开始登录流程', { username: this.formData.username })
      if (!this.formData.username || !this.formData.password) {
        console.log('表单验证失败：用户名或密码为空')
        uni.showToast({
          title: '用户名和密码不能为空',
          icon: 'none'
        })
        return
      }
  
      try {
        console.log('正在生成认证token...')
        const token = this.base64Encode(`${this.formData.username}:${this.formData.password}`)
        console.log('准备发送登录请求...')
        const response = await uni.request({
          url: `${apiBaseUrl}/api/login`,
          method: 'POST',
          header: {
            'Content-Type': 'application/json',
            'Authorization': `Basic ${token}`
          },
          data: this.formData
        })
  
        console.log('收到服务器响应:', { statusCode: response.statusCode })
        if (response.statusCode === 200) {
          console.log('登录成功，保存用户信息...')
          uni.setStorageSync('auth', token)
          uni.setStorageSync('userInfo', response.data.user)
          console.log('跳转到首页...')
          uni.reLaunch({
            url: '/pages/index/index'
          })
        } else {
          console.log('登录失败:', response.data)
          uni.showToast({
            title: response.data.error || '登录失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('登录过程发生错误:', error)
        uni.showToast({
          title: '网络错误',
          icon: 'none'
        })
      }
    }
  }
}
</script>

<style>
.login-container {
  padding: 20rpx 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  background-color: #ffffff;
}

.logo-container {
  margin-top: 20rpx;
  margin-bottom: 40rpx;
  text-align: center;
}

.logo {
  width: 220rpx;
  height: 220rpx;
  transition: transform 0.3s ease;
}

.logo:active {
  transform: scale(0.95);
}

.login-form {
  width: 100%;
  max-width: 680rpx;
  padding: 40rpx;
  background-color: #ffffff;
  border-radius: 20rpx;
  box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.login-form:active {
  transform: translateY(2rpx);
  box-shadow: 0 4rpx 15rpx rgba(0, 0, 0, 0.1);
}

/* 表单项样式 */
.form-item {
  margin-bottom: 40rpx;
}

/* 输入框样式 */
.form-item input {
  width: 90%;
  height: 90rpx;
  padding: 0 30rpx;
  border: 2rpx solid #e0e0e0;
  border-radius: 12rpx;
  font-size: 30rpx;
  transition: border-color 0.3s ease, box-shadow 0.3s ease; /* 输入框状态变化动画 */
  background-color: rgba(255, 255, 255, 0.9);
}

/* 输入框焦点状态样式 */
.form-item input:focus {
  border-color: #2979ff;
  box-shadow: 0 0 0 2rpx rgba(41, 121, 255, 0.2); /* 焦点状态阴影效果 */
  outline: none;
}

/* 登录按钮样式 */
.login-btn {
  width: 80%;
  height: 90rpx;
  line-height: 90rpx;
  background: linear-gradient(135deg, #2979ff 0%, #1565c0 100%); /* 渐变背景 */
  color: #fff;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: 500;
  letter-spacing: 2rpx;
  transition: transform 0.3s ease, box-shadow 0.3s ease; /* 按钮状态变化动画 */
  margin-top: 20rpx;
}

/* 按钮点击状态样式 */
.login-btn:active {
  transform: translateY(2rpx); /* 轻微下移效果 */
  opacity: 0.9; /* 透明度变化 */
  box-shadow: 0 4rpx 15rpx rgba(41, 121, 255, 0.2); /* 点击时阴影效果 */
}
</style>