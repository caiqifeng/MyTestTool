<template>
  <view class="page-container">
    <view class="order-confirm-page">
      <!-- 头部 -->
      <view class="order-header">
        <text class="order-title">订单确认</text>
      </view>

      <!-- 收货地址 -->
      <view class="address-section">
        <view class="section-header">
          <text class="section-title">收货地址</text>
          <text class="section-action" @click="handleSelectAddress">选择地址</text>
        </view>

        <view v-if="selectedAddress" class="address-info">
          <view class="address-main">
            <text class="address-name">{{ selectedAddress.name }}</text>
            <text class="address-phone">{{ selectedAddress.phone }}</text>
          </view>
          <text class="address-detail">
            {{ selectedAddress.province }}{{ selectedAddress.city }}{{ selectedAddress.district }}{{ selectedAddress.detail }}
          </text>
        </view>

        <view v-else class="address-empty" @click="handleSelectAddress">
          <text class="empty-text">请选择收货地址</text>
          <text class="empty-icon">></text>
        </view>
      </view>

      <!-- 商品列表 -->
      <view class="products-section">
        <view class="section-header">
          <text class="section-title">商品清单</text>
        </view>

        <view class="product-list">
          <view
            class="product-item"
            v-for="item in cartStore.getItems.filter(item => cartStore.selectedItems.includes(item.id))"
            :key="item.id"
          >
            <image class="product-image" :src="item.image" mode="aspectFill" />
            <view class="product-info">
              <text class="product-name">{{ item.name }}</text>
              <text v-if="item.specs" class="product-specs">
                {{ Object.values(item.specs).join(' ') }}
              </text>
              <view class="product-bottom">
                <text class="product-price">¥{{ item.price }}</text>
                <text class="product-quantity">×{{ item.quantity }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 优惠券选择 -->
      <view class="coupon-section">
        <view class="section-header">
          <text class="section-title">优惠券</text>
          <text class="section-action" @click="handleSelectCoupon">
            {{ cartStore.getCoupon ? '更换优惠券' : '选择优惠券' }}
          </text>
        </view>
        <view v-if="cartStore.getCoupon" class="coupon-info">
          <view class="coupon-main">
            <text class="coupon-name">{{ cartStore.getCoupon.name }}</text>
            <text class="coupon-desc">{{ cartStore.getCoupon.description }}</text>
            <text class="coupon-value">
              {{ cartStore.getCoupon.type === 'fixed' ? '¥' : '' }}{{ cartStore.getCoupon.discount }}{{ cartStore.getCoupon.type === 'percentage' ? '%' : '' }}
            </text>
          </view>
          <text class="coupon-expiry">有效期至 {{ formatDate(cartStore.getCoupon.expiredAt) }}</text>
        </view>
        <view v-else class="coupon-empty">
          <text class="empty-text">暂无优惠券可用</text>
        </view>
      </view>

      <!-- 订单信息 -->
      <view class="order-info-section">
        <view class="info-item">
          <text class="info-label">商品金额</text>
          <text class="info-value">¥{{ cartStore.getTotalPrice.toFixed(2) }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">运费</text>
          <text class="info-value">¥{{ shippingFee.toFixed(2) }}</text>
        </view>
        <view v-if="cartStore.getCoupon" class="info-item">
          <text class="info-label">优惠券</text>
          <text class="info-value coupon">-¥{{ couponDiscount.toFixed(2) }}</text>
        </view>
        <view class="info-item total">
          <text class="info-label">实付金额</text>
          <text class="info-value total-price">¥{{ finalAmount.toFixed(2) }}</text>
        </view>
      </view>

      <!-- 底部提交栏 -->
      <view class="order-footer">
        <view class="footer-left">
          <text class="total-label">合计：</text>
          <text class="total-price">¥{{ finalAmount.toFixed(2) }}</text>
        </view>

        <view class="footer-right">
          <view class="submit-btn" @click="handleSubmitOrder">
            <text class="submit-text">提交订单</text>
          </view>
        </view>
      </view>

      <!-- 优惠券选择弹窗 -->
      <view v-if="showCouponModal" class="coupon-modal" @click="showCouponModal = false">
        <view class="coupon-modal-content" @click.stop>
          <view class="modal-header">
            <text class="modal-title">选择优惠券</text>
            <text class="modal-close" @click="showCouponModal = false">×</text>
          </view>

          <view class="coupon-list">
            <view
              v-for="coupon in availableCoupons"
              :key="coupon.id"
              class="coupon-card"
              :class="{ selected: selectedCouponId === coupon.id }"
              @click="handleCouponSelect(coupon)"
            >
              <view class="coupon-left">
                <text class="coupon-amount">
                  {{ coupon.type === 'fixed' ? '¥' : '' }}{{ coupon.value }}{{ coupon.type === 'percentage' ? '折' : '' }}
                </text>
                <text class="coupon-condition">
                  {{ coupon.minAmount ? `满${coupon.minAmount}可用` : '无门槛' }}
                </text>
              </view>
              <view class="coupon-right">
                <text class="coupon-name">{{ coupon.name }}</text>
                <text class="coupon-desc">{{ coupon.description }}</text>
                <text class="coupon-expire">有效期至 {{ formatDate(coupon.validTo) }}</text>
              </view>
              <view v-if="selectedCouponId === coupon.id" class="coupon-check">✓</view>
            </view>

            <view v-if="availableCoupons.length === 0" class="empty-coupons">
              <text class="empty-text">暂无可用优惠券</text>
            </view>
          </view>

          <view class="modal-footer">
            <view class="cancel-btn" @click="showCouponModal = false">
              <text>取消</text>
            </view>
            <view class="confirm-btn" @click="handleConfirmCoupon">
              <text>确定</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCartStore } from '../../store/cart.store'
import { useOrderStore } from '../../store/order.store'
import { getUserCoupons } from '../../utils/api/coupon.api'

const cartStore = useCartStore()
const orderStore = useOrderStore()

const selectedAddress = ref<any>(null)
const shippingFee = ref(5)
const showCouponModal = ref(false)
const availableCoupons = ref<any[]>([])
const selectedCouponId = ref<string | null>(null)

const couponDiscount = computed(() => {
  if (!cartStore.getCoupon) return 0
  const coupon = cartStore.getCoupon
  if (coupon.type === 'fixed') {
    return coupon.discount
  } else {
    return cartStore.getTotalPrice * (coupon.discount / 100)
  }
})

const finalAmount = computed(() => {
  return cartStore.getTotalPrice + shippingFee.value - couponDiscount.value
})

// 加载可用优惠券
const loadAvailableCoupons = async () => {
  try {
    const response = await getUserCoupons()
    if (response.data.success) {
      // 过滤出可用的优惠券
      const totalAmount = cartStore.getTotalPrice
      availableCoupons.value = response.data.data.coupons.filter((coupon: any) => {
        const now = new Date()
        const validFrom = new Date(coupon.validFrom)
        const validTo = new Date(coupon.validTo)
        const isValid = now >= validFrom && now <= validTo && coupon.isActive
        const meetsMinAmount = !coupon.minPurchaseAmount || totalAmount >= coupon.minPurchaseAmount
        return isValid && meetsMinAmount
      })
    }
  } catch (error) {
    console.error('加载优惠券失败:', error)
  }
}

onMounted(() => {
  loadAvailableCoupons()
})

const handleSelectAddress = () => {
  uni.showToast({
    title: '地址选择功能开发中',
    icon: 'none',
  })
}

// 选择优惠券
const handleSelectCoupon = () => {
  showCouponModal.value = true
  loadAvailableCoupons()
}

// 选中优惠券
const handleCouponSelect = (coupon: any) => {
  selectedCouponId.value = coupon.id
}

// 确认选择优惠券
const handleConfirmCoupon = () => {
  if (selectedCouponId.value) {
    const selectedCoupon = availableCoupons.value.find(c => c.id === selectedCouponId.value)
    if (selectedCoupon) {
      cartStore.applyCoupon({
        id: selectedCoupon.id,
        name: selectedCoupon.name,
        description: selectedCoupon.description,
        type: selectedCoupon.type,
        discount: selectedCoupon.value,
        expiredAt: selectedCoupon.validTo
      })
    }
  } else {
    cartStore.removeCoupon()
  }
  showCouponModal.value = false
}

// 格式化日期
const formatDate = (dateString?: string): string => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch {
    return dateString
  }
}

