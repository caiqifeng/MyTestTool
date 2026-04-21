<template>
  <view class="page-container">
    <view class="home-page">
      <!-- 加载状态 -->
      <view v-if="productStore.isLoading" class="loading-section">
        <text class="loading-text">加载中...</text>
      </view>

      <!-- 错误状态 -->
      <view v-else-if="productStore.error" class="error-section">
        <text class="error-text">{{ productStore.error }}</text>
        <view class="retry-btn" @click="refreshData">
          <text class="retry-text">重试</text>
        </view>
      </view>

      <!-- 正常显示内容 -->
      <view v-else>
        <!-- 搜索栏 -->
        <view class="home-search-bar">
          <view class="search-input" @click="handleGoToSearch">
            <text class="search-icon">🔍</text>
            <text class="search-placeholder">搜索面包、蛋糕...</text>
          </view>
          <!-- 购物车按钮 -->
          <view class="cart-button" @click="handleGoToCart">
            <text class="cart-icon">🛒</text>
            <text v-if="cartCount > 0" class="cart-badge">{{ cartCount }}</text>
          </view>
        </view>

        <!-- Banner轮播 -->
        <view class="home-banner">
          <swiper
            class="banner-swiper"
            :autoplay="true"
            :interval="3000"
            :circular="true"
            indicator-dots
            indicator-color="rgba(166, 124, 82, 0.3)"
            indicator-active-color="#A67C52"
          >
            <swiper-item v-for="(banner, index) in banners" :key="index">
              <image
                class="banner-image"
                :src="banner.image"
                mode="aspectFill"
                @error="handleImageError"
              />
            </swiper-item>
          </swiper>
        </view>

        <!-- 分类导航 -->
        <view class="category-nav">
          <scroll-view class="category-scroll" scroll-x>
            <view
              class="category-item"
              v-for="category in categories"
              :key="category.id"
              @click="handleCategoryClick(category.id)"
            >
              <view class="category-icon">
                <text>{{ category.icon || '🍞' }}</text>
              </view>
              <text class="category-name">{{ category.name }}</text>
            </view>
          </scroll-view>
        </view>

        <!-- 推荐商品 -->
        <view class="recommended-section">
          <view class="section-header">
            <text class="section-title">今日推荐</text>
            <text class="section-more" @click="handleViewAll">查看更多 ></text>
          </view>

          <view class="product-grid">
            <view
              class="product-item"
              v-for="product in recommendedProducts"
              :key="product.id"
              @click="handleProductClick(product.id)"
            >
              <view class="product-image-wrapper">
                <image
                  class="product-image"
                  :src="product.images?.[0] || '/static/products/small/product-bread.jpg'"
                  mode="aspectFill"
                  @error="handleImageError"
                />
                <view v-if="product.stock === 0" class="sold-out-mask">
                  <text class="sold-out-text">售罄</text>
                </view>
              </view>
              <view class="product-info">
                <text class="product-name">{{ product.name }}</text>
                <view class="product-price-row">
                  <text class="product-price">¥{{ product.price }}</text>
                  <text v-if="product.originalPrice && product.originalPrice > product.price" class="product-original-price">
                    ¥{{ product.originalPrice }}
                  </text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 热门商品 -->
        <view class="hot-section">
          <view class="section-header">
            <text class="section-title">热门商品</text>
          </view>

          <view class="product-list">
            <view
              class="product-card"
              v-for="product in hotProducts"
              :key="product.id"
              @click="handleProductClick(product.id)"
            >
              <view class="product-card-image-wrapper">
                <image
                  class="product-card-image"
                  :src="product.images?.[0] || '/static/products/small/product-bread.jpg'"
                  mode="aspectFill"
                  @error="handleImageError"
                />
                <view v-if="product.stock === 0" class="sold-out-mask">
                  <text class="sold-out-text">售罄</text>
                </view>
              </view>
              <view class="product-card-info">
                <text class="product-card-name">{{ product.name }}</text>
                <text class="product-card-desc">{{ product.description }}</text>
                <view class="product-card-bottom">
                  <text class="product-card-price">¥{{ product.price }}</text>
                  <text class="product-card-sales">已售 {{ product.sales || 0 }}</text>
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
import { useProductStore } from '../../store/product.store'
import { useCartStore } from '../../store/cart.store'

const productStore = useProductStore()
const cartStore = useCartStore()

const cartCount = computed(() => cartStore.getTotalQuantity)

// 从store获取banner数据
const banners = computed(() => {
  const storeBanners = productStore.getBanners
  if (storeBanners && storeBanners.length > 0) {
    return storeBanners.map(banner => ({
      id: banner.id,
      image: banner.image
    }))
  }
  // 默认banner - 使用本地静态图片
  return [
    { id: '1', image: '/static/banners/banner-bakery-interior.jpg' },
    { id: '2', image: '/static/banners/banner-cake-dessert.jpg' },
    { id: '3', image: '/static/banners/banner-coffee-breakfast.jpg' }
  ]
})

