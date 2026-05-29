import api, { ApiResponse } from './index'

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

interface ProductQueryParams {
  categoryId?: string
  keyword?: string
  minPrice?: number
  maxPrice?: number
  sortBy?: 'price' | 'sales' | 'createdAt'
  sortOrder?: 'asc' | 'desc'
  page?: number
  pageSize?: number
}

export const productApi = {
  // 获取商品列表
  getProducts: (params?: ProductQueryParams): Promise<ApiResponse<{
    products: Product[]
    total: number
    page: number
    pageSize: number
    totalPages: number
  }>> => {
    return api.get('/products', { params })
  },

  // 获取商品详情
  getProduct: (id: string): Promise<ApiResponse<Product>> => {
    return api.get(`/products/${id}`)
  },

  // 获取商品分类
  getCategories: (): Promise<ApiResponse<Category[]>> => {
    return api.get('/categories')
  },

  // 搜索商品
  searchProducts: (keyword: string, params?: Omit<ProductQueryParams, 'keyword'>): Promise<ApiResponse<{
    products: Product[]
    total: number
  }>> => {
    return api.get('/products/search', { params: { keyword, ...params } })
  },

  // 获取热门商品
  getHotProducts: (limit?: number): Promise<ApiResponse<Product[]>> => {
    return api.get('/products/hot', { params: { limit } })
  },

  // 获取推荐商品
  getRecommendedProducts: (limit?: number): Promise<ApiResponse<Product[]>> => {
    return api.get('/products/recommended', { params: { limit } })
  },
}