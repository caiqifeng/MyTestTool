<template>
  <view class="page-container">
    <view class="product-list-page">
      <!-- 头部 -->
      <view class="product-header">
        <text class="product-title">{{ pageTitle }}</text>
      </view>

      <!-- 筛选栏 -->
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
              :class="{ 'active': filterStatus === 'price_asc' }"
              @click="setFilterStatus('price_asc')"
            >
              <text class="tab-text">价格从低到高</text>
            </view>
            <view
              class="filter-tab"
              :class="{ 'active': filterStatus === 'price_desc' }"
              @click="setFilterStatus('price_desc')"
            >
              <text class="tab-text">价格从高到低</text>
            </view>
            <view
              class="filter-tab"
              :class="{ 'active': filterStatus === 'sales' }"
              @click="setFilterStatus('sales')"
            >
              <text class="tab-text">销量优先</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 商品列表 -->
      <view class="products-section">
        <view v-if="isLoading" class="loading-section">
          <text class="loading-text">加载中...</text>
        </view>

        <view v-else-if="error" class="error-section">
          <text class="error-text">{{ error }}</text>
          <view class="retry-btn" @click="fetchProducts">
            <text class="retry-text">重试</text>
          </view>
        </view>

        <view v-else-if="products.length === 0" class="empty-section">
          <view class="empty-icon">📦</view>
          <text class="empty-text">暂无商品</text>
          <text class="empty-subtext">该分类下暂无商品</text>
        </view>

        <view v-else class="products-grid">
          <view
            v-for="product in products"
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
              <text v-if="product.description" class="product-desc">
                {{ product.description }}
              </text>
              <view class="product-price">
                <text class="current-price">¥{{ product.price?.toFixed(2) || '0.00' }}</text>
                <text v-if="product.originalPrice && product.originalPrice > product.price" class="original-price">
                  ¥{{ product.originalPrice?.toFixed(2) }}
                </text>
              </view>
              <view class="product-meta">
                <text class="sales-count">销量 {{ product.sales || 0 }}</text>
                <text v-if="product.stock !== undefined" class="stock-info">
                  库存 {{ product.stock }}
                </text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 加载更多 -->
      <view v-if="hasMore && !isLoading" class="load-more-section">
        <view class="load-more-btn" @click="loadMore">
          <text class="load-more-text">加载更多</text>
        </view>
      </view>

      <!-- 没有更多提示 -->
      <view v-if="!hasMore && products.length > 0" class="no-more-section">
        <text class="no-more-text">没有更多商品了</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { productApi } from '../../utils/api/product.api'
import { categoryApi } from '../../utils/api/category.api'

interface Product {
  id: string
  name: string
  description?: string
  price: number
  originalPrice?: number
  images: string[]
  categoryId: string
  sales: number
  stock?: number
  createdAt: string
}

interface Category {
  _id: string
  name: string
  description?: string
}

const products = ref<Product[]>([])
const category = ref<Category | null>(null)
const filterStatus = ref('all')
const isLoading = ref(false)
const error = ref<string | null>(null)
const page = ref(1)
const limit = ref(12)
const total = ref(0)
const hasMore = ref(true)
const keyword = ref('')

// 计算页面标题
const pageTitle = computed(() => {
  if (keyword.value) {
    return `搜索结果：${keyword.value}`
  }
  if (category.value) {
    return category.value.name
  }
  return '商品列表'
})

// 获取分类详情
const fetchCategory = async (categoryId: string) => {
  try {
    const response = await categoryApi.getCategory(categoryId)
    if (response.success && response.data.category) {
      category.value = response.data.category
    }
  } catch (err) {
    console.error('获取分类详情失败:', err)
  }
}

