<template>
  <view class="container">
    <view class="form-container">
      <uni-forms ref="form" :rules="rules" :modelValue="formData">
        <uni-forms-item :label="userTitles || '工单号'" name="work_order">
          <uni-easyinput v-model="formData.work_order" :placeholder="'请输入' + (userTitles || '工单号')"></uni-easyinput>
        </uni-forms-item>
      </uni-forms>
      <button class="submit-btn" type="primary" @click="handleSubmit">点亮灯条</button>
    </view>
  </view>
</template>

<script>
import { apiBaseUrl } from '@/config.js'

export default {
  data() {
    return {
      formData: {
        work_order: ''
      },
      userTitles: '',
      rules: {
        work_order: {
          rules: [{
            required: true,
            errorMessage: '请输入工单号'
          }]
        }
      }
    }
  },
  mounted() {
    this.fetchUserInfo()
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
    async handleSubmit() {
      try {
        const valid = await this.$refs.form.validate()
        if (!valid) return

        const response = await uni.request({
          url: `${apiBaseUrl}/api/lightstrip/light`,
          method: 'POST',
          header: {
            'Authorization': 'Basic ' + uni.getStorageSync('auth')
          },
          data: this.formData
        })

        if (response.statusCode === 200) {
          const result = response.data;
          if (result.data && result.data.success_details && result.data.success_details.length > 0) {
            uni.showModal({
              title: '操作成功',
              content: '灯条已成功点亮',
              showCancel: false,
              success: function() {
                // 重新加载页面
                uni.redirectTo({
                  url: '/pages/index/light'
                })
              }
            })
          } else {
            uni.showModal({
              title: '操作失败',
              content: result.data.failed_details?.[0]?.error || '点亮灯条失败',
              showCancel: false
            })
          }
        } else {
          uni.showModal({
            title: '操作失败',
            content: response.data.error || '点亮灯条失败',
            showCancel: false
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

.back-btn {
  margin-top: 20rpx;
  width: 100%;
}
</style>