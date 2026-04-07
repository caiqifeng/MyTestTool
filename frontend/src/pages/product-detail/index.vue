<template>
  <view class="page-container">
    <view class="product-detail-page">
      <!-- 商品图片轮播 -->
      <view class="product-images">
        <swiper
          class="image-swiper"
          :autoplay="false"
          :circular="true"
          indicator-dots
          indicator-color="rgba(255, 255, 255, 0.5)"
          indicator-active-color="#FF6B35"
        >
          <swiper-item v-for="(image, index) in product.images" :key="index">
            <image class="product-image" :src="image" mode="aspectFill" />
          </swiper-item>
        </swiper>
      </view>

      <!-- 商品基本信息 -->
      <view class="product-info">
        <view class="price-section">
          <text class="current-price">¥{{ product.price }}</text>
          <text v-if="product.originalPrice" class="original-price">
            ¥{{ product.originalPrice }}
          </text>
          <view class="discount-tag" v-if="product.originalPrice">
            {{ Math.round((1 - product.price / product.originalPrice) * 100) }}折
          </view>
        </view>

        <text class="product-name">{{ product.name }}</text>
        <text class="product-description">{{ product.description }}</text>

        <view class="product-meta">
          <view class="meta-item">
            <text class="meta-label">销量</text>
            <text class="meta-value">{{ product.sales }}</text>
          </view>
          <view class="meta-item">
            <text class="meta-label">库存</text>
            <text class="meta-value">{{ product.stock }}</text>
          </view>
          <view class="meta-item">
            <text class="meta-label">分类</text>
            <text class="meta-value">{{ product.categoryName }}</text>
          </view>
        </view>
      </view>

      <!-- 商品规格选择 -->
      <view v-if="product.specs && Object.keys(product.specs).length > 0" class="spec-section">
        <view class="section-title">选择规格</view>

        <view v-for="(values, specName) in product.specs" :key="specName" class="spec-group">
          <text class="spec-label">{{ specName }}</text>
          <view class="spec-options">
            <view
              class="spec-option"
              v-for="value in values"
              :key="value"
              :class="{ 'selected': selectedSpecs[specName] === value }"
              @click="selectSpec(specName, value)"
            >
              <text class="option-text">{{ value }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 商品详情 -->
      <view class="detail-section">
        <view class="section-title">商品详情</view>
        <view class="detail-content">
          <text class="detail-text">
            这里是商品详情描述，可以包含产品的详细介绍、使用方法、注意事项等信息。
            支持富文本展示，可以包含图片、文字等多种格式。
          </text>
          <image
            class="detail-image"
            src="https://via.placeholder.com/750x500/FF6B35/FFFFFF?text=商品详情图"
            mode="widthFix"
          />
        </view>
      </view>

      <!-- 底部操作栏 -->
      <view class="product-footer">
        <view class="footer-left">
          <view class="footer-item" @click="handleNavigate('home')">
            <view class="footer-icon">🏠</view>
            <text class="footer-text">首页</text>
          </view>
          <view class="footer-item" @click="handleNavigate('cart')">
            <view class="footer-icon">🛒</view>
            <text class="footer-text">购物车</text>
            <text v-if="cartStore.getTotalQuantity > 0" class="cart-badge">
              {{ cartStore.getTotalQuantity }}
            </text>
          </view>
          <view class="footer-item" @click="handleFavorite">
            <view class="footer-icon" :class="{ 'favorited': isFavorited }">
              {{ isFavorited ? '❤️' : '🤍' }}
            </view>
            <text class="footer-text">收藏</text>
          </view>
        </view>

        <view class="footer-right">
          <view class="add-cart-btn" @click="handleAddToCart">
            <text class="btn-text">加入购物车</text>
          </view>
          <view class="buy-now-btn" @click="handleBuyNow">
            <text class="btn-text">立即购买</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useCartStore } from '../../store/cart.store'
import { useProductStore } from '../../store/product.store'

const cartStore = useCartStore()
const productStore = useProductStore()

const product = ref({
  id: '1',
  name: '奶油可颂',
  description: '新鲜烘焙的奶油可颂，外酥内软，奶香浓郁，早餐下午茶的不二选择。',
  price: 18,
  originalPrice: 22,
  images: [
    'https://via.placeholder.com/750x750/FF6B35/FFFFFF?text=可颂1',
    'https://via.placeholder.com/750x750/4ECDC4/FFFFFF?text=可颂2',
    'https://via.placeholder.com/750x750/52C41A/FFFFFF?text=可颂3',
  ],
  categoryId: '1',
  categoryName: '面包',
  stock: 100,
  sales: 152,
  specs: {
    '尺寸': ['小份', '中份', '大份'],
    '口味': ['原味', '巧克力', '抹茶'],
  },
  createdAt: '2023-01-01',
})

const selectedSpecs = ref<Record<string, string>>({})
const isFavorited = ref(false)
const quantity = ref(1)

onLoad((options) => {
  const productId = options.id
  console.log('加载商品:', productId)
  // 这里应该根据productId从API加载商品数据
  productStore.setCurrentProduct(product.value)
})

onMounted(() => {
  // 初始化默认规格
  if (product.value.specs) {
    Object.keys(product.value.specs).forEach(specName => {
      if (product.value.specs![specName].length > 0) {
        selectedSpecs.value[specName] = product.value.specs![specName][0]
      }
    })
  }
})

const selectSpec = (specName: string, value: string) => {
  selectedSpecs.value[specName] = value
}

