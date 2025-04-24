<template>
  <view class="container">
    <view class="form-container">
      <uni-forms ref="form" :rules="rules" :modelValue="formData">
        <uni-forms-item :label="userTitles || '工单号'" name="work_order">
          <input 
            class="uni-input"
            v-model="formData.work_order" 
            :placeholder="'请输入' + (userTitles || '工单号')"
            :focus="inputFocus"
            :maxlength="MAX_INPUT_LENGTH"
            @input="handleInput"
          />
        </uni-forms-item>
      </uni-forms>
      <button class="submit-btn" type="primary" @click="handleSubmit">点亮灯条</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiBaseUrl } from '@/config.js'

const form = ref(null)
const inputFocus = ref(false)
const MAX_INPUT_LENGTH = 16 // 设置最大输入长度
const lastInputLength = ref(0)

const formData = ref({
  work_order: ''
})

const userTitles = ref('')

const rules = {
  work_order: {
    rules: [{
      required: true,
      errorMessage: '请输入工单号'
    }, {
      validateFunction: (rule, value, data, callback) => {
        if (value.length > MAX_INPUT_LENGTH) {
          callback('工单号不能超过' + MAX_INPUT_LENGTH + '位')
        }
        return true
      }
    }]
  }
}

// 处理输入
const handleInput = (e) => {
  const value = e.detail.value
  // 如果当前输入长度等于最大长度，且上一次输入长度小于最大长度，说明刚刚达到限制
  if (value.length === MAX_INPUT_LENGTH && lastInputLength.value < MAX_INPUT_LENGTH) {
    uni.showToast({
      title: '工单号已达到最大长度' + MAX_INPUT_LENGTH + '位',
      icon: 'none',
      duration: 1500
    })
  }
  lastInputLength.value = value.length
  formData.value.work_order = value
}

onMounted(() => {
  // 页面加载后延迟聚焦到输入框
  setTimeout(() => {
    inputFocus.value = true
  }, 300)
  
  fetchUserInfo()
})

const fetchUserInfo = async () => {
  try {
    const response = await uni.request({
      url: `${apiBaseUrl}/api/user/info`,
      method: 'GET',
      header: {
        'Authorization': 'Basic ' + uni.getStorageSync('auth')
      }
    })

    if (response.statusCode === 200) {
      userTitles.value = response.data.titles
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

const handleSubmit = async () => {
  try {
    const valid = await form.value.validate()
    if (!valid) return

    const response = await uni.request({
      url: `${apiBaseUrl}/api/lightstrip/light`,
      method: 'POST',
      header: {
        'Authorization': 'Basic ' + uni.getStorageSync('auth')
      },
      data: formData.value
    })

    if (response.statusCode === 200) {
      const result = response.data;
      if (result.data && result.data.success_details && result.data.success_details.length > 0) {
        uni.showToast({
          title: '点亮成功',
          icon: 'success',
          duration: 2000
        })
        // 清空输入框
        formData.value.work_order = ''
        // 重置输入长度记录
        lastInputLength.value = 0
        // 先重置焦点状态
        inputFocus.value = false
        // 延迟重新设置焦点
        setTimeout(() => {
          inputFocus.value = true
        }, 300)
      } else {
        uni.showToast({
          title: result.data.failed_details?.[0]?.error || '点亮失败',
          icon: 'none',
          duration: 2000
        })
      }
    } else {
      uni.showToast({
        title: response.data.error || '点亮失败',
        icon: 'none',
        duration: 2000
      })
    }
  } catch (error) {
    uni.showToast({
      title: '网络错误，请重试',
      icon: 'none'
    })
  }
}
</script>

<style>
.container {
  padding: 40rpx;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.form-container {
  background-color: #fff;
  padding: 30rpx;
  border-radius: 12rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
}

.submit-btn {
  margin-top: 40rpx;
  width: 100%;
}

.back-btn {
  margin-top: 20rpx;
  width: 100%;
}

.uni-input {
  height: 35px;
  padding: 0 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  width: 100%;
  box-sizing: border-box;
}
</style>