<template>
  <view class="page-container">
    <view class="payment-page">
      <!-- 头部 -->
      <view class="payment-header">
        <text class="payment-title">支付订单</text>
      </view>

      <!-- 订单信息 -->
      <view class="order-info-section">
        <view class="section-header">
          <text class="section-title">订单信息</text>
        </view>
        <view class="order-info-list">
          <view class="info-item">
            <text class="info-label">订单编号</text>
            <text class="info-value">{{ order?.orderNo || '--' }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">商品金额</text>
            <text class="info-value">¥{{ order?.totalAmount?.toFixed(2) || '0.00' }}</text>
          </view>
          <view v-if="order?.discountAmount > 0" class="info-item">
            <text class="info-label">优惠金额</text>
            <text class="info-value">-¥{{ order?.discountAmount?.toFixed(2) || '0.00' }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">运费</text>
            <text class="info-value">¥{{ order?.shippingFee?.toFixed(2) || '0.00' }}</text>
          </view>
          <view class="info-item total">
            <text class="info-label">实付金额</text>
            <text class="info-value total-price">¥{{ order?.finalAmount?.toFixed(2) || '0.00' }}</text>
          </view>
        </view>
      </view>

      <!-- 支付方式 -->
      <view class="payment-methods-section">
        <view class="section-header">
          <text class="section-title">支付方式</text>
        </view>
        <view class="payment-methods">
          <view
            v-for="method in paymentMethods"
            :key="method.id"
            class="payment-method-item"
            :class="{ 'selected': selectedMethod === method.id }"
            @click="selectPaymentMethod(method.id)"
          >
            <view class="method-icon">
              <text class="icon-text">{{ method.icon }}</text>
            </view>
            <view class="method-info">
              <text class="method-name">{{ method.name }}</text>
              <text class="method-desc">{{ method.description }}</text>
            </view>
            <view class="method-radio" :class="{ 'selected': selectedMethod === method.id }">
              <text v-if="selectedMethod === method.id" class="radio-dot"></text>
            </view>
          </view>
        </view>
      </view>

      <!-- 支付金额 -->
      <view class="payment-amount-section">
        <view class="amount-display">
          <text class="amount-label">支付金额</text>
          <text class="amount-value">¥{{ order?.finalAmount?.toFixed(2) || '0.00' }}</text>
        </view>
      </view>

      <!-- 底部操作栏 -->
      <view class="payment-footer">
        <view class="footer-btns">
          <view class="action-btn cancel" @click="handleCancel">
            <text class="action-text">取消支付</text>
          </view>
          <view class="action-btn confirm" @click="handlePayment">
            <text class="action-text">立即支付</text>
          </view>
        </view>
      </view>

      <!-- 支付结果弹窗 -->
      <view v-if="showPaymentResult" class="payment-result-modal" @click="handleCloseResult">
        <view class="payment-result-content" @click.stop>
          <view class="result-icon" :class="{ 'success': paymentSuccess, 'fail': !paymentSuccess }">
            <text>{{ paymentSuccess ? '✓' : '✗' }}</text>
          </view>
          <text class="result-title">{{ paymentSuccess ? '支付成功' : '支付失败' }}</text>
          <text class="result-message">{{ paymentResultMessage }}</text>
          <view class="result-btns">
            <view class="result-btn" @click="handlePaymentSuccess">
              <text class="btn-text">确定</text>
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
        <view class="retry-btn" @click="handleRetry">
          <text class="retry-text">重试</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useOrderStore } from '../../store/order.store'

const orderStore = useOrderStore()

// 订单数据
const order = ref<any>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

// 支付方式
const paymentMethods = ref([
  {
    id: 'wechat',
    name: '微信支付',
    description: '推荐使用',
    icon: '💳'
  },
  {
    id: 'alipay',
    name: '支付宝',
    description: '便捷支付',
    icon: '📱'
  },
  {
    id: 'bank',
    name: '银行卡支付',
    description: '储蓄卡/信用卡',
    icon: '🏦'
  }
])

const selectedMethod = ref('wechat')

// 支付结果
const showPaymentResult = ref(false)
const paymentSuccess = ref(false)
const paymentResultMessage = ref('')

// 页面加载
onLoad((options) => {
  const orderId = options.orderId
  if (orderId) {
    fetchOrder(orderId)
  } else {
    error.value = '订单ID无效'
  }
})

// 获取订单详情
const fetchOrder = async (orderId: string) => {
  isLoading.value = true
  error.value = null

  try {
    await orderStore.fetchOrderById(orderId)
    order.value = orderStore.getCurrentOrder

    if (!order.value) {
      throw new Error('订单不存在')
    }
  } catch (err: any) {
    error.value = err.message || '获取订单详情失败'
    console.error('获取订单详情失败:', err)
  } finally {
    isLoading.value = false
  }
}

// 选择支付方式
const selectPaymentMethod = (methodId: string) => {
  selectedMethod.value = methodId
}

// 处理支付
const handlePayment = async () => {
  if (!order.value) {
    uni.showToast({
      title: '订单信息错误',
      icon: 'none'
    })
    return
  }

  isLoading.value = true

  try {
    // 模拟支付API调用
    await simulatePayment()

    // 支付成功
    paymentSuccess.value = true
    paymentResultMessage.value = `订单 ${order.value.orderNo} 支付成功`
    showPaymentResult.value = true
  } catch (err: any) {
    // 支付失败
    paymentSuccess.value = false
    paymentResultMessage.value = err.message || '支付失败，请重试'
    showPaymentResult.value = true
  } finally {
    isLoading.value = false
  }
}

// 模拟支付API调用
const simulatePayment = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    // 模拟网络延迟
    setTimeout(() => {
      // 模拟支付成功（90%成功率）
      const success = Math.random() < 0.9

      if (success) {
        resolve()
      } else {
        reject(new Error('支付失败，请检查账户余额或重试'))
      }
    }, 1500)
  })
}

