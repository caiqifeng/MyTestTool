<template>
  <view class="page-container">
    <view class="user-center-page">
      <!-- 用户信息头部 -->
      <view class="user-header">
        <view class="user-avatar-section" @click="handleLogin">
          <image
            class="user-avatar"
            :src="userStore.getUserInfo?.avatar || defaultAvatar"
            mode="aspectFill"
          />
          <view class="user-info">
            <text v-if="userStore.getIsLoggedIn" class="user-name">
              {{ userStore.getUserInfo?.nickname || '用户' }}
            </text>
            <text v-else class="user-name">点击登录</text>
            <text v-if="userStore.getIsLoggedIn" class="user-level">普通会员</text>
          </view>
        </view>

        <view class="user-stats">
          <view class="stat-item" @click="handleNavigate('order', 'pending')">
            <text class="stat-value">{{ pendingPaymentCount }}</text>
            <text class="stat-label">待付款</text>
          </view>
          <view class="stat-item" @click="handleNavigate('order', 'shipped')">
            <text class="stat-value">{{ pendingShippingCount }}</text>
            <text class="stat-label">待发货</text>
          </view>
          <view class="stat-item" @click="handleNavigate('order', 'delivered')">
            <text class="stat-value">{{ pendingDeliveryCount }}</text>
            <text class="stat-label">待收货</text>
          </view>
          <view class="stat-item" @click="handleNavigate('order', 'completed')">
            <text class="stat-value">{{ pendingReviewCount }}</text>
            <text class="stat-label">待评价</text>
          </view>
        </view>
      </view>

      <!-- 我的订单 -->
      <view class="order-section">
        <view class="section-header" @click="handleNavigate('order')">
          <text class="section-title">我的订单</text>
          <text class="section-more">查看全部 ></text>
        </view>

        <view class="order-menu">
          <view class="menu-item" @click="handleNavigate('order', 'all')">
            <view class="menu-icon">📦</view>
            <text class="menu-text">全部订单</text>
          </view>
          <view class="menu-item" @click="handleNavigate('order', 'pending')">
            <view class="menu-icon">💰</view>
            <text class="menu-text">待付款</text>
          </view>
          <view class="menu-item" @click="handleNavigate('order', 'shipped')">
            <view class="menu-icon">🚚</view>
            <text class="menu-text">待发货</text>
          </view>
          <view class="menu-item" @click="handleNavigate('order', 'delivered')">
            <view class="menu-icon">📦</view>
            <text class="menu-text">待收货</text>
          </view>
          <view class="menu-item" @click="handleNavigate('order', 'completed')">
            <view class="menu-icon">⭐</view>
            <text class="menu-text">待评价</text>
          </view>
        </view>
      </view>

      <!-- 功能菜单 -->
      <view class="menu-section">
        <view class="menu-grid">
          <view class="menu-item" @click="handleNavigate('address')">
            <view class="menu-icon">📍</view>
            <text class="menu-text">收货地址</text>
          </view>
          <view class="menu-item" @click="handleNavigate('coupon')">
            <view class="menu-icon">🎫</view>
            <text class="menu-text">优惠券</text>
          </view>
          <view class="menu-item" @click="handleNavigate('collect')">
            <view class="menu-icon">❤️</view>
            <text class="menu-text">我的收藏</text>
          </view>
          <view class="menu-item" @click="handleNavigate('service')">
            <view class="menu-icon">💁</view>
            <text class="menu-text">客服中心</text>
          </view>
          <view class="menu-item" @click="handleNavigate('setting')">
            <view class="menu-icon">⚙️</view>
            <text class="menu-text">设置</text>
          </view>
          <view class="menu-item" @click="handleNavigate('about')">
            <view class="menu-icon">ℹ️</view>
            <text class="menu-text">关于我们</text>
          </view>
        </view>
      </view>

      <!-- 退出登录 -->
      <view v-if="userStore.getIsLoggedIn" class="logout-section">
        <view class="logout-btn" @click="handleLogout">
          <text class="logout-text">退出登录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '../../store/user.store'
import { useOrderStore } from '../../store/order.store'
import { authApi } from '../../utils/api/auth.api'

const userStore = useUserStore()
const orderStore = useOrderStore()
const defaultAvatar = '/static/avatars/default-avatar.jpg'

const pendingPaymentCount = ref(0)
const pendingShippingCount = ref(0)
const pendingDeliveryCount = ref(0)
const pendingReviewCount = ref(0)

