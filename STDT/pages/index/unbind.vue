<template>
  <view class="container">
    <view class="form-container">
      <uni-forms ref="form" :rules="rules" :modelValue="formData">
        <uni-forms-item :label="'灯条码或' + (userTitles || '工单号')" name="identifier">
          <input 
            class="uni-input"
            v-model="formData.identifier" 
            :placeholder="'请输入灯条码或' + (userTitles || '工单号')"
            :focus="inputFocus"
            :maxlength="MAX_INPUT_LENGTH"
            @input="handleInput"
          />
        </uni-forms-item>
      </uni-forms>
      <button class="submit-btn" type="primary" @click="handleSubmit">解绑灯条</button>
    </view>
    <view class="records-container" v-if="todayRecords.length > 0">
      <view class="records-title">今日解绑记录</view>
      <scroll-view scroll-y class="records-list">
        <uni-list>
          <uni-list-item v-for="record in todayRecords" :key="record.id"
            :title="'灯条码: ' + record.mac_address"
            :note="record.titles || '工单号: ' + record.work_order">
          </uni-list-item>
        </uni-list>
      </scroll-view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiBaseUrl } from '/config.js'

const form = ref(null)
const inputFocus = ref(false)
const MAX_INPUT_LENGTH = 20 // 设置最大输入长度
const lastInputLength = ref(0)

const formData = ref({
  identifier: ''
})

const userTitles = ref('')
const todayRecords = ref([])

const rules = {
  identifier: {
    rules: [{
      required: true,
      errorMessage: '请输入灯条码或工单号'
    }, {
      validateFunction: (rule, value, data, callback) => {
        if (value.length > MAX_INPUT_LENGTH) {
          callback('输入长度不能超过' + MAX_INPUT_LENGTH + '位')
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
      title: '输入已达到最大长度' + MAX_INPUT_LENGTH + '位',
      icon: 'none',
      duration: 1500
    })
  }
  lastInputLength.value = value.length
  formData.value.identifier = value
}

onMounted(() => {
  // 页面加载后延迟聚焦到输入框
  setTimeout(() => {
    inputFocus.value = true
  }, 300)
  
  fetchUserInfo()
  fetchTodayRecords()
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

const fetchTodayRecords = async () => {
  try {
    const response = await uni.request({
      url: `${apiBaseUrl}/api/lightstrip/today-unbind-records`,
      method: 'GET',
      header: {
        'Authorization': 'Basic ' + uni.getStorageSync('auth')
      }
    })

    if (response.statusCode === 200) {
      todayRecords.value = response.data
    }
  } catch (error) {
    uni.showToast({
      title: '获取记录失败',
      icon: 'none'
    })
  }
}

const handleSubmit = async () => {
  try {
    const valid = await form.value.validate()
    if (!valid) return

    const response = await uni.request({
      url: `${apiBaseUrl}/api/lightstrip/unbind`,
      method: 'POST',
      header: {
        'Authorization': 'Basic ' + uni.getStorageSync('auth'),
        'Content-Type': 'application/json'
      },
      data: formData.value
    })

    if (response.statusCode === 200) {
      uni.showToast({
        title: '解绑成功',
        icon: 'success',
        duration: 2000
      })
      // 清空输入框
      formData.value.identifier = ''
      // 重新获取记录
      fetchTodayRecords()
      // 重置输入长度记录
      lastInputLength.value = 0
      // 延迟设置输入框焦点，确保在清空后再聚焦
      setTimeout(() => {
        inputFocus.value = true
      }, 100)
    } else {
      uni.showToast({
        title: response.data.error || '操作失败',
        icon: 'none'
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

.records-container {
  margin-top: 40rpx;
  background-color: #fff;
  padding: 30rpx;
  border-radius: 12rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
}

.records-title {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.records-list {
  max-height: 600rpx;
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