<template>
  <view class="container">
    <view class="form-container">
      <uni-forms ref="formRef" :rules="rules" :modelValue="formData">
        <uni-forms-item :label="userTitles || '工单号'" name="work_order">
          <input 
            class="uni-input"
            v-model="formData.work_order" 
            :placeholder="'请输入' + (userTitles || '工单号')"
            :focus="workOrderFocus"
            @blur="handleWorkOrderBlur"
            :maxlength="MAX_WORK_ORDER_LENGTH"
            @input="handleWorkOrderInput"
          />
        </uni-forms-item>
        <uni-forms-item label="灯条码" name="mac_address">
          <input 
            class="uni-input"
            v-model="formData.mac_address" 
            :focus="macFocus"
            placeholder="请输入灯条码"
            :maxlength="MAX_MAC_LENGTH"
            @input="handleMacInput"
          />
        </uni-forms-item>
      </uni-forms>
      <button class="submit-btn" type="primary" @click="handleSubmit">提交</button>
    </view>
    <view class="records-container">
      <view class="records-title">今日绑定记录</view>
      <scroll-view scroll-y class="records-list">
        <uni-list>
          <uni-list-item v-for="record in todayRecords" :key="record.id"
            :title="'灯条码: ' + record.mac_address"
            :note="'绑定号: ' + record.work_order"
          ></uni-list-item>
        </uni-list>
      </scroll-view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { apiBaseUrl } from '/config.js'

const formRef = ref(null)
const workOrderFocus = ref(false)
const macFocus = ref(false)

const formData = ref({
  mac_address: '',
  work_order: ''
})

const userTitles = ref('')
const todayRecords = ref([])

// 输入长度限制
const MAX_WORK_ORDER_LENGTH = 16
const MAX_MAC_LENGTH = 12

// 上一次输入的长度
const lastWorkOrderLength = ref(0)
const lastMacLength = ref(0)

// 处理工单号输入
const handleWorkOrderInput = (e) => {
  const value = e.detail.value
  formData.value.work_order = value
  
  // 使用延时等待扫码数据完整录入，增加延时时间以确保扫码数据完整
  setTimeout(() => {
    // 增加延时时间到800毫秒，确保扫码数据完整录入后再验证格式
    // 检查是否包含'-'符号
    if (!formData.value.work_order.includes('-')) {
      uni.showToast({
        title: '工单号格式错误，必须包含"-"符号',
        icon: 'none',
        duration: 2000
      })
      // 清空输入内容和formData中的值
      formData.value.work_order = ''
      // 保持焦点在工单号输入框
      workOrderFocus.value = true
      return
    }
    // 检查长度限制
    if (formData.value.work_order.length > MAX_WORK_ORDER_LENGTH) {
      uni.showToast({
        title: '工单号不能超过' + MAX_WORK_ORDER_LENGTH + '位',
        icon: 'none',
        duration: 1500
      })
    }
    lastWorkOrderLength.value = formData.value.work_order.length
    // 当输入正确的工单号格式时，自动切换到灯条码输入框
    workOrderFocus.value = false
    macFocus.value = true
  }, 800) // 增加延时等待时间，确保扫码数据完整录入
}

// 处理灯条码输入
const handleMacInput = (e) => {
  const value = e.detail.value
  // 检查是否包含工单号特有的'-'符号
  if (value.includes('-')) {
    uni.showToast({
      title: '检测到工单号格式，请在正确的输入框中输入',
      icon: 'none',
      duration: 3000
    })
    // 清空输入内容和formData中的值
    e.detail.value = ''
    formData.value.mac_address = ''
    return
  }
  // 只在超出最大长度时显示提示
  if (value.length > MAX_MAC_LENGTH) {
    uni.showToast({
      title: '灯条码不能超过' + MAX_MAC_LENGTH + '位',
      icon: 'none',
      duration: 1500
    })
  }
  lastMacLength.value = value.length
  formData.value.mac_address = value
}

const rules = {
  mac_address: {
    rules: [{
      required: true,
      errorMessage: '请输入灯条码'
    }, {
      validateFunction: (rule, value, data, callback) => {
        if (value.length > MAX_MAC_LENGTH) {
          callback('灯条码不能超过' + MAX_MAC_LENGTH + '位')
        }
        return true
      }
    }]
  },
  work_order: {
    rules: [{
      required: true,
      errorMessage: '请输入绑定号'
    }, {
      validateFunction: (rule, value, data, callback) => {
        if (value.length > MAX_WORK_ORDER_LENGTH) {
          callback('工单号不能超过' + MAX_WORK_ORDER_LENGTH + '位')
        }
        return true
      }
    }]
  }
}

onMounted(() => {
  // 页面加载后延迟聚焦到工单号输入框
  setTimeout(() => {
    // 增加延时时间到800毫秒，确保扫码数据完整录入后再验证格式
    workOrderFocus.value = true
  }, 300)
  
  fetchUserInfo()
  fetchTodayRecords()
})

// 监听工单号变化
watch(() => formData.value.work_order, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    // 如果新值的长度大于旧值的长度，说明是新输入或扫码输入
    if (newVal.length > (oldVal?.length || 0)) {
      // 只在超出最大长度时显示提示
      if (newVal.length > MAX_WORK_ORDER_LENGTH) {
        uni.showToast({
          title: '工单号不能超过' + MAX_WORK_ORDER_LENGTH + '位',
          icon: 'none',
          duration: 1500
        })
      }
    }
  }
})

// 监听灯条码变化
watch(() => formData.value.mac_address, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    // 如果新值的长度大于旧值的长度，说明是新输入或扫码输入
    if (newVal.length > MAX_MAC_LENGTH) {
      uni.showToast({
        title: '灯条码不能超过' + MAX_MAC_LENGTH + '位',
        icon: 'none',
        duration: 1500
      })
    }
  }
})

// 处理工单号失焦事件
const handleWorkOrderBlur = () => {
  workOrderFocus.value = false
}

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
      url: `${apiBaseUrl}/api/lightstrip/today-records`,
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
    const valid = await formRef.value.validate()
    if (!valid) return

    // 检查MAC地址是否以'AD1'开头，如果不是则添加前缀
    if (!formData.value.mac_address.toUpperCase().startsWith('AD1')) {
      formData.value.mac_address = 'AD1' + formData.value.mac_address
    }

    // 验证灯条码不能仅包含'AD1'前缀
    if (formData.value.mac_address.toUpperCase() === 'AD1') {
      uni.showToast({
        title: '请输入完整的灯条码',
        icon: 'none',
        duration: 2000
      })
      return
    }

    const response = await uni.request({
      url: `${apiBaseUrl}/api/lightstrip/bind`,
      method: 'POST',
      header: {
        'Authorization': 'Basic ' + uni.getStorageSync('auth'),
        'Content-Type': 'application/json'
      },
      data: formData.value
    })

    if (response.statusCode === 200) {
      uni.showToast({
        title: '绑定成功',
        icon: 'success',
        duration: 2000
      })
      // 清空表单数据
      formData.value.mac_address = ''
      formData.value.work_order = ''
      fetchTodayRecords()
      
      // 重置焦点状态
      macFocus.value = false
      // 延迟设置工单号输入框焦点，确保在表单清空后再聚焦
      setTimeout(() => {
    // 增加延时时间到800毫秒，确保扫码数据完整录入后再验证格式
        workOrderFocus.value = true
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