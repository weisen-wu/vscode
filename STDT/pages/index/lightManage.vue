<template>
  <view class="container">
    <view class="function-list">
      <view class="function-item" @click="navigateToBind">
        <uni-icons type="plusempty" size="30" color="#2979ff"></uni-icons>
        <text class="function-text">绑定灯条</text>
      </view>
      
      <view class="function-item" @click="navigateToUnbind">
        <uni-icons type="trash" size="30" color="#dd524d"></uni-icons>
        <text class="function-text">解绑灯条</text>
      </view>

      <view class="function-item" @click="navigateToList">
        <uni-icons type="list" size="30" color="#5cb85c"></uni-icons>
        <text class="function-text">灯条列表</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  methods: {
    navigateToBind() {
      uni.navigateTo({
        url: '/pages/index/bind'
      });
    },
    navigateToUnbind() {
      uni.navigateTo({
        url: '/pages/index/unbind'
      });
    },
    navigateToList() {
      uni.navigateTo({
        url: '/pages/index/lightstrip_list'
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