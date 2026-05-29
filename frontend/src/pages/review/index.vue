<template>
  <view class="page-container">
    <view class="review-page">
      <!-- 头部 -->
      <view class="review-header">
        <text class="review-title">评价订单</text>
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
            <text class="info-label">下单时间</text>
            <text class="info-value">{{ formatDate(order?.createdAt) }}</text>
          </view>
        </view>
      </view>

      <!-- 商品评价 -->
      <view class="product-reviews-section">
        <view class="section-header">
          <text class="section-title">商品评价</text>
        </view>
        <view v-if="order?.items" class="product-reviews">
          <view
            v-for="(item, index) in order.items"
            :key="item.productId"
            class="product-review-item"
          >
            <!-- 商品信息 -->
            <view class="product-info">
              <image class="product-image" :src="item.image" mode="aspectFill" />
              <view class="product-details">
                <text class="product-name">{{ item.name }}</text>
                <text v-if="item.specs && Object.keys(item.specs).length > 0" class="product-specs">
                  {{ Object.values(item.specs).join(' ') }}
                </text>
                <text class="product-quantity">×{{ item.quantity }}</text>
              </view>
            </view>

            <!-- 星级评分 -->
            <view class="rating-section">
              <text class="rating-label">商品评分</text>
              <view class="star-rating">
                <view
                  v-for="star in 5"
                  :key="star"
                  class="star"
                  :class="{ 'active': itemRatings[index] >= star }"
                  @click="setItemRating(index, star)"
                >
                  <text class="star-text">★</text>
                </view>
              </view>
            </view>

            <!-- 评论内容 -->
            <view class="comment-section">
              <text class="comment-label">商品评价</text>
              <textarea
                v-model="itemComments[index]"
                class="comment-textarea"
                placeholder="请分享您对商品的体验感受"
                maxlength="200"
                auto-height
              />
              <text class="comment-count">{{ itemComments[index]?.length || 0 }}/200</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 整体评价 -->
      <view class="overall-review-section">
        <view class="section-header">
          <text class="section-title">整体评价</text>
        </view>
        <view class="overall-review">
          <!-- 服务评分 -->
          <view class="service-rating">
            <text class="rating-label">服务评分</text>
            <view class="star-rating">
              <view
                v-for="star in 5"
                :key="star"
                class="star"
                :class="{ 'active': serviceRating >= star }"
                @click="setServiceRating(star)"
              >
                <text class="star-text">★</text>
              </view>
            </view>
          </view>

          <!-- 物流评分 -->
          <view class="delivery-rating">
            <text class="rating-label">物流评分</text>
            <view class="star-rating">
              <view
                v-for="star in 5"
                :key="star"
                class="star"
                :class="{ 'active': deliveryRating >= star }"
                @click="setDeliveryRating(star)"
              >
                <text class="star-text">★</text>
              </view>
            </view>
          </view>

          <!-- 整体评论 -->
          <view class="overall-comment">
            <text class="comment-label">整体评价</text>
            <textarea
              v-model="overallComment"
              class="comment-textarea"
              placeholder="请分享您的整体购物体验"
              maxlength="300"
              auto-height
            />
            <text class="comment-count">{{ overallComment?.length || 0 }}/300</text>
          </view>
        </view>
      </view>

      <!-- 底部操作栏 -->
      <view class="review-footer">
        <view class="footer-btns">
          <view class="action-btn cancel" @click="handleCancel">
            <text class="action-text">取消</text>
          </view>
          <view class="action-btn submit" @click="handleSubmitReview">
            <text class="action-text">提交评价</text>
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
import dayjs from 'dayjs'

const orderStore = useOrderStore()

// 订单数据
const order = ref<any>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

// 商品评分和评论
const itemRatings = ref<number[]>([])
const itemComments = ref<string[]>([])

// 整体评价
const serviceRating = ref(5)
const deliveryRating = ref(5)
const overallComment = ref('')

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

    // 初始化商品评价数据
    if (order.value.items) {
      const itemCount = order.value.items.length
      itemRatings.value = Array(itemCount).fill(5)
      itemComments.value = Array(itemCount).fill('')
    }
  } catch (err: any) {
    error.value = err.message || '获取订单详情失败'
    console.error('获取订单详情失败:', err)
  } finally {
    isLoading.value = false
  }
}

// 设置商品评分
const setItemRating = (index: number, rating: number) => {
  itemRatings.value[index] = rating
}

// 设置服务评分
const setServiceRating = (rating: number) => {
  serviceRating.value = rating
}

// 设置物流评分
const setDeliveryRating = (rating: number) => {
  deliveryRating.value = rating
}