const handleSubmitOrder = async () => {
  if (!selectedAddress.value) {
    uni.showToast({
      title: '请选择收货地址',
      icon: 'none',
    })
    return
  }

  if (cartStore.getSelectedCount === 0) {
    uni.showToast({
      title: '请选择商品',
      icon: 'none',
    })
    return
  }

  uni.showModal({
    title: '确认订单',
    content: `确认支付 ¥${finalAmount.value.toFixed(2)} 吗？`,
    success: (res) => {
      if (res.confirm) {
        // 构建订单数据
        const selectedCartItems = cartStore.getItems.filter(item => cartStore.selectedItems.includes(item.id))

        const orderData = {
          items: selectedCartItems.map(item => ({
            productId: item.productId,
            name: item.name,
            price: item.price,
            quantity: item.quantity,
            image: item.image,
            specs: item.specs || {}
          })),
          deliveryType: 'delivery', // 默认配送方式
          deliveryAddressId: selectedAddress.value?.id || undefined,
          paymentMethod: 'wechat_pay', // 默认微信支付
          couponCode: cartStore.getCoupon?.id || undefined,
          remark: ''
        }

        // 调用API创建订单
        try {
          await orderStore.createNewOrder(orderData)

          if (orderStore.error.value) {
            throw new Error(orderStore.error.value)
          }

          // 清空已选商品
          cartStore.selectedItems.forEach(itemId => {
            cartStore.removeItem(itemId)
          })

          uni.showToast({
            title: '订单创建成功',
            icon: 'success',
          })

          // 跳转到支付页面
          setTimeout(() => {
            if (orderStore.getCurrentOrder) {
              uni.navigateTo({
                url: `/pages/payment/index?orderId=${orderStore.getCurrentOrder.id}`,
              })
            } else {
              uni.navigateBack()
            }
          }, 1500)
        } catch (error) {
          console.error('创建订单失败:', error)
          uni.showToast({
            title: '创建订单失败，请重试',
            icon: 'none',
          })
        }
      }
    }
  })
}
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.order-confirm-page {
  padding-bottom: 120rpx; /* 为底部提交栏留空间 */
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

.address-section,
.products-section,
.order-info-section {
  background-color: $color-white;
  margin: $spacing-md;
  border-radius: $border-radius-md;
  padding: $spacing-md;
  box-shadow: $shadow-sm;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;

  .section-title {
    font-size: $font-size-lg;
    font-weight: 600;
    color: $color-text-primary;
  }

  .section-action {
    font-size: $font-size-md;
    color: $color-primary;
  }
}

.address-info {
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

.address-empty {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md;
  border: 1px dashed $color-border;
  border-radius: $border-radius-md;

  .empty-text {
    font-size: $font-size-md;
    color: $color-text-tertiary;
  }

  .empty-icon {
    font-size: $font-size-lg;
    color: $color-text-tertiary;
  }
}

.product-list {
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

.coupon-section {
  background-color: $color-white;
  margin: $spacing-md;
  border-radius: $border-radius-md;
  box-shadow: $shadow-sm;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $spacing-md;
    border-bottom: 1px solid $color-border;

    .section-title {
      font-size: $font-size-lg;
      font-weight: 600;
      color: $color-text-primary;
    }

    .section-action {
      font-size: $font-size-md;
      color: $color-primary;
    }
  }

  .coupon-info {
    padding: $spacing-md;

    .coupon-main {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      margin-bottom: $spacing-xs;
    }

    .coupon-name {
      font-size: $font-size-md;
      font-weight: 600;
      color: $color-text-primary;
    }

    .coupon-desc {
      font-size: $font-size-sm;
      color: $color-text-secondary;
      flex: 1;
    }

    .coupon-value {
      font-size: $font-size-lg;
      font-weight: 600;
      color: $color-primary;
    }

    .coupon-expiry {
      display: block;
      font-size: $font-size-sm;
      color: $color-text-tertiary;
    }
  }

  .coupon-empty {
    padding: $spacing-md;
    text-align: center;

    .empty-text {
      font-size: $font-size-md;
      color: $color-text-tertiary;
    }
  }
}

.order-info-section {
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

    &.coupon {
      color: $color-primary;
    }

    &.total-price {
      font-size: $font-size-xl;
      color: $color-error;
      font-weight: 600;
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
    .submit-btn {
      background-color: $color-primary;
      border-radius: $border-radius-round;
      padding: $spacing-sm $spacing-xl;

      .submit-text {
        color: $color-white;
        font-size: $font-size-md;
        font-weight: 600;
      }
    }
  }
}

// 优惠券弹窗样式
.coupon-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  z-index: 1000;

  .coupon-modal-content {
    width: 100%;
    max-height: 80vh;
    background-color: $color-white;
    border-radius: $border-radius-lg $border-radius-lg 0 0;
    display: flex;
    flex-direction: column;

    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: $spacing-md;
      border-bottom: 1px solid $color-border;

      .modal-title {
        font-size: $font-size-lg;
        font-weight: 600;
        color: $color-text-primary;
      }

      .modal-close {
        font-size: 48rpx;
        color: $color-text-tertiary;
        line-height: 1;
      }
    }

    .coupon-list {
      flex: 1;
      overflow-y: auto;
      padding: $spacing-md;

      .coupon-card {
        position: relative;
        display: flex;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: $border-radius-md;
        padding: $spacing-md;
        margin-bottom: $spacing-md;
        color: $color-white;

        &.selected {
          border: 2px solid $color-primary;
        }

        .coupon-left {
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          min-width: 120rpx;
          border-right: 1px dashed rgba(255, 255, 255, 0.3);
          padding-right: $spacing-md;
          margin-right: $spacing-md;

          .coupon-amount {
            font-size: 48rpx;
            font-weight: 700;
          }

          .coupon-condition {
            font-size: $font-size-xs;
            margin-top: $spacing-xs;
            opacity: 0.9;
          }
        }

        .coupon-right {
          flex: 1;
          display: flex;
          flex-direction: column;
          justify-content: center;

          .coupon-name {
            font-size: $font-size-md;
            font-weight: 600;
            margin-bottom: $spacing-xs;
          }

          .coupon-desc {
            font-size: $font-size-sm;
            opacity: 0.9;
            margin-bottom: $spacing-xs;
          }

          .coupon-expire {
            font-size: $font-size-xs;
            opacity: 0.8;
          }
        }

        .coupon-check {
          position: absolute;
          top: $spacing-sm;
          right: $spacing-sm;
          width: 40rpx;
          height: 40rpx;
          background-color: $color-primary;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: $font-size-md;
          font-weight: 700;
        }
      }

      .empty-coupons {
        padding: 80rpx 0;
        text-align: center;

        .empty-text {
          font-size: $font-size-md;
          color: $color-text-tertiary;
        }
      }
    }

    .modal-footer {
      display: flex;
      padding: $spacing-md;
      border-top: 1px solid $color-border;
      gap: $spacing-md;

      .cancel-btn,
      .confirm-btn {
        flex: 1;
        padding: $spacing-sm;
        border-radius: $border-radius-md;
        text-align: center;
        font-size: $font-size-md;
      }

      .cancel-btn {
        background-color: $color-bg-secondary;
        color: $color-text-secondary;
      }

      .confirm-btn {
        background-color: $color-primary;
        color: $color-white;
      }
    }
  }
}
</style>
        font-weight: 500;
        font-size: $font-size-md;
      }
    }
  }
}
</style>