// 获取商品列表
const fetchProducts = async (reset = true) => {
  if (isLoading.value) return

  if (reset) {
    page.value = 1
    products.value = []
    hasMore.value = true
  }

  isLoading.value = true
  error.value = null

  try {
    const queryParams: any = {
      page: page.value,
      limit: limit.value
    }

    // 获取URL参数
    const urlParams = uni.getCurrentPages()[uni.getCurrentPages().length - 1].options
    const categoryId = urlParams.categoryId
    const searchKeyword = urlParams.keyword

    if (searchKeyword) {
      queryParams.keyword = searchKeyword
      keyword.value = searchKeyword
    }

    if (categoryId) {
      queryParams.categoryId = categoryId
      // 如果是第一次加载，获取分类信息
      if (reset && !category.value) {
        await fetchCategory(categoryId)
      }
    }

    // 应用排序
    switch (filterStatus.value) {
      case 'price_asc':
        queryParams.sortBy = 'price'
        queryParams.sortOrder = 'asc'
        break
      case 'price_desc':
        queryParams.sortBy = 'price'
        queryParams.sortOrder = 'desc'
        break
      case 'sales':
        queryParams.sortBy = 'sales'
        queryParams.sortOrder = 'desc'
        break
      default:
        queryParams.sortBy = 'sortOrder'
        queryParams.sortOrder = 'desc'
    }

    const response = await productApi.getProducts(queryParams)

    if (response.success && response.data.products) {
      const newProducts = response.data.products.map((product: any) => ({
        id: product._id || product.id,
        name: product.name,
        description: product.description,
        price: product.price,
        originalPrice: product.originalPrice,
        images: product.images || [],
        categoryId: product.categoryId?._id || product.categoryId,
        sales: product.salesCount || 0,
        stock: product.stock,
        createdAt: product.createdAt
      }))

      if (reset) {
        products.value = newProducts
      } else {
        products.value = [...products.value, ...newProducts]
      }

      total.value = response.data.pagination?.total || 0
      hasMore.value = products.value.length < total.value
    } else {
      throw new Error(response.message || '获取商品列表失败')
    }
  } catch (err: any) {
    error.value = err.message || '获取商品列表失败'
    console.error('获取商品列表失败:', err)
  } finally {
    isLoading.value = false
  }
}

// 设置筛选状态
const setFilterStatus = (status: string) => {
  if (filterStatus.value === status) return

  filterStatus.value = status
  fetchProducts()
}

// 处理商品点击
const handleProductClick = (product: Product) => {
  uni.navigateTo({
    url: `/pages/product-detail/index?id=${product.id}`
  })
}

// 加载更多
const loadMore = () => {
  if (hasMore.value && !isLoading.value) {
    page.value += 1
    fetchProducts(false)
  }
}

// 页面加载
onLoad((options) => {
  // 如果有分类ID，获取分类信息
  if (options.categoryId && !category.value) {
    fetchCategory(options.categoryId)
  }
  fetchProducts()
})

onMounted(() => {
  // 页面初始化
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.product-list-page {
  padding-bottom: $spacing-xl;
}

.product-header {
  padding: $spacing-lg $spacing-md;
  background-color: $color-white;
  border-bottom: 1px solid $color-border;

  .product-title {
    font-size: $font-size-xl;
    font-weight: 600;
    color: $color-text-primary;
  }
}

.filter-section {
  background-color: $color-white;
  padding: $spacing-md;
  border-bottom: 1px solid $color-border;

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
}

.products-section {
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

.products-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-md;

  .product-card {
    background-color: $color-white;
    border-radius: $border-radius-md;
    box-shadow: $shadow-sm;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.2s ease;

    &:active {
      opacity: 0.8;
    }
  }

  .product-image {
    width: 100%;
    height: 300rpx;
    background-color: $color-background;
  }

  .product-info {
    padding: $spacing-md;
  }

  .product-name {
    display: block;
    font-size: $font-size-md;
    font-weight: 600;
    color: $color-text-primary;
    margin-bottom: $spacing-sm;
    @include text-ellipsis(1);
  }

  .product-desc {
    display: block;
    font-size: $font-size-sm;
    color: $color-text-secondary;
    margin-bottom: $spacing-sm;
    @include text-ellipsis(2);
    line-height: 1.4;
  }

  .product-price {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    margin-bottom: $spacing-sm;
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

  .product-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .sales-count,
  .stock-info {
    font-size: $font-size-xs;
    color: $color-text-tertiary;
  }
}

.load-more-section,
.no-more-section {
  padding: $spacing-md;
  text-align: center;
}

.load-more-btn {
  background-color: $color-white;
  border: 1px solid $color-border;
  border-radius: $border-radius-round;
  padding: $spacing-sm $spacing-lg;
  display: inline-block;
  cursor: pointer;
  transition: all 0.2s ease;

  &:active {
    opacity: 0.8;
  }
}

.load-more-text {
  font-size: $font-size-md;
  color: $color-text-primary;
}

.no-more-text {
  font-size: $font-size-sm;
  color: $color-text-tertiary;
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
</style>