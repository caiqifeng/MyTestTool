// frontend/src/store/product.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { productApi } from '../utils/api/product.api'
import { bannerApi } from '../utils/api/banner.api'

interface Product {
  id: string
  name: string
  description: string
  price: number
  originalPrice?: number
  images: string[]
  categoryId: string
  categoryName: string
  stock: number
  sales: number
  specs?: Record<string, string[]>
  createdAt: string
}

interface Category {
  id: string
  name: string
  icon?: string
  parentId?: string
}

interface Banner {
  id: string
  title: string
  description?: string
  image: string
  linkType: 'product' | 'category' | 'url'
  linkTarget?: string
  sortOrder: number
  isActive: boolean
  isCurrentlyActive?: boolean
  startDate?: string
  endDate?: string
  createdAt: string
  updatedAt: string
}

export const useProductStore = defineStore('product', () => {
  // 状态
  const products = ref<Product[]>([])
  const categories = ref<Category[]>([])
  const banners = ref<Banner[]>([])
  const currentProduct = ref<Product | null>(null)
  const searchHistory = ref<string[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // getters
  const getProducts = computed(() => products.value)
  const getCategories = computed(() => categories.value)
  const getBanners = computed(() => banners.value)
  const getCurrentProduct = computed(() => currentProduct.value)
  const getSearchHistory = computed(() => searchHistory.value)
  const getIsLoading = computed(() => isLoading.value)
  const getError = computed(() => error.value)

  // 辅助函数：将规格数组转换为记录格式
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
  }

  // 工具函数：将后端产品数据转换为前端格式
  const transformBackendProduct = (backendProduct: any): Product => ({
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
    createdAt: backendProduct.createdAt
  })

  // 工具函数：将后端分类数据转换为前端格式
  const transformBackendCategory = (backendCategory: any): Category => ({
    id: backendCategory._id,
    name: backendCategory.name,
    icon: backendCategory.icon,
    parentId: backendCategory.parentId
  })

  // actions
  const fetchProducts = async (params?: any) => {
    try {
      isLoading.value = true
      error.value = null
      const response = await productApi.getProducts(params)
      if (response.success && response.data.products) {
        products.value = response.data.products.map(transformBackendProduct)
      } else {
        error.value = response.message || '获取产品列表失败'
      }
    } catch (err: any) {
      error.value = err.message || '请求产品列表失败'
      console.error('获取产品列表失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  const fetchCategories = async () => {
    try {
      isLoading.value = true
      error.value = null
      const response = await productApi.getCategories()
      if (response.success && response.data) {
        categories.value = response.data.map(transformBackendCategory)
      } else {
        error.value = response.message || '获取分类列表失败'
      }
    } catch (err: any) {
      error.value = err.message || '请求分类列表失败'
      console.error('获取分类列表失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  const fetchBanners = async (params?: { activeOnly?: 'true' | 'false'; limit?: number }) => {
    try {
      isLoading.value = true
      error.value = null
      const response = await bannerApi.getBanners(params)
      if (response.success && response.data.banners) {
        banners.value = response.data.banners.map((banner: any) => ({
          id: banner._id,
          title: banner.title,
          description: banner.description,
          image: banner.image,
          linkType: banner.linkType,
          linkTarget: banner.linkTarget,
          sortOrder: banner.sortOrder,
          isActive: banner.isActive,
          isCurrentlyActive: banner.isCurrentlyActive,
          startDate: banner.startDate,
          endDate: banner.endDate,
          createdAt: banner.createdAt,
          updatedAt: banner.updatedAt
        }))
      } else {
        error.value = response.message || '获取banner列表失败'
      }
    } catch (err: any) {
      error.value = err.message || '请求banner列表失败'
      console.error('获取banner列表失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  const fetchProductById = async (id: string) => {
    try {
      isLoading.value = true
      error.value = null
      const response = await productApi.getProduct(id)
      if (response.success && response.data) {
        currentProduct.value = transformBackendProduct(response.data)
      } else {
        error.value = response.message || '获取产品详情失败'
      }
    } catch (err: any) {
      error.value = err.message || '请求产品详情失败'
      console.error('获取产品详情失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  const searchProducts = async (keyword: string, params?: any) => {
    try {
      isLoading.value = true
      error.value = null
      const response = await productApi.searchProducts(keyword, params)
      if (response.success && response.data.products) {
        products.value = response.data.products.map(transformBackendProduct)
        addSearchHistory(keyword)
      } else {
        error.value = response.message || '搜索产品失败'
      }
    } catch (err: any) {
      error.value = err.message || '请求搜索失败'
      console.error('搜索产品失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  const setProducts = (newProducts: Product[]) => {
    products.value = newProducts
  }

  const setCategories = (newCategories: Category[]) => {
    categories.value = newCategories
  }

  const setCurrentProduct = (product: Product | null) => {
    currentProduct.value = product
  }

  const addSearchHistory = (keyword: string) => {
    if (!keyword.trim()) return

    searchHistory.value = searchHistory.value.filter(item => item !== keyword)
    searchHistory.value.unshift(keyword)
    if (searchHistory.value.length > 10) {
      searchHistory.value = searchHistory.value.slice(0, 10)
    }
  }

  const clearSearchHistory = () => {
    searchHistory.value = []
  }

  const clearCurrentProduct = () => {
    currentProduct.value = null
  }

  return {
    // 状态
    products,
    categories,
    currentProduct,
    searchHistory,
    isLoading,
    error,

    // getters
    getProducts,
    getCategories,
    getBanners,
    getCurrentProduct,
    getSearchHistory,
    getIsLoading,
    getError,

    // actions
    fetchProducts,
    fetchCategories,
    fetchBanners,
    fetchProductById,
    searchProducts,
    setProducts,
    setCategories,
    setCurrentProduct,
    addSearchHistory,
    clearSearchHistory,
    clearCurrentProduct,
  }
})