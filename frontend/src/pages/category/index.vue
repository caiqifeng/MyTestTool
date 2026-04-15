<template>
  <view class="page-container">
    <view class="category-page">
      <!-- 头部 -->
      <view class="category-header">
        <text class="category-title">商品分类</text>
      </view>

      <!-- 分类列表 -->
      <view class="category-list-section">
        <view v-if="isLoading" class="loading-section">
          <text class="loading-text">加载中...</text>
        </view>

        <view v-else-if="error" class="error-section">
          <text class="error-text">{{ error }}</text>
          <view class="retry-btn" @click="fetchCategories">
            <text class="retry-text">重试</text>
          </view>
        </view>

        <view v-else-if="categories.length === 0" class="empty-section">
          <view class="empty-icon">📂</view>
          <text class="empty-text">暂无分类</text>
          <text class="empty-subtext">商品分类正在整理中</text>
        </view>

        <view v-else class="categories-list">
          <view
            v-for="category in categories"
            :key="category._id"
            class="category-item"
            @click="handleCategoryClick(category)"
          >
            <view class="category-card">
              <!-- 分类图标 -->
              <view class="category-icon">
                <text class="icon-text">{{ category.icon || '🍞' }}</text>
              </view>

              <!-- 分类信息 -->
              <view class="category-info">
                <text class="category-name">{{ category.name }}</text>
                <text v-if="category.description" class="category-desc">
                  {{ category.description }}
                </text>
              </view>

              <!-- 右侧箭头 -->
              <view class="category-arrow">
                <text class="arrow-text">›</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 当前分类商品 -->
      <view v-if="selectedCategory && categoryProducts.length > 0" class="products-section">
        <view class="section-header">
          <text class="section-title">{{ selectedCategory.name }} - 商品</text>
          <text v-if="categoryProducts.length > 3" class="section-more" @click="handleViewMore">
            查看全部
          </text>
        </view>

        <view class="product-grid">
          <view
            v-for="product in categoryProducts.slice(0, 6)"
            :key="product.id"
            class="product-card"
            @click="handleProductClick(product)"
          >
            <view class="product-image-wrapper">
              <image class="product-image" :src="product.images?.[0] || '/static/products/small/product-bread.jpg'" mode="aspectFill" />
              <view v-if="product.stock === 0" class="sold-out-mask">
                <text class="sold-out-text">售罄</text>
              </view>
            </view>
            <view class="product-info">
              <text class="product-name">{{ product.name }}</text>
              <view class="product-price">
                <text class="current-price">¥{{ product.price?.toFixed(2) || '0.00' }}</text>
                <text v-if="product.originalPrice && product.originalPrice > product.price" class="original-price">
                  ¥{{ product.originalPrice?.toFixed(2) }}
                </text>
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
import { categoryApi } from '../../utils/api/category.api'
import { productApi } from '../../utils/api/product.api'

interface Category {
  _id: string
  name: string
  description?: string
  icon?: string
  sortOrder: number
  parentId?: string
  createdAt: string
  updatedAt: string
}

interface Product {
  id: string
  name: string
  price: number
  originalPrice?: number
  images: string[]
  categoryId: string
  description?: string
}

const categories = ref<Category[]>([])
const selectedCategory = ref<Category | null>(null)
const categoryProducts = ref<Product[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)

// 获取分类列表
const fetchCategories = async () => {
  isLoading.value = true
  error.value = null

  try {
    const response = await categoryApi.getCategories()
    if (response.success && response.data.categories) {
      categories.value = response.data.categories
      // 默认选择第一个分类
      if (categories.value.length > 0 && !selectedCategory.value) {
        selectedCategory.value = categories.value[0]
        fetchCategoryProducts(categories.value[0]._id)
      }
    } else {
      throw new Error(response.message || '获取分类列表失败')
    }
  } catch (err: any) {
    error.value = err.message || '获取分类列表失败'
    console.error('获取分类列表失败:', err)
  } finally {
    isLoading.value = false
  }
}

