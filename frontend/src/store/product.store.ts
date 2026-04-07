// frontend/src/store/product.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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

interface ProductState {
  products: Product[]
  categories: Category[]
  currentProduct: Product | null
  searchHistory: string[]
}

export const useProductStore = defineStore('product', () => {
  // 状态
  const products = ref<Product[]>([])
  const categories = ref<Category[]>([])
  const currentProduct = ref<Product | null>(null)
  const searchHistory = ref<string[]>([])

  // getters
  const getProducts = computed(() => products.value)
  const getCategories = computed(() => categories.value)
  const getCurrentProduct = computed(() => currentProduct.value)
  const getSearchHistory = computed(() => searchHistory.value)

  // actions
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

    // getters
    getProducts,
    getCategories,
    getCurrentProduct,
    getSearchHistory,

    // actions
    setProducts,
    setCategories,
    setCurrentProduct,
    addSearchHistory,
    clearSearchHistory,
    clearCurrentProduct,
  }
})