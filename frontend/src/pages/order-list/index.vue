<template>
  <view class="page-container">
    <view class="order-list-page">
      <!-- 头部 -->
      <view class="order-header">
        <text class="order-title">我的订单</text>
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
              :class="{ 'active': filterStatus === 'pending' }"
              @click="setFilterStatus('pending')"
            >
              <text class="tab-text">待付款</text>
              <text v-if="getPendingCount > 0" class="tab-badge">{{ getPendingCount }}</text>
            </view>
            <view
              class="filter-tab"
              :class="{ 'active': filterStatus === 'paid' }"
              @click="setFilterStatus('paid')"
            >
              <text class="tab-text">待发货</text>
            </view>
            <view
              class="filter-tab"
              :class="{ 'active': filterStatus === 'shipped' }"
              @click="setFilterStatus('shipped')"
            >
              <text class="tab-text">待收货</text>
              <text v-if="getShippedCount > 0" class="tab-badge">{{ getShippedCount }}</text>
            </view>
            <view
              class="filter-tab"
              :class="{ 'active': filterStatus === 'delivered' }"
              @click="setFilterStatus('delivered')"
            >
              <text class="tab-text">待评价</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 订单列表 -->
      <view class="orders-section">
        <view v-if="isLoading" class="loading-section">
          <text class="loading-text">加载中...</text>
        </view>

        <view v-else-if="error" class="error-section">
          <text class="error-text">{{ error }}</text>
          <view class="retry-btn" @click="fetchOrders">
            <text class="retry-text">重试</text>
          </view>
        </view>

        <view v-else-if="filteredOrders.length === 0" class="empty-section">
          <view class="empty-icon">📦</view>
          <text class="empty-text">暂无订单</text>
          <text class="empty-subtext">快去挑选喜欢的商品吧</text>
        </view>

        <view v-else class="orders-list">
          <view
            v-for="order in filteredOrders"
            :key="order.id"
            class="order-card"
            @click="handleOrderClick(order.id)"
          >
            <!-- 订单头部 -->
            <view class="order-card-header">
              <text class="order-card-no">订单号: {{ order.orderNo }}</text>
              <text class="order-card-status" :class="getStatusClass(order.status)">
                {{ getStatusText(order.status) }}
              </text>
            </view>

            <!-- 订单商品 -->
            <view class="order-card-products">
              <view
                v-for="(item, index) in order.items.slice(0, 3)"
                :key="index"
                class="product-preview"
              >
                <image class="product-preview-image" :src="item.image" mode="aspectFill" />
                <view v-if="index === 2 && order.items.length > 3" class="product-preview-more">
                  <text class="more-text">+{{ order.items.length - 3 }}</text>
                </view>
              </view>
            </view>

            <!-- 订单信息 -->
            <view class="order-card-info">
              <view class="info-item">
                <text class="info-label">订单金额</text>
                <text class="info-value">¥{{ order.finalAmount.toFixed(2) }}</text>
              </view>
              <view class="info-item">
                <text class="info-label">下单时间</text>
                <text class="info-value">{{ formatDate(order.createdAt) }}</text>
              </view>
              <view v-if="order.items.length === 1" class="info-item">
                <text class="info-label">{{ order.items[0].name }}</text>
                <text class="info-value">×{{ order.items[0].quantity }}</text>
              </view>
            </view>

            <!-- 操作按钮 -->
            <view class="order-card-actions">
              <view v-if="order.status === 'pending'" class="action-btns">
                <view class="action-btn cancel" @click.stop="handleCancelOrder(order.id)">
                  <text class="action-text">取消订单</text>
                </view>
                <view class="action-btn primary" @click.stop="handlePayOrder(order.id)">
                  <text class="action-text">立即付款</text>
                </view>
              </view>

              <view v-else-if="order.status === 'delivered'" class="action-btns">
                <view class="action-btn review" @click.stop="handleReviewOrder(order.id)">
                  <text class="action-text">评价</text>
                </view>
              </view>

              <view v-else-if="order.status === 'shipped'" class="action-btns">
                <view class="action-btn confirm" @click.stop="handleConfirmOrder(order.id)">
                  <text class="action-text">确认收货</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useOrderStore } from '../../store/order.store'
import dayjs from 'dayjs'

const orderStore = useOrderStore()

const filterStatus = ref('all')
const isLoading = ref(false)
const error = ref<string | null>(null)

// 获取订单列表
const orders = computed(() => orderStore.getOrders)

// 根据状态过滤订单
const filteredOrders = computed(() => {
  if (filterStatus.value === 'all') {
    return orders.value
  }

  return orders.value.filter(order => {
    switch (filterStatus.value) {
      case 'pending':
        return order.status === 'pending'
      case 'paid':
        return order.status === 'paid'
      case 'shipped':
        return order.status === 'shipped'
      case 'delivered':
        return order.status === 'delivered'
      default:
        return true
    }
  })
})

// 统计各类订单数量
const getPendingCount = computed(() =>
  orders.value.filter(order => order.status === 'pending').length
)

const getShippedCount = computed(() =>
  orders.value.filter(order => order.status === 'shipped').length
)

const setFilterStatus = (status: string) => {
  filterStatus.value = status
}

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: '待付款',
    paid: '待发货',
    shipped: '待收货',
    delivered: '待评价',
    cancelled: '已取消',
    refunded: '已退款',
    completed: '已完成'
  }
  return statusMap[status] || status
}

