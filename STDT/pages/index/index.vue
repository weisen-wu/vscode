<template>
  <view class="container">
    <view class="header">
      <text class="welcome">欢迎, {{userInfo.username}}</text>
      <text class="company">{{userInfo.company}}</text>
    </view>
    
    <view class="stats-grid">
      <view class="stats-card">
        <view class="stats-value">{{stats.totalBaseStations}}</view>
        <view class="stats-label">基站总数</view>
        <view class="stats-icon">
          <uni-icons type="wifi" size="24" color="#2979ff"></uni-icons>
        </view>
      </view>
      
      <view class="stats-card">
        <view class="stats-value">{{stats.totalLightStrips}}</view>
        <view class="stats-label">灯条总数</view>
        <view class="stats-icon">
          <uni-icons type="list" size="24" color="#ff9900"></uni-icons>
        </view>
      </view>
    </view>
    
    <view class="section-title">基站列表</view>
    <view class="station-list">
      <view class="station-header">
        <text class="header-item">位置</text>
        <text class="header-item">IP地址</text>
        <text class="header-item">描述</text>
        <text class="header-item">状态</text>
      </view>
      <view v-for="(station, index) in companyStations" :key="index" class="station-item">
        <view class="station-info">
          <text class="station-location">{{station.location}}</text>
          <text class="station-ip">{{station.ip_address}}</text>
          <text class="station-desc">{{station.description}}</text>
          <text :class="['station-status', station.status === 'online' ? 'status-online' : 'status-offline']">{{station.status === 'online' ? '在线' : '离线'}}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { apiBaseUrl } from '/config.js'
export default {
  data() {
    return {
      userInfo: {},
      stats: {
        totalBaseStations: 0,
        totalLightStrips: 0
      },
      companyStations: [],
      pingTimer: null
    }
  },
  onShow() {
    const userInfo = uni.getStorageSync('userInfo')
    if (!userInfo) {
      uni.redirectTo({
        url: '/pages/login/index'
      })
      return
    }
    this.userInfo = userInfo
    this.fetchDashboardData()
    this.fetchCompanyStations()
  },
  methods: {
    async fetchDashboardData() {
      try {
        const response = await uni.request({
          url: `${apiBaseUrl}/api/dashboard/stats`,
          method: 'GET',
          header: {
            'Authorization': 'Basic ' + uni.getStorageSync('auth')
          }
        })

        if (response.statusCode === 200) {
          this.stats = response.data
        }
      } catch (error) {
        uni.showToast({
          title: '获取数据失败',
          icon: 'none'
        })
      }
    },
    async fetchCompanyStations() {
      try {
        const response = await uni.request({
          url: `${apiBaseUrl}/api/dashboard/company-stations`,
          method: 'GET',
          header: {
            'Authorization': 'Basic ' + uni.getStorageSync('auth')
          }
        })

        if (response.statusCode === 200) {
          this.companyStations = response.data.map(station => ({
            ...station,
            status: 'checking'
          }))
          this.checkStationsStatus()
        }
      } catch (error) {
        uni.showToast({
          title: '获取基站列表失败',
          icon: 'none'
        })
      }
    },
    async checkStationStatus(station) {
      try {
        const response = await uni.request({
          url: `${apiBaseUrl}/estatione/api/ping?ip=${station.ip_address}`,
          method: 'GET'
        })
        if (response.statusCode === 200) {
          station.status = response.data.status
        }
      } catch (error) {
        station.status = 'offline'
      }
    },
    checkStationsStatus() {
      this.companyStations.forEach(station => {
        this.checkStationStatus(station)
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

.header {
  margin-bottom: 40rpx;
}

.welcome {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  display: block;
}

.company {
  font-size: 28rpx;
  color: #666;
  margin-top: 8rpx;
  display: block;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.stats-card {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 24rpx;
  position: relative;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
}

.stats-value {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 8rpx;
}

.stats-label {
  font-size: 24rpx;
  color: #666;
}

.stats-icon {
  position: absolute;
  top: 24rpx;
  right: 24rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.station-list {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
}

.station-item {
  display: flex;
  align-items: center;
  padding: 16rpx;
  border-bottom: 1px solid #f0f0f0;
}

.station-item:last-child {
  border-bottom: none;
}

.station-header {
  display: flex;
  padding: 20rpx 16rpx;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.header-item {
  flex: 1;
  font-size: 28rpx;
  color: #666;
  font-weight: bold;
}

.station-info {
  flex: 1;
  display: flex;
}

.station-location,
.station-ip,
.station-desc,
.station-status {
  flex: 1;
  font-size: 28rpx;
  padding: 4rpx 0;
}

.station-location {
  color: #333;
  font-weight: bold;
}

.status-online {
  color: #16a34a;
}

.status-offline {
  color: #dc2626;
}

.station-ip {
  font-size: 24rpx;
  color: #666;
  display: block;
  margin-bottom: 4rpx;
}

.station-desc {
  font-size: 24rpx;
  color: #999;
  display: block;
}
</style>

methods: {
  navigateToBind() {
    uni.navigateTo({
      url: '/pages/index/bind'
    })
  },
  navigateToLightList() {
    uni.navigateTo({
      url: '/pages/index/lightstrip_list'
    })
  }
}