// 格式化日期
const formatDate = (date?: string): string => {
  if (!date) return ''
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 验证评价数据
const validateReview = (): boolean => {
  if (!order.value) {
    uni.showToast({
      title: '订单信息错误',
      icon: 'none'
    })
    return false
  }

  // 检查商品评价是否完整
  if (order.value.items) {
    for (let i = 0; i < order.value.items.length; i++) {
      if (!itemRatings.value[i]) {
        uni.showToast({
          title: `请为第${i + 1}个商品评分`,
          icon: 'none'
        })
        return false
      }
    }
  }

  // 检查服务评分
  if (!serviceRating.value) {
    uni.showToast({
      title: '请为服务评分',
      icon: 'none'
    })
    return false
  }

  // 检查物流评分
  if (!deliveryRating.value) {
    uni.showToast({
      title: '请为物流评分',
      icon: 'none'
    })
    return false
  }

  return true
}

// 提交评价
const handleSubmitReview = async () => {
  if (!validateReview()) {
    return
  }

  isLoading.value = true

  try {
    // 构建评价数据
    const reviewData = {
      orderId: order.value.id,
      orderNo: order.value.orderNo,
      itemReviews: order.value.items.map((item: any, index: number) => ({
        productId: item.productId,
        productName: item.name,
        rating: itemRatings.value[index],
        comment: itemComments.value[index] || ''
      })),
      serviceRating: serviceRating.value,
      deliveryRating: deliveryRating.value,
      overallComment: overallComment.value,
      reviewDate: new Date().toISOString()
    }

    // 模拟提交评价API调用
    await simulateReviewSubmission(reviewData)

    // 评价成功
    uni.showToast({
      title: '评价成功',
      icon: 'success'
    })

    // 延迟返回，让用户看到成功提示
    setTimeout(() => {
      uni.navigateBack({
        delta: 2  // 返回到订单列表页
      })
    }, 1500)
  } catch (err: any) {
    // 评价失败
    uni.showToast({
      title: err.message || '评价失败，请重试',
      icon: 'none'
    })
  } finally {
    isLoading.value = false
  }
}

// 模拟提交评价API
const simulateReviewSubmission = (reviewData: any): Promise<void> => {
  return new Promise((resolve, reject) => {
    // 模拟网络延迟
    setTimeout(() => {
      // 模拟提交成功（95%成功率）
      const success = Math.random() < 0.95

      if (success) {
        console.log('评价提交成功:', reviewData)
        resolve()
      } else {
        reject(new Error('评价提交失败，请重试'))
      }
    }, 1000)
  })
}

// 取消评价
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

onMounted(() => {
  // 页面初始化
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.review-page {
  padding-bottom: 120rpx; /* 为底部操作栏留空间 */
}

.review-header {
  padding: $spacing-lg $spacing-md;
  background-color: $color-white;
  border-bottom: 1px solid $color-border;

  .review-title {
    font-size: $font-size-xl;
    font-weight: 500;
    color: $color-text-primary;
  }
}

.order-info-section,
.product-reviews-section,
.overall-review-section {
  background-color: $color-white;
  margin: $spacing-md;
  border-radius: $border-radius-lg;
}

.section-header {
  padding: $spacing-md;
  border-bottom: 1px solid $color-border;

  .section-title {
    font-size: $font-size-md;
    font-weight: 500;
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
  }

  .info-label {
    font-size: $font-size-sm;
    font-weight: 300;
    color: $color-text-secondary;
  }

  .info-value {
    font-size: $font-size-sm;
    color: $color-text-primary;
    font-weight: 400;
  }
}

.product-reviews {
  .product-review-item {
    padding: $spacing-md;
    border-bottom: 1px solid $color-border;

    &:last-child {
      border-bottom: none;
    }
  }

  .product-info {
    display: flex;
    margin-bottom: $spacing-lg;
  }

  .product-image {
    width: 120rpx;
    height: 120rpx;
    border-radius: $border-radius-md;
    margin-right: $spacing-md;
  }

  .product-details {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .product-name {
    font-size: $font-size-sm;
    font-weight: 400;
    color: $color-text-primary;
    margin-bottom: $spacing-xs;
    @include text-ellipsis(2);
  }

  .product-specs {
    font-size: $font-size-xs;
    font-weight: 300;
    color: $color-text-secondary;
    margin-bottom: $spacing-xs;
  }

  .product-quantity {
    font-size: $font-size-xs;
    font-weight: 300;
    color: $color-text-secondary;
  }
}

.rating-section,
.comment-section,
.service-rating,
.delivery-rating,
.overall-comment {
  margin-bottom: $spacing-lg;

  &:last-child {
    margin-bottom: 0;
  }
}

.rating-label,
.comment-label {
  display: block;
  font-size: $font-size-sm;
  font-weight: 400;
  color: $color-text-primary;
  margin-bottom: $spacing-sm;
}

.star-rating {
  display: flex;
  gap: $spacing-sm;
}

.star {
  font-size: 36rpx;
  color: $color-star-inactive;
  cursor: pointer;
  transition: color 0.2s ease;

  &.active {
    color: $color-star-active;
  }

  &:hover {
    opacity: 0.8;
  }
}

.star-text {
  display: block;
}

.comment-textarea {
  width: 100%;
  min-height: 160rpx;
  font-size: $font-size-md;
  color: $color-text-primary;
  padding: $spacing-md;
  border: 1px solid $color-border;
  border-radius: $border-radius-md;
  outline: none;
  resize: none;
  box-sizing: border-box;

  &::placeholder {
    color: $color-text-tertiary;
  }
}

.comment-count {
  display: block;
  text-align: right;
  font-size: $font-size-xs;
  font-weight: 300;
  color: $color-text-secondary;
  margin-top: $spacing-xs;
}

.review-footer {
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

  &.submit {
    background-color: $color-accent;
  }

  .action-text {
    font-weight: 500;
    font-size: $font-size-md;

    .cancel & {
      color: $color-text-primary;
    }

    .submit & {
      color: $color-white;
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