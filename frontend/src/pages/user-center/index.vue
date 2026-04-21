<template>
  <view class="page-container">
    <view class="user-center-page">
      <!-- 用户信息卡片 -->
      <view class="user-card">
        <view class="user-info-section" @click="handleLogin">
          <image
            class="user-avatar"
            :src="userStore.getUserInfo?.avatar || defaultAvatar"
            mode="aspectFill"
          />
          <view class="user-details">
            <text v-if="userStore.getIsLoggedIn" class="user-name">
              {{ userStore.getUserInfo?.nickname || '用户' }}
            </text>
            <text v-else class="user-name">点击登录</text>
            <text v-if="userStore.getIsLoggedIn" class="user-level">Cycle&Cycle 会员</text>
          </view>
        </view>

        <!-- 订单统计 -->
        <view class="order-stats">
          <view class="stat-item" @click="handleNavigate('order', 'pending')">
            <text class="stat-value">{{ pendingPaymentCount }}</text>
            <text class="stat-label">待付款</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item" @click="handleNavigate('order', 'shipped')">
            <text class="stat-value">{{ pendingShippingCount }}</text>
            <text class="stat-label">待发货</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item" @click="handleNavigate('order', 'delivered')">
            <text class="stat-value">{{ pendingDeliveryCount }}</text>
            <text class="stat-label">待收货</text>
          </view>
          <view class="stat-divider"></view>
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
          <view class="order-menu-item" @click="handleNavigate('order', 'all')">
            <text class="order-icon">📦</text>
            <text class="order-text">全部订单</text>
          </view>
          <view class="order-menu-item" @click="handleNavigate('order', 'pending')">
            <text class="order-icon">💰</text>
            <text class="order-text">待付款</text>
          </view>
          <view class="order-menu-item" @click="handleNavigate('order', 'shipped')">
            <text class="order-icon">🚚</text>
            <text class="order-text">待发货</text>
          </view>
          <view class="order-menu-item" @click="handleNavigate('order', 'delivered')">
            <text class="order-icon">📦</text>
            <text class="order-text">待收货</text>
          </view>
          <view class="order-menu-item" @click="handleNavigate('order', 'completed')">
            <text class="order-icon">⭐</text>
            <text class="order-text">待评价</text>
          </view>
        </view>
      </view>

      <!-- 功能菜单 -->
      <view class="menu-section">
        <view class="menu-grid">
          <view class="menu-item" @click="handleNavigate('address')">
            <text class="menu-icon">📍</text>
            <text class="menu-text">收货地址</text>
          </view>
          <view class="menu-item" @click="handleNavigate('coupon')">
            <text class="menu-icon">🎫</text>
            <text class="menu-text">优惠券</text>
          </view>
          <view class="menu-item" @click="handleNavigate('collect')">
            <text class="menu-icon">❤️</text>
            <text class="menu-text">我的收藏</text>
          </view>
          <view class="menu-item" @click="handleNavigate('service')">
            <text class="menu-icon">💁</text>
            <text class="menu-text">客服中心</text>
          </view>
          <view class="menu-item" @click="handleNavigate('setting')">
            <text class="menu-icon">⚙️</text>
            <text class="menu-text">设置</text>
          </view>
          <view class="menu-item" @click="handleNavigate('about')">
            <text class="menu-icon">ℹ️</text>
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
  if (!userStore.getIsLoggedIn) {
    uni.showToast({
      title: '请先登录',
      icon: 'none',
    })
    return
  }

  switch (type) {
    case 'order':
      uni.navigateTo({
        url: `/pages/order-list/index?status=${subType || 'all'}`
      })
      break
    case 'address':
      uni.navigateTo({
        url: '/pages/address-list/index'
      })
      break
    case 'coupon':
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

.page-container {
  min-height: 100vh;
  background-color: $color-background;
  padding-bottom: 120rpx;
}

.user-center-page {
  padding-bottom: $spacing-xl;
}

// 用户信息卡片
.user-card {
  margin: $spacing-lg $spacing-md;
  background: linear-gradient(135deg, #F8F3EB 0%, #EDE4D8 100%);
  border-radius: $border-radius-xl;
  padding: $spacing-xl $spacing-lg;
  box-shadow: 0 2rpx 16rpx rgba(166, 124, 82, 0.08);
}

.user-info-section {
  display: flex;
  align-items: center;
  margin-bottom: $spacing-lg;
}

.user-avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: $border-radius-circle;
  margin-right: $spacing-md;
}

.user-details {
  flex: 1;

  .user-name {
    display: block;
    font-size: $font-size-lg;
    font-weight: 500;
    color: $color-text-primary;
    margin-bottom: $spacing-xs;
  }

  .user-level {
    font-size: $font-size-xs;
    font-weight: 300;
    color: $color-text-secondary;
  }
}

// 订单统计
.order-stats {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding-top: $spacing-md;
  border-top: 1px solid $color-border;

  .stat-item {
    flex: 1;
    text-align: center;
  }

  .stat-divider {
    width: 1px;
    height: 40rpx;
    background-color: $color-border;
  }

  .stat-value {
    display: block;
    font-size: $font-size-md;
    font-weight: 500;
    color: $color-primary;
    margin-bottom: $spacing-xs;
  }

  .stat-label {
    font-size: $font-size-xs;
    font-weight: 300;
    color: $color-text-secondary;
  }
}

// 我的订单
.order-section {
  margin: 0 $spacing-md $spacing-lg;
  background: linear-gradient(135deg, #FFFFFF 0%, #FFF9F0 100%);
  border-radius: $border-radius-xl;
  padding: $spacing-lg;
  box-shadow: 0 2rpx 12rpx rgba(166, 124, 82, 0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
}

.section-title {
  font-size: $font-size-md;
  font-weight: 500;
  color: $color-text-primary;
}

.section-more {
  font-size: $font-size-xs;
  font-weight: 300;
  color: $color-text-secondary;
}

.order-menu {
  display: flex;
  justify-content: space-around;

  .order-menu-item {
    display: flex;
    flex-direction: column;
    align-items: center;

    .order-icon {
      font-size: 40rpx;
      margin-bottom: $spacing-xs;
    }

    .order-text {
      font-size: $font-size-xs;
      font-weight: 300;
      color: $color-text-secondary;
    }
  }
}

// 功能菜单
.menu-section {
  margin: 0 $spacing-md $spacing-lg;
  background: linear-gradient(135deg, #FFFFFF 0%, #FFF9F0 100%);
  border-radius: $border-radius-xl;
  padding: $spacing-lg;
  box-shadow: 0 2rpx 12rpx rgba(166, 124, 82, 0.06);
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-lg;
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;

  .menu-icon {
    font-size: 48rpx;
    margin-bottom: $spacing-sm;
  }

  .menu-text {
    font-size: $font-size-xs;
    font-weight: 300;
    color: $color-text-secondary;
  }
}

// 退出登录
.logout-section {
  margin: 0 $spacing-md;

  .logout-btn {
    background: linear-gradient(135deg, #FFFFFF 0%, #FFF9F0 100%);
    border-radius: $border-radius-xl;
    padding: $spacing-lg;
    text-align: center;
    box-shadow: 0 2rpx 12rpx rgba(166, 124, 82, 0.06);

    .logout-text {
      color: $color-error;
      font-size: $font-size-sm;
      font-weight: 400;
    }
  }
}
</style>
