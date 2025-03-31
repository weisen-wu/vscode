<template>
  <view class="container">
    <view class="form-container">
      <uni-forms ref="form" :rules="rules" :modelValue="formData">
        <uni-forms-item :label="'灯条码或' + (userTitles || '工单号')" name="identifier">
          <uni-easyinput v-model="formData.identifier" :placeholder="'请输入灯条码或' + (userTitles || '工单号')"></uni-easyinput>
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

<script>
import { apiBaseUrl } from '/config.js'

export default {
  data() {
    return {
      formData: {
        identifier: ''
      },
      userTitles: '',
      todayRecords: [],
      rules: {
        identifier: {
          rules: [{
            required: true,
            errorMessage: '请输入灯条码或工单号'
          }]
        }
      }
    }
  },
  mounted() {
    this.fetchUserInfo()
    this.fetchTodayRecords()
  },
  methods: {
    async fetchUserInfo() {
      try {
        const response = await uni.request({
          url: `${apiBaseUrl}/api/user/info`,
          method: 'GET',
          header: {
            'Authorization': 'Basic ' + uni.getStorageSync('auth')
          }
        })

        if (response.statusCode === 200) {
          this.userTitles = response.data.titles
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    },
    async fetchTodayRecords() {
      try {
        const response = await uni.request({
          url: `${apiBaseUrl}/api/lightstrip/today-unbind-records`,
          method: 'GET',
          header: {
            'Authorization': 'Basic ' + uni.getStorageSync('auth')
          }
        })

        if (response.statusCode === 200) {
          this.todayRecords = response.data
        }
      } catch (error) {
        uni.showToast({
          title: '获取记录失败',
          icon: 'none'
        })
      }
    },
    async handleSubmit() {
      try {
        const valid = await this.$refs.form.validate()
        if (!valid) return

        const response = await uni.request({
          url: `${apiBaseUrl}/api/lightstrip/unbind`,
          method: 'POST',
          header: {
            'Authorization': 'Basic ' + uni.getStorageSync('auth'),
            'Content-Type': 'application/json'
          },
          data: this.formData
        })

        if (response.statusCode === 200) {
          uni.showToast({
            title: '解绑成功',
            icon: 'success',
            duration: 2000
          })
          this.formData.identifier = ''
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
</style>