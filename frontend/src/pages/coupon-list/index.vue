<template>
  <view class="page-container">
    <view class="coupon-page">
      <!-- 头部 -->
      <view class="coupon-header">
        <text class="coupon-title">我的优惠券</text>
      </view>

      <!-- 状态过滤 -->
      <view class="filter-section">
        <scroll-view class="filter-scroll" scroll-x>
          <view class="filter-tabs">
            <view
              class="filter-tab"
              :class="{ 'active': filterStatus === 'all' }"
              @click="setFilterStatus('all')"
            >
              <text class="tab-text">全部</text>
            </view>
            <view
              class="filter-tab"
              :class="{ 'active': filterStatus === 'available' }"
              @click="setFilterStatus('available')"
            >
              <text class="tab-text">可用</text>
            </view>
            <view
              class="filter-tab"
              :class="{ 'active': filterStatus === 'used' }"
              @click="setFilterStatus('used')"
            >
              <text class="tab-text">已使用</text>
            </view>
            <view
              class="filter-tab"
              :class="{ 'active': filterStatus === 'expired' }"
              @click="setFilterStatus('expired')"
            >
              <text class="tab-text">已过期</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 优惠券列表 -->
      <view class="coupons-section">
        <view v-if="isLoading" class="loading-section">
          <text class="loading-text">加载中...</text>
        </view>

        <view v-else-if="error" class="error-section">
          <text class="error-text">{{ error }}</text>
          <view class="retry-btn" @click="fetchCoupons">
            <text class="retry-text">重试</text>
          </view>
        </view>

        <view v-else-if="filteredCoupons.length === 0" class="empty-section">
          <view class="empty-icon">🎫</view>
          <text class="empty-text">暂无优惠券</text>
          <text class="empty-subtext">快去领取优惠券吧</text>
          <view class="empty-btn" @click="handleGetCoupons">
            <text class="empty-btn-text">领取优惠券</text>
          </view>
        </view>

        <view v-else class="coupons-list">
          <view
            v-for="coupon in filteredCoupons"
            :key="coupon._id"
            class="coupon-card"
            :class="getCouponStatusClass(coupon)"
          >
            <!-- 优惠券信息 -->
            <view class="coupon-info">
              <view class="coupon-main">
                <text class="coupon-name">{{ coupon.name }}</text>
                <text class="coupon-discount">
                  {{ coupon.discountType === 'fixed' ? '¥' : '' }}{{ coupon.discountValue }}{{ coupon.discountType === 'percentage' ? '%' : '' }} OFF
                </text>
              </view>
              <text v-if="coupon.description" class="coupon-desc">
                {{ coupon.description }}
              </text>
              <view class="coupon-details">
                <text class="coupon-code">代码: {{ coupon.code }}</text>
                <text class="coupon-expiry">
                  有效期: {{ formatDate(coupon.startDate) }} - {{ formatDate(coupon.endDate) }}
                </text>
              </view>
              <view class="coupon-conditions">
                <text v-if="coupon.minPurchaseAmount" class="condition-item">
                  满¥{{ coupon.minPurchaseAmount.toFixed(2) }}可用
                </text>
                <text v-if="coupon.maxDiscountAmount" class="condition-item">
                  最高减¥{{ coupon.maxDiscountAmount.toFixed(2) }}
                </text>
                <text v-if="coupon.usageLimit" class="condition-item">
                  剩余{{ coupon.usageLimit - coupon.usedCount }}次
                </text>
              </view>
            </view>

            <!-- 状态标签 -->
            <view class="coupon-status" :class="getCouponStatusClass(coupon)">
              <text class="status-text">{{ getCouponStatusText(coupon) }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 领取优惠券按钮 -->
      <view v-if="filteredCoupons.length > 0" class="get-coupon-section">
        <view class="get-coupon-btn" @click="handleGetCoupons">
          <text class="get-coupon-text">领取更多优惠券</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { couponApi } from '../../utils/api/coupon.api'
import dayjs from 'dayjs'

interface Coupon {
  _id: string
  code: string
  name: string
  description?: string
  discountType: 'percentage' | 'fixed'
  discountValue: number
  minPurchaseAmount?: number
  maxDiscountAmount?: number
  startDate: string
  endDate: string
  usageLimit?: number
  usedCount: number
  isActive: boolean
  applicableCategories?: string[]
  excludedProducts?: string[]
  createdAt: string
  updatedAt: string
  isUsed?: boolean
  isValid?: boolean
}

const coupons = ref<Coupon[]>([])
const filterStatus = ref('all')
const isLoading = ref(false)
const error = ref<string | null>(null)

// 过滤优惠券
const filteredCoupons = computed(() => {
  const now = new Date()

  return coupons.value.filter(coupon => {
    const endDate = new Date(coupon.endDate)
    const isExpired = endDate < now
    const isAvailable = coupon.isActive && !isExpired && coupon.usedCount < (coupon.usageLimit || Infinity)

    switch (filterStatus.value) {
      case 'available':
        return isAvailable && !coupon.isUsed
      case 'used':
        return coupon.isUsed
      case 'expired':
        return isExpired || !coupon.isActive
      case 'all':
      default:
        return true
    }
  })
})

// 获取优惠券状态类
const getCouponStatusClass = (coupon: Coupon): string => {
  const now = new Date()
  const endDate = new Date(coupon.endDate)
  const isExpired = endDate < now

  if (coupon.isUsed) return 'used'
  if (isExpired || !coupon.isActive) return 'expired'
  return 'available'
}

// 获取优惠券状态文本
const getCouponStatusText = (coupon: Coupon): string => {
  const statusClass = getCouponStatusClass(coupon)
  switch (statusClass) {
    case 'used':
      return '已使用'
    case 'expired':
      return '已过期'
    case 'available':
    default:
      return '可用'
  }
}

// 获取优惠券列表
const fetchCoupons = async () => {
  isLoading.value = true
  error.value = null

  try {
    // 这里使用用户优惠券API
    const response = await couponApi.getUserCoupons()
    if (response.success && response.data.coupons) {
      coupons.value = response.data.coupons
    } else {
      throw new Error(response.message || '获取优惠券列表失败')
    }
  } catch (err: any) {
    error.value = err.message || '获取优惠券列表失败'
    console.error('获取优惠券列表失败:', err)
  } finally {
    isLoading.value = false
  }
}

// 设置筛选状态
const setFilterStatus = (status: string) => {
  filterStatus.value = status
}

// 格式化日期
const formatDate = (dateString: string): string => {
  try {
    return dayjs(dateString).format('YYYY-MM-DD')
  } catch {
    return dateString
  }
}

// 领取优惠券
const handleGetCoupons = () => {
  uni.showToast({
    title: '优惠券领取功能开发中',
    icon: 'none'
  })
  // TODO: 实现优惠券领取页面
}

onMounted(() => {
  fetchCoupons()
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.coupon-page {
  padding-bottom: $spacing-xl;
}

.coupon-header {
  padding: $spacing-lg $spacing-md;
  background-color: $color-white;
  border-bottom: 1px solid $color-border;

  .coupon-title {
    font-size: $font-size-xl;
    font-weight: 600;
    color: $color-text-primary;
  }
}

.filter-section {
  background-color: $color-white;
  padding: $spacing-md;
  border-bottom: 1px solid $color-border;

  .filter-scroll {
    white-space: nowrap;
  }

  .filter-tabs {
    display: inline-flex;
    gap: $spacing-sm;
  }

  .filter-tab {
    position: relative;
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    padding: $spacing-sm $spacing-md;
    border-radius: $border-radius-round;
    background-color: $color-background;
    white-space: nowrap;
    transition: all 0.2s ease;

    &.active {
      background-color: $color-primary;
      color: $color-white;
    }
  }

  .tab-text {
    font-size: $font-size-sm;
    font-weight: 500;
  }
}

.coupons-section {
  padding: $spacing-md;

  .loading-section,
  .error-section,
  .empty-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: $spacing-xl 0;
    background-color: $color-white;
    border-radius: $border-radius-md;
    box-shadow: $shadow-sm;
  }

  .loading-text,
  .error-text,
  .empty-text {
    font-size: $font-size-md;
    color: $color-text-secondary;
    margin-bottom: $spacing-md;
  }

  .retry-btn {
    background-color: $color-primary;
    border-radius: $border-radius-round;
    padding: $spacing-sm $spacing-lg;

    .retry-text {
      color: $color-white;
      font-weight: 500;
      font-size: $font-size-md;
    }
  }

  .empty-icon {
    font-size: 80rpx;
    margin-bottom: $spacing-md;
  }

  .empty-subtext {
    font-size: $font-size-sm;
    color: $color-text-tertiary;
    margin-bottom: $spacing-md;
  }

  .empty-btn {
    background-color: $color-primary;
    border-radius: $border-radius-round;
    padding: $spacing-sm $spacing-lg;
  }

  .empty-btn-text {
    color: $color-white;
    font-weight: 500;
    font-size: $font-size-md;
  }
}

.coupons-list {
  .coupon-card {
    position: relative;
    background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
    border-radius: $border-radius-md;
    padding: $spacing-md;
    margin-bottom: $spacing-md;
    box-shadow: $shadow-sm;
    overflow: hidden;

    &:last-child {
      margin-bottom: 0;
    }

    &.available {
      background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
    }

    &.used {
      background: linear-gradient(135deg, #d4d4d4 0%, #f0f0f0 100%);
      opacity: 0.8;
    }

    &.expired {
      background: linear-gradient(135deg, #e0e0e0 0%, #f5f5f5 100%);
      opacity: 0.6;
    }
  }

  .coupon-info {
    color: $color-text-primary;
  }

  .coupon-main {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-sm;
  }

  .coupon-name {
    font-size: $font-size-lg;
    font-weight: 600;
  }

  .coupon-discount {
    font-size: $font-size-xl;
    font-weight: 700;
    color: $color-error;
  }

  .coupon-desc {
    display: block;
    font-size: $font-size-sm;
    margin-bottom: $spacing-sm;
    color: rgba(0, 0, 0, 0.7);
  }

  .coupon-details {
    margin-bottom: $spacing-sm;
  }

  .coupon-code,
  .coupon-expiry {
    display: block;
    font-size: $font-size-xs;
    color: rgba(0, 0, 0, 0.6);
  }

  .coupon-conditions {
    display: flex;
    flex-wrap: wrap;
    gap: $spacing-xs;
  }

  .condition-item {
    font-size: $font-size-xs;
    background-color: rgba(255, 255, 255, 0.3);
    padding: 2rpx 6rpx;
    border-radius: $border-radius-sm;
    color: rgba(0, 0, 0, 0.7);
  }

  .coupon-status {
    position: absolute;
    top: $spacing-md;
    right: $spacing-md;
    background-color: rgba(255, 255, 255, 0.9);
    padding: 2rpx 8rpx;
    border-radius: $border-radius-sm;

    &.available {
      background-color: rgba(76, 175, 80, 0.2);
      color: #4caf50;
    }

    &.used {
      background-color: rgba(158, 158, 158, 0.2);
      color: #9e9e9e;
    }

    &.expired {
      background-color: rgba(244, 67, 54, 0.2);
      color: #f44336;
    }
  }

  .status-text {
    font-size: $font-size-xs;
    font-weight: 500;
  }
}

.get-coupon-section {
  padding: $spacing-md;
  text-align: center;
}

.get-coupon-btn {
  background-color: $color-primary;
  border-radius: $border-radius-round;
  padding: $spacing-md;

  .get-coupon-text {
    color: $color-white;
    font-weight: 500;
    font-size: $font-size-md;
  }
}
</style>