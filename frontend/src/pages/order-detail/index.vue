<template>
  <view class="page-container">
    <view class="order-detail-page">
      <!-- 头部 -->
      <view class="order-header">
        <text class="order-title">订单详情</text>
      </view>

      <!-- 订单状态 -->
      <view class="order-status-section">
        <text class="status-text">{{ getStatusText(order?.status) }}</text>
        <text v-if="order?.status === 'shipped'" class="status-desc">商品已发货，请注意查收</text>
        <text v-else-if="order?.status === 'delivered'" class="status-desc">商品已送达，请及时评价</text>
        <text v-else class="status-desc">{{ getStatusDesc(order?.status) }}</text>
      </view>

      <!-- 收货地址 -->
      <view v-if="order?.address" class="address-section">
        <view class="section-header">
          <text class="section-title">收货地址</text>
        </view>
        <view class="address-info">
          <view class="address-main">
            <text class="address-name">{{ order.address.name }}</text>
            <text class="address-phone">{{ order.address.phone }}</text>
          </view>
          <text class="address-detail">
            {{ order.address.province }}{{ order.address.city }}{{ order.address.district }}{{ order.address.detail }}
          </text>
        </view>
      </view>

      <!-- 商品列表 -->
      <view class="products-section">
        <view class="section-header">
          <text class="section-title">商品清单</text>
        </view>
        <view class="product-list">
          <view
            v-for="item in order?.items"
            :key="item.productId"
            class="product-item"
          >
            <image class="product-image" :src="item.image" mode="aspectFill" />
            <view class="product-info">
              <text class="product-name">{{ item.name }}</text>
              <text v-if="item.specs && Object.keys(item.specs).length > 0" class="product-specs">
                {{ Object.values(item.specs).join(' ') }}
              </text>
              <view class="product-bottom">
                <text class="product-price">¥{{ item.price.toFixed(2) }}</text>
                <text class="product-quantity">×{{ item.quantity }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 订单信息 -->
      <view class="order-info-section">
        <view class="section-header">
          <text class="section-title">订单信息</text>
        </view>
        <view class="info-list">
          <view class="info-item">
            <text class="info-label">订单编号</text>
            <text class="info-value">{{ order?.orderNo }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">下单时间</text>
            <text class="info-value">{{ formatDate(order?.createdAt) }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">商品金额</text>
            <text class="info-value">¥{{ order?.totalAmount.toFixed(2) }}</text>
          </view>
          <view v-if="order?.discountAmount > 0" class="info-item">
            <text class="info-label">优惠金额</text>
            <text class="info-value">-¥{{ order?.discountAmount.toFixed(2) }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">运费</text>
            <text class="info-value">¥{{ order?.shippingFee.toFixed(2) }}</text>
          </view>
          <view class="info-item total">
            <text class="info-label">实付金额</text>
            <text class="info-value total-price">¥{{ order?.finalAmount.toFixed(2) }}</text>
          </view>
        </view>
      </view>

      <!-- 底部操作栏 -->
      <view v-if="order" class="order-footer">
        <view class="footer-left">
          <text class="total-label">合计：</text>
          <text class="total-price">¥{{ order.finalAmount.toFixed(2) }}</text>
        </view>
        <view class="footer-right">
          <view v-if="order.status === 'pending'" class="action-btns">
            <view class="action-btn cancel" @click="handleCancelOrder">
              <text class="action-text">取消订单</text>
            </view>
            <view class="action-btn primary" @click="handlePayOrder">
              <text class="action-text">立即付款</text>
            </view>
          </view>
          <view v-else-if="order.status === 'shipped'" class="action-btns">
            <view class="action-btn confirm" @click="handleConfirmOrder">
              <text class="action-text">确认收货</text>
            </view>
          </view>
          <view v-else-if="order.status === 'delivered'" class="action-btns">
            <view class="action-btn review" @click="handleReviewOrder">
              <text class="action-text">评价</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 加载状态 -->
      <view v-if="isLoading" class="loading-overlay">
        <text class="loading-text">加载中...</text>
      </view>

      <view v-else-if="error" class="error-overlay">
        <text class="error-text">{{ error }}</text>
        <view class="retry-btn" @click="fetchOrder">
          <text class="retry-text">重试</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useOrderStore } from '../../store/order.store'
import dayjs from 'dayjs'

const orderStore = useOrderStore()

const isLoading = ref(false)
const error = ref<string | null>(null)

// 计算属性：获取当前订单
const order = computed(() => orderStore.getCurrentOrder)

const getStatusText = (status?: string): string => {
  const statusMap: Record<string, string> = {
    pending: '待付款',
    paid: '待发货',
    shipped: '待收货',
    delivered: '待评价',
    cancelled: '已取消',
    refunded: '已退款',
    completed: '已完成'
  }
  return statusMap[status || ''] || status || ''
}

const getStatusDesc = (status?: string): string => {
  const descMap: Record<string, string> = {
    pending: '等待买家付款',
    paid: '商家正在备货',
    shipped: '商品运输中',
    delivered: '商品已送达',
    cancelled: '订单已取消',
    refunded: '退款已完成',
    completed: '交易已完成'
  }
  return descMap[status || ''] || ''
}

const formatDate = (date?: string): string => {
  if (!date) return ''
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const fetchOrder = async (orderId: string) => {
  isLoading.value = true
  error.value = null

  try {
    await orderStore.fetchOrderById(orderId)
  } catch (err: any) {
    error.value = err.message || '获取订单详情失败'
    console.error('获取订单详情失败:', err)
  } finally {
    isLoading.value = false
  }
}

const handleCancelOrder = () => {
  if (!order.value) return

  uni.showModal({
    title: '确认取消',
    content: '确定要取消此订单吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await orderStore.cancelOrder(order.value!.id)
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

const handlePayOrder = () => {
  if (!order.value) return

  uni.navigateTo({
    url: `/pages/payment/index?orderId=${order.value.id}`
  })
}

const handleConfirmOrder = async () => {
  if (!order.value) return

  try {
    // 这里应该调用API确认收货
    console.log('确认收货:', order.value.id)
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

const handleReviewOrder = () => {
  if (!order.value) return

  uni.navigateTo({
    url: `/pages/review/index?orderId=${order.value.id}`
  })
}

onLoad((options) => {
  const orderId = options.id
  if (orderId) {
    fetchOrder(orderId)
  }
})

onMounted(() => {
  // 如果已经有当前订单数据，可以预加载
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.order-detail-page {
  padding-bottom: 120rpx; /* 为底部操作栏留空间 */
}

.order-header {
  padding: $spacing-md;
  background-color: $color-white;
  border-bottom: 1px solid $color-border;

  .order-title {
    font-size: $font-size-xl;
    font-weight: 600;
    color: $color-text-primary;
  }
}

.order-status-section {
  background: linear-gradient(135deg, $color-primary 0%, $color-primary-light 100%);
  padding: $spacing-xl $spacing-md;
  color: $color-white;
  text-align: center;

  .status-text {
    display: block;
    font-size: $font-size-xxl;
    font-weight: 600;
    margin-bottom: $spacing-sm;
  }

  .status-desc {
    font-size: $font-size-md;
    opacity: 0.9;
  }
}

.address-section,
.products-section,
.order-info-section {
  background-color: $color-white;
  margin: $spacing-md;
  border-radius: $border-radius-md;
  box-shadow: $shadow-sm;
}

.section-header {
  padding: $spacing-md;
  border-bottom: 1px solid $color-border;

  .section-title {
    font-size: $font-size-lg;
    font-weight: 600;
    color: $color-text-primary;
  }
}

.address-info {
  padding: $spacing-md;

  .address-main {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-xs;

    .address-name {
      font-size: $font-size-md;
      font-weight: 600;
      color: $color-text-primary;
    }

    .address-phone {
      font-size: $font-size-md;
      color: $color-text-secondary;
    }
  }

  .address-detail {
    display: block;
    font-size: $font-size-md;
    color: $color-text-secondary;
    line-height: 1.4;
  }
}

.product-list {
  padding: $spacing-md;

  .product-item {
    display: flex;
    padding: $spacing-md 0;
    border-bottom: 1px solid $color-border;

    &:last-child {
      border-bottom: none;
    }
  }

  .product-image {
    width: 120rpx;
    height: 120rpx;
    border-radius: $border-radius-sm;
    margin-right: $spacing-md;
  }

  .product-info {
    flex: 1;
    display: flex;
    flex-direction: column;

    .product-name {
      font-size: $font-size-md;
      color: $color-text-primary;
      margin-bottom: $spacing-xs;
      @include text-ellipsis(1);
    }

    .product-specs {
      font-size: $font-size-sm;
      color: $color-text-tertiary;
      margin-bottom: $spacing-sm;
    }

    .product-bottom {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: auto;
    }

    .product-price {
      font-size: $font-size-lg;
      font-weight: 600;
      color: $color-error;
    }

    .product-quantity {
      font-size: $font-size-md;
      color: $color-text-secondary;
    }
  }
}

.order-info-section {
  .info-list {
    padding: $spacing-md;

    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: $spacing-md;

      &:last-child {
        margin-bottom: 0;
      }

      &.total {
        padding-top: $spacing-md;
        border-top: 1px solid $color-border;
      }
    }

    .info-label {
      font-size: $font-size-md;
      color: $color-text-secondary;
    }

    .info-value {
      font-size: $font-size-md;
      color: $color-text-primary;
      font-weight: 500;

      &.total-price {
        font-size: $font-size-xl;
        color: $color-error;
        font-weight: 600;
      }
    }
  }
}

.order-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: $color-white;
  border-top: 1px solid $color-border;
  padding: $spacing-md;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;

  .footer-left {
    .total-label {
      font-size: $font-size-sm;
      color: $color-text-secondary;
      margin-right: $spacing-xs;
    }

    .total-price {
      font-size: $font-size-xl;
      font-weight: 600;
      color: $color-error;
    }
  }

  .footer-right {
    .action-btns {
      display: flex;
      gap: $spacing-sm;
    }

    .action-btn {
      border-radius: $border-radius-round;
      padding: $spacing-sm $spacing-lg;

      &.cancel {
        background-color: $color-white;
        border: 1px solid $color-border;
      }

      &.primary,
      &.review,
      &.confirm {
        background-color: $color-primary;
      }

      .action-text {
        font-weight: 500;
        font-size: $font-size-md;

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

.loading-overlay,
.error-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;

  .loading-text,
  .error-text {
    font-size: $font-size-lg;
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
}
</style>