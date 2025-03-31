<template>
  <view class="container">
    <uni-forms ref="form" :modelValue="formData">
      <uni-forms-item label="用户名" name="username">
        <uni-easyinput v-model="formData.username" :disabled="true" />
      </uni-forms-item>
      <uni-forms-item label="所属公司" name="company">
        <uni-easyinput v-model="formData.company" :disabled="true" />
      </uni-forms-item>
      <uni-forms-item label="所属部门" name="department">
        <uni-easyinput v-model="formData.department" :disabled="true" />
      </uni-forms-item>
      
      <uni-forms-item label="亮灯颜色" name="colors">
        <uni-data-select v-model="formData.colors" :localdata="colorOptions" />
      </uni-forms-item>
      
      <uni-forms-item label="亮灯时长" name="time">
        <view class="duration-container">
          <uni-data-select v-model="formData.time" :localdata="timeOptions" />
          <text class="duration-note">（每个档位五秒）</text>
        </view>
      </uni-forms-item>

      <uni-forms-item label="工单号标签" name="titles">
        <uni-easyinput v-model="formData.titles" placeholder="请输入工单号的自定义标签"></uni-easyinput>
      </uni-forms-item>
    </uni-forms>
    
    <button class="save-btn" type="primary" @click="handleSave">保存设置</button>
    <button class="logout-btn" type="default" @click="handleLogout">退出登录</button>
  </view>
</template>

<script>
import { apiBaseUrl } from '/config.js'

export default {
  data() {
    return {
      formData: {
        username: '',
        company: '',
        department: '',
        colors: '',
        time: '',
        titles: ''
      },
      colorOptions: [
        { value: 'red', text: '红色' },
        { value: 'green', text: '绿色' },
        { value: 'blue', text: '蓝色' },
        { value: 'yellow', text: '黄色' },
        { value: 'cyan', text: '青色' },
        { value: 'purple', text: '紫色' },
        { value: 'white', text: '白色' }
      ],
      timeOptions: [
        { value: 1, text: '5秒' },
        { value: 2, text: '10秒' },
        { value: 3, text: '15秒' },
        { value: 4, text: '20秒' },
        { value: 5, text: '30秒' }
      ]
    }
  },
  methods: {
    async handleSave() {
      try {
        const response = await uni.request({
          url: `${apiBaseUrl}/api/user/update-settings`,
          method: 'POST',
          header: {
            'Authorization': 'Basic ' + uni.getStorageSync('auth')
          },
          data: {
            colors: this.formData.colors,
            time: this.formData.time,
            titles: this.formData.titles
          }
        });

        if (response.statusCode === 200) {
          uni.showToast({ title: '设置保存成功', icon: 'success' });
        } else {
          uni.showToast({ title: '保存失败，请重试', icon: 'none' });
        }
      } catch (error) {
        uni.showToast({ title: '网络错误，请重试', icon: 'none' });
      }
    },
    handleLogout() {
      uni.showModal({
        title: '提示',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            uni.clearStorageSync();
            uni.reLaunch({
              url: '/pages/login/index'
            });
          }
        }
      });
    }
  },
  async onLoad() {
    try {
      const response = await uni.request({
        url: `${apiBaseUrl}/api/user/info`,
        method: 'GET',
        header: {
          'Authorization': 'Basic ' + uni.getStorageSync('auth')
        }
      });

      if (response.statusCode === 200) {
        this.formData = {
          username: response.data.username,
          company: response.data.company,
          department: response.data.department,
          colors: response.data.colors,
          time: response.data.time,
          titles: response.data.titles
        };
      } else {
        uni.showToast({ title: '获取用户信息失败', icon: 'none' });
      }
    } catch (error) {
      uni.showToast({ title: '网络错误', icon: 'none' });
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

.user-info-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0 30px;
  background: linear-gradient(to right, #1296db, #1890ff);
  margin: -20px -20px 20px;
  border-radius: 0 0 20px 20px;
}

.avatar-container {
  width: 80px;
  height: 80px;
  border-radius: 40px;
  overflow: hidden;
  border: 2px solid #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 10px;
}

.avatar {
  width: 100%;
  height: 100%;
}

.welcome-text {
  color: #fff;
  font-size: 18px;
  font-weight: 500;
}

.settings-form {
  background-color: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.duration-container {
  display: flex;
  align-items: center;
}

.duration-note {
  margin-left: 10px;
  font-size: 14px;
  color: #999;
}

.custom-select {
  flex: 1;
}

.button-group {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.save-btn {
  background: #1296db;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  height: 44px;
  margin-bottom: 15px;
}

.logout-btn {
  width: 100%;
  background: #f8f8f8;
  color: #dd524d;
  border: 1px solid #dd524d;
  border-radius: 8px;
  font-size: 16px;
  height: 44px;
  line-height: 44px;
}

.save-btn:active {
  background: #0f85c7;
}

.logout-btn {
  background: #fff;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  height: 44px;
  line-height: 44px;
}

.logout-btn:active {
  background: #f5f5f5;
}
</style>