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
            <view class="image-wrapper">
              <image class="product-image" :src="image" mode="aspectFill" />
              <view v-if="product.stock === 0" class="sold-out-mask">
                <text class="sold-out-text">售罄</text>
              </view>
            </view>
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
            src="/static/product-detail/detail-bakery-display.jpg"
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
          <view
            class="add-cart-btn"
            :class="{ 'disabled': product.stock === 0 }"
            @click="product.stock > 0 && handleAddToCart()"
          >
            <text class="btn-text">{{ product.stock === 0 ? '已售罄' : '加入购物车' }}</text>
          </view>
          <view
            class="buy-now-btn"
            :class="{ 'disabled': product.stock === 0 }"
            @click="product.stock > 0 && handleBuyNow()"
          >
            <text class="btn-text">{{ product.stock === 0 ? '已售罄' : '立即购买' }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useCartStore } from '../../store/cart.store'
import { useProductStore } from '../../store/product.store'

const cartStore = useCartStore()
const productStore = useProductStore()

const isLoading = ref(false)
const error = ref<string | null>(null)
const selectedSpecs = ref<Record<string, string>>({})
const isFavorited = ref(false)
const quantity = ref(1)

const product = computed(() => {
  if (!productStore.getCurrentProduct) {
    return {
      id: '',
      name: '',
      description: '',
      price: 0,
      originalPrice: 0,
      images: [],
      categoryId: '',
      categoryName: '',
      stock: 0,
      sales: 0,
      specs: {},
      createdAt: '',
    }
  }
  return productStore.getCurrentProduct
})

const transformProduct = (backendProduct: any) => {
  // 转换规格数组为记录格式
  const convertSpecsArrayToRecord = (specsArray: any[]): Record<string, string[]> => {
    if (!specsArray || !Array.isArray(specsArray)) {
      return {};
    }

    const result: Record<string, string[]> = {};
    specsArray.forEach((spec: any) => {
      if (spec && spec.name && spec.value) {
        if (!result[spec.name]) {
          result[spec.name] = [];
        }
        result[spec.name].push(spec.value);
      }
    });
    return result;
  };

  return {
    id: backendProduct._id,
    name: backendProduct.name,
    description: backendProduct.description,
    price: backendProduct.price,
    originalPrice: backendProduct.originalPrice,
    images: backendProduct.images || [],
    categoryId: backendProduct.categoryId?._id || backendProduct.categoryId || '',
    categoryName: backendProduct.categoryId?.name || '',
    stock: backendProduct.stock || 0,
    sales: backendProduct.salesCount || 0,
    specs: convertSpecsArrayToRecord(backendProduct.specs),
    createdAt: backendProduct.createdAt,
  }
}

onLoad((options) => {
  const productId = options.id
  console.log('加载商品:', productId)

  if (productId) {
    isLoading.value = true
    error.value = null

    productStore.fetchProductById(productId)
      .then(() => {
        // 数据加载完成后初始化规格
        if (productStore.getCurrentProduct?.specs) {
          Object.keys(productStore.getCurrentProduct.specs).forEach(specName => {
            const values = productStore.getCurrentProduct!.specs![specName]
            if (values.length > 0) {
              selectedSpecs.value[specName] = values[0]
            }
          })
        }
      })
      .catch(err => {
        error.value = err.message || '加载商品失败'
        console.error('加载商品失败:', err)
      })
      .finally(() => {
        isLoading.value = false
      })
})

onMounted(() => {
  // 组件挂载后，检查是否有当前产品数据
  if (productStore.getCurrentProduct && Object.keys(selectedSpecs.value).length === 0) {
    if (productStore.getCurrentProduct.specs) {
      Object.keys(productStore.getCurrentProduct.specs).forEach(specName => {
        const values = productStore.getCurrentProduct!.specs![specName]
        if (values.length > 0) {
          selectedSpecs.value[specName] = values[0]
        }
      })
    }
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

  .disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background-color: $color-text-tertiary !important;
  }
}

.product-images {
  .image-wrapper {
    position: relative;
    width: 100%;
    height: 100%;
  }

  .sold-out-mask {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;

    .sold-out-text {
      color: $color-white;
      font-size: $font-size-lg;
      font-weight: 600;
      padding: $spacing-sm $spacing-lg;
      background-color: rgba(0, 0, 0, 0.8);
      border-radius: $border-radius-sm;
    }
  }
}
</style>