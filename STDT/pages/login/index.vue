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
    <view class="version-info">
      <text>{{ appName }} - 版本号：{{ appVersion }}</text>
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
      pageReady: false,
      appVersion: '',
      appName: ''
    }
  },
  onLoad() {
    console.log('登录页面 onLoad 生命周期')
    this.initializePage()
    this.getAppVersion()
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
          
          // 检查版本
          try {
            const versionRes = await uni.request({
              url: `${apiBaseUrl}/api/check-version`,
              method: 'GET',
              header: {
                'Authorization': `Basic ${token}`
              }
            })
            
            if (versionRes.statusCode === 200 && versionRes.data && versionRes.data.code === 200 && versionRes.data.data) {
              const serverVersion = versionRes.data.data.version
              const updateLogs = versionRes.data.data.update_logs
              const downloadUrl = versionRes.data.data.download_url
              console.log('服务器版本号:', serverVersion)
              
              // #ifdef APP-PLUS
              try {
                plus.runtime.getProperty(plus.runtime.appid, async (wgtinfo) => {
                  const manifestVersion = wgtinfo.version
                  console.log('获取到的本地版本号:', manifestVersion)
                  console.log('版本比较:', { serverVersion, manifestVersion })
                  
                  if (serverVersion !== manifestVersion) {
                    uni.showLoading({
                      title: '正在更新...',
                      mask: true
                    })
                    uni.showModal({
                      title: '版本更新',
                      content: `发现新版本 ${serverVersion}\n\n更新内容：\n${updateLogs[serverVersion]}\n\n系统将自动更新到最新版本`,
                      showCancel: false,
                      confirmText: '确定',
                      success: async () => {
                        console.log('[DEBUG] 开始下载更新:', downloadUrl)
                        await uni.downloadFile({
                          url: downloadUrl,
                          header: {
                            'Authorization': `Basic ${token}`
                          },
                          success: (downloadRes) => {
                            uni.hideLoading()
                            console.log('[DEBUG] 下载结果:', downloadRes)
                            if (downloadRes.statusCode === 200) {
                              const tempFilePath = downloadRes.tempFilePath
                              console.log('[DEBUG] 临时文件路径:', tempFilePath)
                              
                              if (!tempFilePath) {
                                console.error('[ERROR] 临时文件路径为空')
                                uni.showModal({
                                  title: '更新失败',
                                  content: '下载文件保存失败',
                                  showCancel: false
                                })
                                return
                              }
                              
                              plus.runtime.install(tempFilePath, {
                                force: true
                              }, () => {
                                console.log('[DEBUG] 安装成功')
                                uni.showModal({
                                  title: '更新完成',
                                  content: '应用已更新完成，请重启应用',
                                  showCancel: false,
                                  success: () => {
                                    plus.runtime.restart()
                                  }
                                })
                              }, (e) => {
                                console.error('[ERROR] 安装更新失败:', e)
                                uni.showModal({
                                  title: '更新失败',
                                  content: `安装更新失败：${e.message}`,
                                  showCancel: false
                                })
                              })
                            } else {
                              console.error('[ERROR] 下载失败，状态码:', downloadRes.statusCode)
                              uni.showModal({
                                title: '更新失败',
                                content: `下载失败（${downloadRes.statusCode}），请稍后重试`,
                                showCancel: false
                              })
                            }
                          },
                          fail: (err) => {
                            console.error('[ERROR] 下载更新包失败:', err)
                            uni.showModal({
                              title: '下载失败',
                              content: `下载更新包失败：${err.errMsg}`,
                              showCancel: false
                            })
                          }
                        })
                      }
                    })
                  } else {
                    console.log('当前已是最新版本')
                  }
                  })
                } catch (error) {
                  console.error('获取本地版本号失败:', error)
                }
                // #endif
              } else {
                console.error('获取服务器版本信息失败:', versionRes.data)
                uni.showToast({
                  title: versionRes.data?.message || '获取版本信息失败',
                  icon: 'none'
                })
              }
            } catch (error) {
              console.error('版本检查失败:', error)
            }
          
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
    },
    async getAppVersion() {
      try {
        // #ifdef APP-PLUS
        // APP环境下，获取应用版本号和名称
        try {
          plus.runtime.getProperty(plus.runtime.appid, (wgtinfo) => {
            console.log('获取到的应用信息:', wgtinfo);
            this.appVersion = wgtinfo.version;  // 修改这里，使用 version 而不是 versionName
            this.appName = wgtinfo.name;
          });
        } catch (error) {
          console.error('获取APP信息失败:', error);
        }
        // #endif
        
        // #ifndef APP-PLUS
        // 非APP环境下，版本号和名称置空
        this.appVersion = '';
        this.appName = '';
        // #endif
      } catch (error) {
        console.error('获取版本信息失败:', error);
        this.appVersion = '';
        this.appName = '';
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

.version-info {
  position: fixed;
  bottom: 40rpx;
  width: 100%;
  text-align: center;
  color: #999;
  font-size: 24rpx;
}
</style>