onMounted(async () => {
  // 如果用户已登录，获取用户信息和订单统计
  if (userStore.getIsLoggedIn) {
    await fetchUserData()
    await fetchOrderStats()
  }
})

const fetchUserData = async () => {
  try {
    const response = await authApi.getCurrentUser()
    if (response.success && response.data) {
      userStore.setUserInfo(response.data)
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

const fetchOrderStats = async () => {
  try {
    await orderStore.fetchOrders()
    const orders = orderStore.getOrders

    // 计算订单统计（简化版）
    pendingPaymentCount.value = orders.filter(order => order.status === 'pending').length
    pendingShippingCount.value = orders.filter(order => order.status === 'paid').length
    pendingDeliveryCount.value = orders.filter(order => order.status === 'shipped').length
    pendingReviewCount.value = orders.filter(order => order.status === 'delivered').length
  } catch (error) {
    console.error('获取订单统计失败:', error)
  }
}

const handleLogin = () => {
  if (!userStore.getIsLoggedIn) {
    console.log('跳转到登录页')
    uni.navigateTo({
      url: '/pages/login/index'
    })
  }
}

const handleLogout = () => {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
      }
    }
  })
}

const handleNavigate = (type: string, subType?: string) => {
  console.log('跳转到:', type, subType)

  if (!userStore.getIsLoggedIn) {
    uni.showToast({
      title: '请先登录',
      icon: 'none',
    })
    return
  }

  // 这里可以添加具体的导航逻辑
  switch (type) {
    case 'order':
      console.log('跳转到订单页面')
      uni.navigateTo({
        url: `/pages/order-list/index?status=${subType || 'all'}`
      })
      break
    case 'address':
      console.log('跳转到地址页面')
      uni.navigateTo({
        url: '/pages/address-list/index'
      })
      break
    case 'coupon':
      console.log('跳转到优惠券页面')
      uni.navigateTo({
        url: '/pages/coupon-list/index'
      })
      break
    default:
      console.log('跳转到:', type)
  }
}
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.user-center-page {
  padding-bottom: $spacing-xl;
}

.user-header {
  background: linear-gradient(135deg, $color-primary 0%, $color-primary-light 100%);
  padding: $spacing-xl $spacing-md;
  color: $color-white;
}

.user-avatar-section {
  display: flex;
  align-items: center;
  margin-bottom: $spacing-lg;
}

.user-avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: $border-radius-circle;
  border: 3px solid rgba(255, 255, 255, 0.3);
  margin-right: $spacing-md;
}

.user-info {
  .user-name {
    display: block;
    font-size: $font-size-xl;
    font-weight: 600;
    margin-bottom: $spacing-xs;
  }

  .user-level {
    font-size: $font-size-sm;
    opacity: 0.9;
  }
}

.user-stats {
  display: flex;
  justify-content: space-around;
  text-align: center;

  .stat-item {
    flex: 1;
  }

  .stat-value {
    display: block;
    font-size: $font-size-xl;
    font-weight: 600;
    margin-bottom: $spacing-xs;
  }

  .stat-label {
    font-size: $font-size-sm;
    opacity: 0.9;
  }
}

.order-section,
.menu-section {
  background-color: $color-white;
  margin: $spacing-md;
  border-radius: $border-radius-md;
  box-shadow: $shadow-sm;
  overflow: hidden;
}

.section-header {
  padding: $spacing-md;
  border-bottom: 1px solid $color-border;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: $font-size-lg;
  font-weight: 600;
  color: $color-text-primary;
}

.section-more {
  font-size: $font-size-sm;
  color: $color-text-tertiary;
}

.order-menu {
  display: flex;
  justify-content: space-around;
  padding: $spacing-md 0;
}

.menu-section {
  .menu-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: $spacing-md;
    padding: $spacing-md;
  }
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;

  .menu-icon {
    width: 80rpx;
    height: 80rpx;
    background-color: $color-background;
    border-radius: $border-radius-circle;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40rpx;
    margin-bottom: $spacing-xs;
  }

  .menu-text {
    font-size: $font-size-sm;
    color: $color-text-secondary;
  }
}

.logout-section {
  margin: $spacing-md;

  .logout-btn {
    background-color: $color-white;
    border-radius: $border-radius-md;
    padding: $spacing-md;
    text-align: center;
    box-shadow: $shadow-sm;

    .logout-text {
      color: $color-error;
      font-weight: 500;
      font-size: $font-size-md;
    }
  }
}
</style>