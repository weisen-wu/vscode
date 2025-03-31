<template>
  <view class="container">
    <view class="search-box">
      <uni-easyinput v-model="searchQuery" placeholder="输入MAC地址或标签搜索" @input="handleSearch"></uni-easyinput>
    </view>
    
    <view class="list-container">
      <uni-list v-if="lightstrips.length > 0">
        <uni-list-item v-for="item in lightstrips" :key="item.mac_address"
          :title="item.mac_address"
          :note="`${item.titles || '绑定号: ' + item.work_order} | 操作员: ${item.operator_name || '未知'}`"
        ></uni-list-item>
      </uni-list>
      <view v-else class="empty-state">
        <text>暂无灯条数据</text>
      </view>
    </view>
    
    <uni-pagination
      :total="total"
      :pageSize="pageSize"
      :current="currentPage"
      @change="handlePageChange"
    ></uni-pagination>
  </view>
</template>

<script>
import { apiBaseUrl } from '/config.js'

export default {
  data() {
    return {
      lightstrips: [],
      searchQuery: '',
      currentPage: 1,
      pageSize: 10,
      total: 0
    }
  },
  onLoad() {
    this.fetchLightstrips()
  },
  methods: {
    async fetchLightstrips() {
      try {
        const response = await uni.request({
          url: `${apiBaseUrl}/api/lightstrip/list?page=${this.currentPage}&per_page=${this.pageSize}&query=${this.searchQuery}`,
          method: 'GET',
          header: {
            'Authorization': 'Basic ' + uni.getStorageSync('auth')
          }
        })

        if (response.statusCode === 200) {
          this.lightstrips = response.data.items
          this.total = response.data.total
        } else {
          uni.showToast({
            title: '获取数据失败',
            icon: 'none'
          })
        }
      } catch (error) {
        uni.showToast({
          title: '网络错误',
          icon: 'none'
        })
      }
    },
    handleSearch(value) {
      this.currentPage = 1
      this.searchQuery = value
      this.fetchLightstrips()
    },
    handlePageChange(e) {
      this.currentPage = e.current
      this.fetchLightstrips()
    }
  }
}
</script>

<style>
.container {
  padding: 20px;
  background-color: #f8f8f8;
  min-height: 100vh;
}

.search-box {
  margin-bottom: 20px;
}

.list-container {
  background-color: #fff;
  border-radius: 12px;
  margin-bottom: 20px;
  overflow: hidden;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
  color: #999;
}
</style>