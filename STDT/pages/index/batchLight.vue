<template>
  <view class="container">
    <view class="search-container">
      <uni-forms ref="form" :rules="rules" :modelValue="formData">
        <uni-forms-item label="领料单号" name="po_order">
          <view class="search-box">
            <uni-easyinput v-model="formData.po_order" placeholder="请输入领料单号"></uni-easyinput>
            <button class="search-btn" type="primary" @click="handleSearch">查询</button>
          </view>
        </uni-forms-item>
      </uni-forms>
    </view>
    
    <view class="list-container" v-if="workOrders.length > 0">
      <view class="list-header">
        <text class="header-item">工单号</text>
        <text class="header-item">品号</text>
        <text class="header-item">数量</text>
        <text class="header-item">结果</text>
      </view>
      <scroll-view scroll-y class="list-content">
        <view class="list-item" v-for="(item, index) in workOrders" :key="index">
          <text class="item-text">{{ item.work_order }}</text>
          <text class="item-text">{{ item.work_ph }}</text>
          <text class="item-text">{{ item.work_sl }}</text>
          <text class="item-text" :class="{'success': item.result === '成功', 'error': item.result === '失败'}">{{ item.result || '-' }}</text>
        </view>
      </scroll-view>
      <button class="batch-btn" type="primary" @click="handleBatchLight" :disabled="isProcessing">批量点亮</button>
      <button class="batch-btn" type="warn" @click="handleBatchUnbind" :disabled="isProcessing">批量解绑</button>
    </view>
    
    <view class="empty-state" v-else>
      <text>暂无数据</text>
    </view>
  </view>
</template>

<script>
import { apiBaseUrl } from '/config.js'

export default {
  data() {
    return {
      formData: {
        po_order: ''
      },
      rules: {
        po_order: {
          rules: [{
            required: true,
            errorMessage: '请输入领料单号'
          }]
        }
      },
      workOrders: [],
      isProcessing: false
    }
  },
  methods: {
    async handleSearch() {
      try {
        const valid = await this.$refs.form.validate()
        if (!valid) return

        const response = await uni.request({
          url: `${apiBaseUrl}/api/lightstrip/search-po`,
          method: 'POST',
          header: {
            'Authorization': 'Basic ' + uni.getStorageSync('auth')
          },
          data: this.formData
        })

        if (response.statusCode === 200) {
          this.workOrders = response.data.map(item => ({
            ...item,
            result: item.is_bound ? '' : '未绑定'
          }))
        } else {
          uni.showModal({
            title: '查询失败',
            content: response.data.error || '获取工单信息失败',
            showCancel: false
          })
        }
      } catch (error) {
        uni.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
      }
    },
    async handleBatchLight() {
      if (this.isProcessing) return
      this.isProcessing = true

      try {
        const workOrderList = this.workOrders.map(item => item.work_order)
        const response = await uni.request({
          url: `${apiBaseUrl}/api/lightstrip/light`,
          method: 'POST',
          header: {
            'Authorization': 'Basic ' + uni.getStorageSync('auth')
          },
          data: {
            work_order: workOrderList
          }
        })

        if (response.statusCode === 200) {
          const { success_details, failed_details } = response.data.data
          // 更新工单状态，只更新已绑定工单的结果
          this.workOrders = this.workOrders.map(item => {
            // 如果当前工单状态是'未绑定'，保持不变
            if (item.result === '未绑定') {
              return item
            }
            // 否则根据点亮结果更新状态
            return {
              ...item,
              result: success_details.some(s => s.work_order === item.work_order) ? '成功' : '失败'
            }
          })
        } else {
          // 如果请求失败，将所有工单标记为失败
          this.workOrders = this.workOrders.map(item => ({
            ...item,
            result: '失败'
          }))
        }
      } catch (error) {
        // 发生错误时，将所有工单标记为失败
        this.workOrders = this.workOrders.map(item => ({
          ...item,
          result: '失败'
        }))
      } finally {
        this.isProcessing = false
      }
    },
    async handleBatchUnbind() {
      if (this.isProcessing) return
      
      const res = await uni.showModal({
        title: '确认解绑',
        content: '确定要批量解绑选中的工单吗？',
        confirmText: '确认解绑',
        cancelText: '取消'
      })
      
      if (!res.confirm) return
      
      this.isProcessing = true

      try {
        // 过滤出已绑定的工单
        const boundWorkOrders = this.workOrders
          .filter(item => item.result !== '未绑定')
          .map(item => item.work_order)

        if (boundWorkOrders.length === 0) {
          uni.showToast({
            title: '没有可解绑的工单',
            icon: 'none'
          })
          return
        }

        const response = await uni.request({
          url: `${apiBaseUrl}/api/lightstrip/unbind`,
          method: 'POST',
          header: {
            'Authorization': 'Basic ' + uni.getStorageSync('auth')
          },
          data: {
            identifiers: boundWorkOrders
          }
        })

        if (response.statusCode === 200) {
          const { success_unbinds, failed_unbinds } = response.data.data
          // 更新工单状态
          this.workOrders = this.workOrders.map(item => {
            const successUnbind = success_unbinds.find(s => s.work_order === item.work_order)
            const failedUnbind = failed_unbinds.find(f => f.identifier === item.work_order)
            
            if (successUnbind) {
              return { ...item, result: '已解绑' }
            } else if (failedUnbind) {
              return { ...item, result: '解绑失败' }
            }
            return item
          })

          uni.showToast({
            title: '批量解绑完成',
            icon: 'success'
          })
        } else {
          uni.showModal({
            title: '解绑失败',
            content: response.data.error || '批量解绑失败',
            showCancel: false
          })
        }
      } catch (error) {
        uni.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
      } finally {
        this.isProcessing = false
      }
    },
    goBack() {
      uni.navigateTo({
        url: '/pages/index/index'
      })
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

.search-container {
  background-color: #fff;
  padding: 30rpx;
  border-radius: 12rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
  margin-bottom: 20rpx;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.search-btn {
  width: 160rpx;
  height: 70rpx;
  line-height: 70rpx;
  margin: 0;
  font-size: 28rpx;
}

.list-container {
  background-color: #fff;
  border-radius: 12rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
  padding: 20rpx;
}

.list-header {
  display: flex;
  padding: 20rpx;
  border-bottom: 1px solid #eee;
  font-weight: bold;
}

.list-content {
  max-height: 800rpx;
}

.list-item {
  display: flex;
  padding: 20rpx;
  border-bottom: 1px solid #eee;
}

.header-item,
.item-text {
  flex: 1;
  text-align: center;
  font-size: 28rpx;
}

.success {
  color: #10b981;
}

.error {
  color: #ef4444;
}

.batch-btn {
  margin: 20rpx auto;
  width: 80%;
  margin-top: 30rpx;
}

.empty-state {
  text-align: center;
  padding: 40rpx;
  color: #666;
}
</style>