// 计算属性：获取分类数据
const categories = computed(() => {
  const storeCategories = productStore.getCategories
  if (storeCategories && storeCategories.length > 0) {
    return storeCategories
  }
  // 默认分类
  return [
    { id: '1', name: '面包', icon: '🍞' },
    { id: '2', name: '蛋糕', icon: '🎂' },
    { id: '3', name: '饼干', icon: '🍪' },
    { id: '4', name: '甜甜圈', icon: '🍩' }
  ]
})

// 计算属性：获取推荐产品（前3个）
const recommendedProducts = computed(() => {
  const products = productStore.getProducts
  if (products && products.length > 0) {
    return products.slice(0, 3)
  }
  // 返回模拟数据作为fallback
  return [
    {
      id: '1',
      name: '奶油可颂',
      price: 18,
      originalPrice: 22,
      images: ['/static/products/small/product-bread.jpg'],
      stock: 152
    },
    {
      id: '2',
      name: '巧克力蛋糕',
      price: 68,
      originalPrice: 88,
      images: ['/static/products/small/product-cheesecake.jpg'],
      stock: 89
    },
    {
      id: '3',
      name: '草莓慕斯',
      price: 48,
      images: ['/static/products/small/product-latte.jpg'],
      stock: 120
    }
  ]
})

// 计算属性：获取热门产品（第4-6个）
const hotProducts = computed(() => {
  const products = productStore.getProducts
  if (products && products.length > 3) {
    return products.slice(3, 6)
  }
  // 返回模拟数据作为fallback
  return [
    {
      id: '4',
      name: '全麦面包',
      description: '健康全麦，低脂低糖',
      price: 28,
      images: ['/static/products/small/product-bread.jpg'],
      sales: 152,
      stock: 50
    },
    {
      id: '5',
      name: '芝士蛋糕',
      description: '浓郁芝士，入口即化',
      price: 58,
      images: ['/static/products/small/product-cheesecake.jpg'],
      sales: 98,
      stock: 30
    },
    {
      id: '6',
      name: '拿铁咖啡',
      description: '现磨咖啡，香浓顺滑',
      price: 25,
      images: ['/static/products/small/product-latte.jpg'],
      sales: 203,
      stock: 100
    }
  ]
})

const handleGoToSearch = () => {
  uni.navigateTo({
    url: '/pages/search/index'
  })
}

const handleGoToCart = () => {
  uni.navigateTo({
    url: '/pages/cart/index'
  })
}

const handleCategoryClick = (categoryId: string) => {
  console.log('选择分类:', categoryId)
  uni.navigateTo({
    url: `/pages/product-list/index?categoryId=${categoryId}`
  })
}

const handleProductClick = (productId: string) => {
  console.log('查看商品:', productId)
  uni.navigateTo({
    url: `/pages/product-detail/index?id=${productId}`
  })
}

const handleViewAll = () => {
  console.log('查看全部推荐')
  uni.switchTab({
    url: '/pages/category/index'
  })
}

const handleImageError = (e: any) => {
  console.error('图片加载失败:', e)
}

const refreshData = async () => {
  try {
    // 并行获取所有数据
    await Promise.allSettled([
      productStore.fetchBanners(),
      productStore.fetchCategories(),
      productStore.fetchProducts({ limit: 6 })
    ])
  } catch (error) {
    console.error('刷新数据失败:', error)
  }
}