// 支付成功后处理
const handlePaymentSuccess = () => {
  showPaymentResult.value = false

  // 支付成功，返回订单详情页
  uni.showToast({
    title: '支付成功',
    icon: 'success'
  })

  // 延迟返回，让用户看到成功提示
  setTimeout(() => {
    uni.navigateBack({
      delta: 2  // 返回到订单详情页
    })
  }, 1000)
}

// 取消支付
const handleCancel = () => {
  uni.navigateBack()
}

// 重试
const handleRetry = () => {
  error.value = null
  if (order.value) {
    fetchOrder(order.value.id)
  }
}

// 关闭支付结果弹窗
const handleCloseResult = () => {
  showPaymentResult.value = false
}

onMounted(() => {
  // 页面初始化
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.payment-page {
  padding-bottom: 120rpx; /* 为底部操作栏留空间 */
}

.payment-header {
  padding: $spacing-lg $spacing-md;
  background-color: $color-white;
  border-bottom: 1px solid $color-border;

  .payment-title {
    font-size: $font-size-xl;
    font-weight: 600;
    color: $color-text-primary;
  }
}

.order-info-section,
.payment-methods-section,
.payment-amount-section {
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

.order-info-list {
  padding: $spacing-md;

  .info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-sm;

    &:last-child {
      margin-bottom: 0;
    }

    &.total {
      padding-top: $spacing-md;
      border-top: 1px solid $color-border;
      margin-top: $spacing-sm;
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

.payment-methods {
  padding: $spacing-md;

  .payment-method-item {
    display: flex;
    align-items: center;
    padding: $spacing-md;
    border: 1px solid $color-border;
    border-radius: $border-radius-md;
    margin-bottom: $spacing-sm;
    cursor: pointer;
    transition: all 0.2s ease;

    &:last-child {
      margin-bottom: 0;
    }

    &.selected {
      border-color: $color-primary;
      background-color: rgba($color-primary, 0.05);
    }

    &:active {
      opacity: 0.8;
    }
  }

  .method-icon {
    margin-right: $spacing-md;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .icon-text {
    font-size: 32rpx;
  }

  .method-info {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .method-name {
    font-size: $font-size-md;
    font-weight: 500;
    color: $color-text-primary;
    margin-bottom: 2rpx;
  }

  .method-desc {
    font-size: $font-size-sm;
    color: $color-text-tertiary;
  }

  .method-radio {
    width: 36rpx;
    height: 36rpx;
    border: 2px solid $color-border;
    border-radius: $border-radius-circle;
    display: flex;
    align-items: center;
    justify-content: center;

    &.selected {
      border-color: $color-primary;
      background-color: $color-primary;
    }
  }

  .radio-dot {
    width: 8rpx;
    height: 8rpx;
    border-radius: $border-radius-circle;
    background-color: $color-white;
  }
}

.payment-amount-section {
  .amount-display {
    padding: $spacing-xl $spacing-md;
    text-align: center;
  }

  .amount-label {
    display: block;
    font-size: $font-size-md;
    color: $color-text-secondary;
    margin-bottom: $spacing-sm;
  }

  .amount-value {
    display: block;
    font-size: 48rpx;
    font-weight: 600;
    color: $color-error;
  }
}

.payment-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: $color-white;
  border-top: 1px solid $color-border;
  padding: $spacing-md;
  z-index: 100;
}

.footer-btns {
  display: flex;
  gap: $spacing-sm;
}

.action-btn {
  flex: 1;
  border-radius: $border-radius-round;
  padding: $spacing-md;
  text-align: center;

  &.cancel {
    background-color: $color-white;
    border: 1px solid $color-border;
  }

  &.confirm {
    background-color: $color-primary;
  }

  .action-text {
    font-weight: 500;
    font-size: $font-size-md;

    .cancel & {
      color: $color-text-primary;
    }

    .confirm & {
      color: $color-white;
    }
  }
}

.payment-result-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.payment-result-content {
  background-color: $color-white;
  border-radius: $border-radius-md;
  padding: $spacing-xl;
  width: 80%;
  max-width: 500rpx;
  text-align: center;
}

.result-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: $border-radius-circle;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto $spacing-md;

  &.success {
    background-color: $color-success;
    color: $color-white;
  }

  &.fail {
    background-color: $color-error;
    color: $color-white;
  }

  text {
    font-size: 36rpx;
    font-weight: bold;
  }
}

.result-title {
  display: block;
  font-size: $font-size-xl;
  font-weight: 600;
  color: $color-text-primary;
  margin-bottom: $spacing-sm;
}

.result-message {
  display: block;
  font-size: $font-size-md;
  color: $color-text-secondary;
  margin-bottom: $spacing-lg;
}

.result-btns {
  .result-btn {
    background-color: $color-primary;
    border-radius: $border-radius-round;
    padding: $spacing-md;
  }

  .btn-text {
    color: $color-white;
    font-weight: 500;
    font-size: $font-size-md;
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