// 获取分类下的商品
const fetchCategoryProducts = async (categoryId: string) => {
  try {
    const response = await categoryApi.getCategoryProducts(categoryId, {
      page: 1,
      limit: 12
    })

    if (response.success && response.data.products) {
      // 转换数据格式
      categoryProducts.value = response.data.products.map((product: any) => ({
        id: product._id || product.id,
        name: product.name,
        price: product.price,
        originalPrice: product.originalPrice,
        images: product.images || [],
        categoryId: product.categoryId?._id || product.categoryId,
        description: product.description
      }))
    }
  } catch (err) {
    console.error('获取分类商品失败:', err)
    // 如果API失败，返回空数组
    categoryProducts.value = []
  }
}

// 处理分类点击
const handleCategoryClick = (category: Category) => {
  selectedCategory.value = category
  fetchCategoryProducts(category._id)
}

// 处理商品点击
const handleProductClick = (product: Product) => {
  uni.navigateTo({
    url: `/pages/product-detail/index?id=${product.id}`
  })
}

// 查看全部商品
const handleViewMore = () => {
  if (selectedCategory.value) {
    uni.navigateTo({
      url: `/pages/product-list/index?categoryId=${selectedCategory.value._id}`
    })
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.category-page {
  padding-bottom: $spacing-xl;
}

.category-header {
  padding: $spacing-lg $spacing-md;
  background-color: $color-white;
  border-bottom: 1px solid $color-border;

  .category-title {
    font-size: $font-size-xl;
    font-weight: 600;
    color: $color-text-primary;
  }
}

.category-list-section {
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
  }
}

.categories-list {
  .category-item {
    margin-bottom: $spacing-sm;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .category-card {
    display: flex;
    align-items: center;
    padding: $spacing-md;
    background-color: $color-white;
    border-radius: $border-radius-md;
    box-shadow: $shadow-sm;
    cursor: pointer;
    transition: all 0.2s ease;

    &:active {
      opacity: 0.8;
    }
  }

  .category-icon {
    width: 60rpx;
    height: 60rpx;
    border-radius: $border-radius-circle;
    background-color: rgba($color-primary, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: $spacing-md;
  }

  .icon-text {
    font-size: 28rpx;
  }

  .category-info {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .category-name {
    font-size: $font-size-md;
    font-weight: 600;
    color: $color-text-primary;
    margin-bottom: 2rpx;
  }

  .category-desc {
    font-size: $font-size-sm;
    color: $color-text-tertiary;
    @include text-ellipsis(1);
  }

  .category-arrow {
    margin-left: $spacing-sm;
  }

  .arrow-text {
    font-size: $font-size-lg;
    color: $color-text-tertiary;
  }
}

.products-section {
  margin: $spacing-md;
  padding: $spacing-md;
  background-color: $color-white;
  border-radius: $border-radius-md;
  box-shadow: $shadow-sm;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-md;
    padding-bottom: $spacing-sm;
    border-bottom: 1px solid $color-border;
  }

  .section-title {
    font-size: $font-size-lg;
    font-weight: 600;
    color: $color-text-primary;
  }

  .section-more {
    font-size: $font-size-sm;
    color: $color-primary;
    cursor: pointer;
  }
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-md;

  .product-card {
    border-radius: $border-radius-md;
    overflow: hidden;
    box-shadow: $shadow-sm;
    cursor: pointer;
    transition: all 0.2s ease;

    &:active {
      opacity: 0.8;
    }
  }

  .product-image {
    width: 100%;
    height: 200rpx;
    background-color: $color-background;
  }

  .product-info {
    padding: $spacing-md;
  }

  .product-name {
    display: block;
    font-size: $font-size-md;
    color: $color-text-primary;
    margin-bottom: $spacing-sm;
    @include text-ellipsis(1);
  }

  .product-price {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
  }

  .current-price {
    font-size: $font-size-lg;
    font-weight: 600;
    color: $color-error;
  }

  .original-price {
    font-size: $font-size-sm;
    color: $color-text-tertiary;
    text-decoration: line-through;
  }

  .product-image-wrapper {
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
    border-radius: $border-radius-md;

    .sold-out-text {
      color: $color-white;
      font-size: $font-size-md;
      font-weight: 600;
      padding: $spacing-xs $spacing-md;
      background-color: rgba(0, 0, 0, 0.8);
      border-radius: $border-radius-sm;
    }
  }
}
</style>