const getStatusClass = (status: string): string => {
  const classMap: Record<string, string> = {
    pending: 'status-pending',
    paid: 'status-paid',
    shipped: 'status-shipped',
    delivered: 'status-delivered',
    cancelled: 'status-cancelled',
    refunded: 'status-refunded',
    completed: 'status-completed'
  }
  return classMap[status] || ''
}

const formatDate = (date: string): string => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const fetchOrders = async () => {
  isLoading.value = true
  error.value = null

  try {
    await orderStore.fetchOrders()
  } catch (err: any) {
    error.value = err.message || '获取订单列表失败'
    console.error('获取订单列表失败:', err)
  } finally {
    isLoading.value = false
  }
}

const handleOrderClick = (orderId: string) => {
  uni.navigateTo({
    url: `/pages/order-detail/index?id=${orderId}`
  })
}

const handleCancelOrder = (orderId: string) => {
  uni.showModal({
    title: '确认取消',
    content: '确定要取消此订单吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await orderStore.cancelOrder(orderId)
          uni.showToast({
            title: '订单已取消',
            icon: 'success'
          })
        } catch (err: any) {
          uni.showToast({
            title: err.message || '取消失败',
            icon: 'none'
          })
        }
      }
    }
  })
}

const handlePayOrder = (orderId: string) => {
  console.log('支付订单:', orderId)
  uni.navigateTo({
    url: `/pages/payment/index?orderId=${orderId}`
  })
}

const handleConfirmOrder = async (orderId: string) => {
  try {
    // 这里应该调用API确认收货
    console.log('确认收货:', orderId)
    uni.showToast({
      title: '确认收货成功',
      icon: 'success'
    })
  } catch (err: any) {
    uni.showToast({
      title: err.message || '确认收货失败',
      icon: 'none'
    })
  }
}

const handleReviewOrder = (orderId: string) => {
  uni.navigateTo({
    url: `/pages/review/index?orderId=${orderId}`
  })
}

onMounted(() => {
  fetchOrders()
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.order-list-page {
  padding-bottom: $spacing-xl;
}

.order-header {
  padding: $spacing-lg $spacing-md;
  background-color: $color-white;
  border-bottom: 1px solid $color-border;

  .order-title {
    font-size: $font-size-xl;
    font-weight: 500;
    color: $color-text-primary;
  }
}

.filter-section {
  background-color: $color-white;
  padding: $spacing-md;

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

  .tab-badge {
    position: absolute;
    top: -6rpx;
    right: -6rpx;
    background-color: $color-error;
    color: $color-white;
    font-size: $font-size-xs;
    min-width: 32rpx;
    height: 32rpx;
    border-radius: $border-radius-circle;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 4rpx;
  }
}

.orders-section {
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
    border-radius: $border-radius-lg;
  }

  .loading-text,
  .error-text,
  .empty-text {
    font-size: $font-size-md;
    font-weight: 400;
    color: $color-text-secondary;
    margin-bottom: $spacing-md;
  }

  .retry-btn {
    background-color: $color-primary;
    border-radius: $border-radius-lg;
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
    font-size: $font-size-xs;
    font-weight: 300;
    color: $color-text-secondary;
  }
}

.orders-list {
  .order-card {
    background-color: $color-white;
    border-radius: $border-radius-lg;
    margin-bottom: $spacing-md;
    overflow: hidden;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .order-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $spacing-md;
    border-bottom: 1px solid $color-border;
  }

  .order-card-no {
    font-size: $font-size-xs;
    font-weight: 300;
    color: $color-text-secondary;
  }

  .order-card-status {
    font-size: $font-size-sm;
    font-weight: 400;

    &.status-pending {
      color: $color-primary;
    }
    &.status-paid {
      color: $color-primary;
    }
    &.status-shipped {
      color: $color-primary;
    }
    &.status-delivered {
      color: $color-success;
    }
    &.status-cancelled,
    &.status-refunded {
      color: $color-text-secondary;
    }
    &.status-completed {
      color: $color-text-secondary;
    }
  }

  .order-card-products {
    display: flex;
    padding: $spacing-md;
    gap: $spacing-sm;

    .product-preview {
      position: relative;
      width: 120rpx;
      height: 120rpx;
      border-radius: $border-radius-md;
      overflow: hidden;
    }

    .product-preview-image {
      width: 100%;
      height: 100%;
    }

    .product-preview-more {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.6);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .more-text {
      color: $color-white;
      font-size: $font-size-md;
      font-weight: 500;
    }
  }

  .order-card-info {
    padding: $spacing-md;
    border-top: 1px solid $color-border;

    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: $spacing-sm;

      &:last-child {
        margin-bottom: 0;
      }
    }

    .info-label {
      font-size: $font-size-xs;
      font-weight: 300;
      color: $color-text-secondary;
    }

    .info-value {
      font-size: $font-size-sm;
      color: $color-text-primary;
      font-weight: 400;
    }
  }

  .order-card-actions {
    padding: $spacing-md;
    border-top: 1px solid $color-border;
    background-color: $color-background;

    .action-btns {
      display: flex;
      justify-content: flex-end;
      gap: $spacing-sm;
    }

    .action-btn {
      border-radius: $border-radius-round;
      padding: $spacing-sm $spacing-lg;

      &.cancel {
        background-color: $color-white;
        border: 1px solid $color-border;
      }

      &.primary {
        background-color: $color-accent;
      }

      &.review,
      &.confirm {
        background-color: $color-primary;
      }

      .action-text {
        font-weight: 500;
        font-size: $font-size-sm;

        .cancel & {
          color: $color-text-primary;
        }

        .primary &,
        .review &,
        .confirm & {
          color: $color-white;
        }
      }
    }
  }
}
</style>