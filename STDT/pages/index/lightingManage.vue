<template>
  <view class="container">
    <view class="function-list">
      <view class="function-item" @click="navigateToLight">
        <uni-icons type="list" size="30" color="#f0ad4e"></uni-icons>
        <text class="function-text">点亮灯条</text>
      </view>
      
      <view class="function-item" @click="navigateToBatchLight">
        <uni-icons type="list" size="30" color="#009688"></uni-icons>
        <text class="function-text">批量点亮灯条</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  methods: {
    navigateToLight() {
      uni.navigateTo({
        url: '/pages/index/light'
      });
    },
    navigateToBatchLight() {
      uni.navigateTo({
        url: '/pages/index/batchLight'
      });
    }
  }
};
</script>

<style>
.container {
  padding: 20px;
  background-color: #f8f8f8;
  min-height: 100vh;
}

.function-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.function-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.function-text {
  margin-left: 15px;
  font-size: 16px;
  color: #333;
}
</style>