onMounted(() => {
  // 页面加载时获取数据
  refreshData()
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.page-container {
  min-height: 100vh;
  background-color: $color-background;
  padding-bottom: 140rpx; /* 为原生 Tabbar 留空间 */
}

.home-page {
  padding-bottom: $spacing-xl;
}

.loading-section,
.error-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $spacing-xl;
  background: linear-gradient(135deg, #FFFFFF 0%, #FFF9F0 100%);
  border-radius: $border-radius-xl;
  box-shadow: 0 2rpx 16rpx rgba(166, 124, 82, 0.08);
  margin: $spacing-md;

  .loading-text,
  .error-text {
    font-size: $font-size-md;
    color: $color-text-secondary;
    margin-bottom: $spacing-md;
    text-align: center;
  }

  .retry-btn {
    background: linear-gradient(135deg, $color-primary 0%, #8B6A3E 100%);
    border-radius: $border-radius-round;
    padding: $spacing-sm $spacing-xl;
    box-shadow: 0 4rpx 12rpx rgba(166, 124, 82, 0.25);

    .retry-text {
      color: $color-white;
      font-weight: 500;
      font-size: $font-size-md;
    }
  }
}

// 搜索栏
.home-search-bar {
  padding: $spacing-md;
  background-color: $color-white;
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.search-input {
  flex: 1;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #F8F3EB 0%, #EDE4D8 100%);
  border-radius: $border-radius-round;
  padding: $spacing-sm $spacing-lg;
  height: 72rpx;

  .search-icon {
    margin-right: $spacing-sm;
    color: $color-text-secondary;
    font-size: 32rpx;
  }

  .search-placeholder {
    flex: 1;
    font-size: $font-size-md;
    color: $color-text-secondary;
  }
}

.cart-button {
  position: relative;
  width: 72rpx;
  height: 72rpx;
  background: linear-gradient(135deg, #F8F3EB 0%, #EDE4D8 100%);
  border-radius: $border-radius-circle;
  display: flex;
  align-items: center;
  justify-content: center;

  .cart-icon {
    font-size: 36rpx;
  }

  .cart-badge {
    position: absolute;
    top: 4rpx;
    right: 4rpx;
    background: linear-gradient(135deg, $color-accent 0%, #C98A5E 100%);
    color: $color-white;
    font-size: 20rpx;
    font-weight: 500;
    min-width: 32rpx;
    height: 32rpx;
    border-radius: $border-radius-circle;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 8rpx;
  }
}

// Banner轮播
.home-banner {
  padding: 0 $spacing-md $spacing-lg;

  .banner-swiper {
    height: 320rpx;
    border-radius: $border-radius-xl;
    overflow: hidden;
    box-shadow: 0 4rpx 16rpx rgba(166, 124, 82, 0.12);
  }

  .banner-image {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #F8F3EB 0%, #EDE4D8 100%);
  }
}

// 分类导航
.category-nav {
  padding: $spacing-md;

  .category-scroll {
    white-space: nowrap;
  }

  .category-item {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    margin-right: $spacing-xl;

    &:last-child {
      margin-right: 0;
    }
  }

  .category-icon {
    width: 96rpx;
    height: 96rpx;
    background: linear-gradient(135deg, #FFFFFF 0%, #FFF9F0 100%);
    border-radius: $border-radius-circle;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 44rpx;
    margin-bottom: $spacing-sm;
    box-shadow: 0 2rpx 12rpx rgba(166, 124, 82, 0.08);
  }

  .category-name {
    font-size: $font-size-sm;
    color: $color-text-primary;
    font-weight: 400;
  }
}

// 推荐商品和热门商品
.recommended-section,
.hot-section {
  padding: 0 $spacing-md;
  margin-bottom: $spacing-lg;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
}

.section-title {
  font-size: 36rpx;
  font-weight: 500;
  color: $color-text-primary;
  position: relative;
  padding-left: $spacing-sm;

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 6rpx;
    height: 32rpx;
    background: linear-gradient(180deg, $color-primary 0%, $color-accent 100%);
    border-radius: 3rpx;
  }
}

.section-more {
  font-size: $font-size-sm;
  color: $color-text-secondary;
}

// 推荐商品网格
.product-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-sm;
}

.product-item {
  background: linear-gradient(135deg, #FFFFFF 0%, #FFF9F0 100%);
  border-radius: $border-radius-lg;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(166, 124, 82, 0.06);
}

.product-image {
  width: 100%;
  height: 200rpx;
  background: linear-gradient(135deg, #F8F3EB 0%, #EDE4D8 100%);
}

.product-info {
  padding: $spacing-sm;

  .product-name {
    display: block;
    font-size: $font-size-sm;
    color: $color-text-primary;
    margin-bottom: $spacing-xs;
    @include text-ellipsis(1);
  }

  .product-price-row {
    display: flex;
    align-items: center;
    gap: $spacing-xs;
  }

  .product-price {
    font-size: $font-size-md;
    font-weight: 500;
    color: $color-primary;
  }

  .product-original-price {
    font-size: $font-size-xs;
    color: $color-text-secondary;
    text-decoration: line-through;
  }
}

// 热门商品列表
.product-list {
  .product-card {
    display: flex;
    background: linear-gradient(135deg, #FFFFFF 0%, #FFF9F0 100%);
    border-radius: $border-radius-xl;
    padding: $spacing-md;
    margin-bottom: $spacing-md;
    box-shadow: 0 2rpx 12rpx rgba(166, 124, 82, 0.06);

    &:last-child {
      margin-bottom: 0;
    }
  }

  .product-card-image {
    width: 200rpx;
    height: 200rpx;
    border-radius: $border-radius-lg;
    margin-right: $spacing-md;
    flex-shrink: 0;
    background: linear-gradient(135deg, #F8F3EB 0%, #EDE4D8 100%);
  }

  .product-card-info {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .product-card-name {
    font-size: $font-size-md;
    font-weight: 500;
    color: $color-text-primary;
    margin-bottom: $spacing-xs;
  }

  .product-card-desc {
    font-size: $font-size-sm;
    color: $color-text-secondary;
    margin-bottom: $spacing-md;
    @include text-ellipsis(2);
    line-height: 1.4;
  }

  .product-card-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
  }

  .product-card-price {
    font-size: 36rpx;
    font-weight: 500;
    color: $color-primary;
  }

  .product-card-sales {
    font-size: $font-size-sm;
    color: $color-text-secondary;
  }
}

// 售罄遮罩
.product-image-wrapper,
.product-card-image-wrapper {
  position: relative;
  width: 100%;
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
  border-radius: $border-radius-lg;

  .sold-out-text {
    color: $color-white;
    font-size: $font-size-md;
    font-weight: 600;
    padding: $spacing-xs $spacing-md;
    background-color: rgba(0, 0, 0, 0.8);
    border-radius: $border-radius-sm;
  }
}
</style>
