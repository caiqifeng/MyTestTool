<template>
  <view>
    <!-- 页面内容 -->
    <slot />
  </view>
</template>

<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from './src/stores/user.store'
import './src/styles/global.scss'

// 初始化用户状态
const userStore = useUserStore()

onLaunch(() => {
  console.log('App Launch')

  // 检查登录状态
  userStore.checkLoginStatus()

  // 初始化应用配置
  initAppConfig()
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})

// 初始化应用配置
const initAppConfig = () => {
  // 设置系统信息
  const systemInfo = uni.getSystemInfoSync()
  console.log('System Info:', systemInfo)

  // 设置导航栏样式
  uni.setNavigationBarColor({
    frontColor: '#000000',
    backgroundColor: '#ffffff'
  })

  // 设置TabBar样式
  uni.setTabBarStyle({
    color: '#7A7E83',
    selectedColor: '#FF6B35',
    backgroundColor: '#ffffff',
    borderStyle: 'black'
  })
}

// 全局错误处理
const onError = (error: any) => {
  console.error('Global Error:', error)

  // 可以在这里添加错误上报逻辑
  // reportError(error)

  // 显示友好错误提示
  uni.showToast({
    title: '系统繁忙，请稍后重试',
    icon: 'none',
    duration: 2000
  })
}

// 监听全局错误
if (typeof window !== 'undefined') {
  window.addEventListener('error', onError)
  window.addEventListener('unhandledrejection', (event) => {
    onError(event.reason)
  })
}
</script>

<style>
/* 全局样式重置 */
page {
  background-color: #f8f8f8;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

/* 解决iOS滚动回弹问题 */
::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
  color: transparent;
}

/* 通用样式类 */
.text-primary {
  color: #FF6B35;
}

.bg-primary {
  background-color: #FF6B35;
}

.border-primary {
  border-color: #FF6B35;
}

.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>