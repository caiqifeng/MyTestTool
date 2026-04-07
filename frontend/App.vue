<template>
  <view>
    <slot />
  </view>
</template>

<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from './src/store/user.store'

// 应用启动
onLaunch(() => {
  console.log('App Launch')

  // 检查登录状态
  const userStore = useUserStore()
  userStore.checkLoginStatus()
})

// 应用显示
onShow(() => {
  console.log('App Show')
})

// 应用隐藏
onHide(() => {
  console.log('App Hide')
})
</script>

<style lang="scss">
/* 导入全局样式 */
@import './src/styles/global.scss';
</style>