const handleAddToCart = () => {
  const cartItem = {
    productId: product.value.id,
    name: product.value.name,
    price: product.value.price,
    quantity: quantity.value,
    image: product.value.images[0],
    specs: selectedSpecs.value,
  }

  cartStore.addItem(cartItem)

  uni.showToast({
    title: '已加入购物车',
    icon: 'success',
  })
}

const handleBuyNow = () => {
  const cartItem = {
    productId: product.value.id,
    name: product.value.name,
    price: product.value.price,
    quantity: quantity.value,
    image: product.value.images[0],
    specs: selectedSpecs.value,
  }

  cartStore.addItem(cartItem)

  uni.navigateTo({
    url: '/pages/order-confirm/index',
  })
}

const handleNavigate = (type: string) => {
  switch (type) {
    case 'home':
      uni.switchTab({
        url: '/pages/index/index',
      })
      break
    case 'cart':
      uni.switchTab({
        url: '/pages/cart/index',
      })
      break
  }
}

const handleFavorite = () => {
  isFavorited.value = !isFavorited.value

  uni.showToast({
    title: isFavorited.value ? '已收藏' : '已取消收藏',
    icon: 'none',
  })
}
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.product-detail-page {
  padding-bottom: 120rpx; /* 为底部操作栏留空间 */
}

.product-images {
  .image-swiper {
    height: 750rpx;
  }

  .product-image {
    width: 100%;
    height: 100%;
  }
}

.product-info {
  background-color: $color-white;
  padding: $spacing-md;
  margin-bottom: $spacing-md;
}

.price-section {
  display: flex;
  align-items: baseline;
  margin-bottom: $spacing-sm;

  .current-price {
    font-size: $font-size-xxl;
    font-weight: 600;
    color: $color-error;
    margin-right: $spacing-sm;
  }

  .original-price {
    font-size: $font-size-md;
    color: $color-text-tertiary;
    text-decoration: line-through;
    margin-right: $spacing-md;
  }

  .discount-tag {
    background-color: $color-error;
    color: $color-white;
    font-size: $font-size-xs;
    padding: 2rpx 8rpx;
    border-radius: $border-radius-sm;
  }
}

.product-name {
  display: block;
  font-size: $font-size-lg;
  font-weight: 600;
  color: $color-text-primary;
  margin-bottom: $spacing-sm;
}

.product-description {
  display: block;
  font-size: $font-size-md;
  color: $color-text-secondary;
  margin-bottom: $spacing-md;
  line-height: 1.5;
}

.product-meta {
  display: flex;
  justify-content: space-around;
  padding-top: $spacing-md;
  border-top: 1px solid $color-border;

  .meta-item {
    text-align: center;
    flex: 1;
  }

  .meta-label {
    display: block;
    font-size: $font-size-sm;
    color: $color-text-tertiary;
    margin-bottom: $spacing-xs;
  }

  .meta-value {
    display: block;
    font-size: $font-size-md;
    color: $color-text-primary;
    font-weight: 500;
  }
}

.spec-section,
.detail-section {
  background-color: $color-white;
  padding: $spacing-md;
  margin-bottom: $spacing-md;
}

.section-title {
  font-size: $font-size-lg;
  font-weight: 600;
  color: $color-text-primary;
  margin-bottom: $spacing-md;
}

.spec-group {
  margin-bottom: $spacing-lg;

  &:last-child {
    margin-bottom: 0;
  }
}

.spec-label {
  display: block;
  font-size: $font-size-md;
  color: $color-text-primary;
  margin-bottom: $spacing-sm;
}

.spec-options {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;
}

.spec-option {
  border: 1px solid $color-border;
  border-radius: $border-radius-md;
  padding: $spacing-sm $spacing-md;
  font-size: $font-size-md;
  color: $color-text-secondary;
  transition: all 0.2s ease;

  &.selected {
    border-color: $color-primary;
    background-color: rgba($color-primary, 0.1);
    color: $color-primary;
  }
}

.detail-content {
  .detail-text {
    display: block;
    font-size: $font-size-md;
    color: $color-text-secondary;
    line-height: 1.6;
    margin-bottom: $spacing-md;
  }

  .detail-image {
    width: 100%;
    border-radius: $border-radius-md;
  }
}

.product-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: $color-white;
  border-top: 1px solid $color-border;
  padding: $spacing-sm $spacing-md;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;

  .footer-left {
    display: flex;
    align-items: center;
  }

  .footer-item {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-right: $spacing-lg;

    &:last-child {
      margin-right: 0;
    }
  }

  .footer-icon {
    font-size: 40rpx;
    margin-bottom: 4rpx;

    &.favorited {
      color: $color-error;
    }
  }

  .footer-text {
    font-size: $font-size-xs;
    color: $color-text-secondary;
  }

  .cart-badge {
    position: absolute;
    top: -10rpx;
    right: -10rpx;
    background-color: $color-error;
    color: $color-white;
    font-size: $font-size-xs;
    width: 36rpx;
    height: 36rpx;
    border-radius: $border-radius-circle;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .footer-right {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
  }

  .add-cart-btn,
  .buy-now-btn {
    border-radius: $border-radius-round;
    padding: $spacing-sm $spacing-lg;
  }

  .add-cart-btn {
    background-color: $color-secondary;
  }

  .buy-now-btn {
    background-color: $color-primary;
  }

  .btn-text {
    color: $color-white;
    font-weight: 500;
    font-size: $font-size-md;
  }
}
</style>