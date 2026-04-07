<template>
  <view class="page-container">
    <view class="home-page">
      <!-- 搜索栏 -->
      <view class="home-search-bar">
        <view class="search-input">
          <text class="search-icon">🔍</text>
          <input
            type="text"
            placeholder="搜索面包、蛋糕..."
            v-model="searchKeyword"
            @confirm="handleSearch"
          />
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
          indicator-color="rgba(255, 255, 255, 0.5)"
          indicator-active-color="#FF6B35"
        >
          <swiper-item v-for="(banner, index) in banners" :key="index">
            <image class="banner-image" :src="banner.image" mode="aspectFill" />
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
            <image class="product-image" :src="product.images[0]" mode="aspectFill" />
            <view class="product-info">
              <text class="product-name">{{ product.name }}</text>
              <text class="product-price">¥{{ product.price }}</text>
              <text v-if="product.originalPrice" class="product-original-price">
                ¥{{ product.originalPrice }}
              </text>
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
            <image class="product-card-image" :src="product.images[0]" mode="aspectFill" />
            <view class="product-card-info">
              <text class="product-card-name">{{ product.name }}</text>
              <text class="product-card-desc">{{ product.description }}</text>
              <view class="product-card-bottom">
                <text class="product-card-price">¥{{ product.price }}</text>
                <text class="product-card-sales">已售 {{ product.sales }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useProductStore } from '../../store/product.store'

const productStore = useProductStore()

const searchKeyword = ref('')
const banners = ref([
  { id: 1, image: 'https://via.placeholder.com/750x300/FF6B35/FFFFFF?text=面包店Banner1' },
  { id: 2, image: 'https://via.placeholder.com/750x300/4ECDC4/FFFFFF?text=新品上市' },
  { id: 3, image: 'https://via.placeholder.com/750x300/52C41A/FFFFFF?text=限时优惠' },
])

const categories = ref([
  { id: '1', name: '全部', icon: '🍞' },
  { id: '2', name: '面包', icon: '🥖' },
  { id: '3', name: '蛋糕', icon: '🍰' },
  { id: '4', name: '甜点', icon: '🍮' },
  { id: '5', name: '饮品', icon: '☕' },
  { id: '6', name: '礼盒', icon: '🎁' },
])

const recommendedProducts = ref([
  {
    id: '1',
    name: '奶油可颂',
    price: 18,
    originalPrice: 22,
    images: ['https://via.placeholder.com/200x200/FF6B35/FFFFFF?text=可颂'],
  },
  {
    id: '2',
    name: '巧克力蛋糕',
    price: 68,
    originalPrice: 88,
    images: ['https://via.placeholder.com/200x200/4ECDC4/FFFFFF?text=蛋糕'],
  },
  {
    id: '3',
    name: '草莓慕斯',
    price: 48,
    images: ['https://via.placeholder.com/200x200/52C41A/FFFFFF?text=慕斯'],
  },
])

const hotProducts = ref([
  {
    id: '4',
    name: '全麦面包',
    description: '健康全麦，低脂低糖',
    price: 28,
    sales: 152,
    images: ['https://via.placeholder.com/100x100/FF6B35/FFFFFF?text=全麦'],
  },
  {
    id: '5',
    name: '芝士蛋糕',
    description: '浓郁芝士，入口即化',
    price: 58,
    sales: 98,
    images: ['https://via.placeholder.com/100x100/4ECDC4/FFFFFF?text=芝士'],
  },
  {
    id: '6',
    name: '拿铁咖啡',
    description: '现磨咖啡，香浓顺滑',
    price: 25,
    sales: 203,
    images: ['https://via.placeholder.com/100x100/52C41A/FFFFFF?text=咖啡'],
  },
])

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    productStore.addSearchHistory(searchKeyword.value)
    // 跳转到搜索页
    console.log('搜索:', searchKeyword.value)
  }
}

const handleCategoryClick = (categoryId: string) => {
  console.log('选择分类:', categoryId)
  // 跳转到分类页
}

const handleProductClick = (productId: string) => {
  console.log('查看商品:', productId)
  // 跳转到商品详情页
  uni.navigateTo({
    url: `/pages/product-detail/index?id=${productId}`,
  })
}

const handleViewAll = () => {
  console.log('查看全部推荐')
  // 跳转到商品列表页
}

onMounted(() => {
  // 初始化数据
  productStore.setProducts([...recommendedProducts.value, ...hotProducts.value])
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.home-page {
  padding-bottom: $spacing-xl;
}

.home-search-bar {
  padding: $spacing-md;
  background-color: $color-white;
}

.search-input {
  display: flex;
  align-items: center;
  background-color: $color-background;
  border-radius: $border-radius-round;
  padding: $spacing-sm $spacing-md;

  .search-icon {
    margin-right: $spacing-sm;
    color: $color-text-tertiary;
  }

  input {
    flex: 1;
    font-size: $font-size-md;
    background: transparent;
    border: none;
    outline: none;

    &::placeholder {
      color: $color-text-tertiary;
    }
  }
}

.home-banner {
  padding: 0 $spacing-md;

  .banner-swiper {
    height: 300rpx;
    border-radius: $border-radius-lg;
    overflow: hidden;
  }

  .banner-image {
    width: 100%;
    height: 100%;
  }
}

.category-nav {
  padding: $spacing-lg $spacing-md;

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
    width: 80rpx;
    height: 80rpx;
    background-color: $color-background;
    border-radius: $border-radius-circle;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40rpx;
    margin-bottom: $spacing-xs;
  }

  .category-name {
    font-size: $font-size-sm;
    color: $color-text-secondary;
  }
}

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
  font-size: $font-size-lg;
  font-weight: 600;
  color: $color-text-primary;
}

.section-more {
  font-size: $font-size-sm;
  color: $color-text-tertiary;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-sm;
}

.product-item {
  background-color: $color-white;
  border-radius: $border-radius-md;
  overflow: hidden;
  box-shadow: $shadow-sm;
}

.product-image {
  width: 100%;
  height: 200rpx;
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

  .product-price {
    font-size: $font-size-md;
    font-weight: 600;
    color: $color-error;
  }

  .product-original-price {
    font-size: $font-size-xs;
    color: $color-text-tertiary;
    text-decoration: line-through;
    margin-left: $spacing-xs;
  }
}

.product-list {
  .product-card {
    display: flex;
    background-color: $color-white;
    border-radius: $border-radius-md;
    padding: $spacing-md;
    margin-bottom: $spacing-md;
    box-shadow: $shadow-sm;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .product-card-image {
    width: 200rpx;
    height: 200rpx;
    border-radius: $border-radius-sm;
    margin-right: $spacing-md;
  }

  .product-card-info {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .product-card-name {
    font-size: $font-size-md;
    font-weight: 600;
    color: $color-text-primary;
    margin-bottom: $spacing-xs;
  }

  .product-card-desc {
    font-size: $font-size-sm;
    color: $color-text-secondary;
    margin-bottom: $spacing-md;
    @include text-ellipsis(2);
  }

  .product-card-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
  }

  .product-card-price {
    font-size: $font-size-lg;
    font-weight: 600;
    color: $color-error;
  }

  .product-card-sales {
    font-size: $font-size-sm;
    color: $color-text-tertiary;
  }
}
</style>