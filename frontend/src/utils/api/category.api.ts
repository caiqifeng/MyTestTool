import api, { ApiResponse } from './index'

export interface Category {
  _id: string
  name: string
  description?: string
  icon?: string
  sortOrder: number
  parentId?: string
  createdAt: string
  updatedAt: string
}

export const categoryApi = {
  // 获取分类列表
  getCategories: (): Promise<ApiResponse<{
    categories: Category[]
  }>> => {
    return api.get('/categories')
  },

  // 获取分类详情
  getCategory: (id: string): Promise<ApiResponse<{
    category: Category
  }>> => {
    return api.get(`/categories/${id}`)
  },

  // 获取分类下的商品
  getCategoryProducts: (
    categoryId: string,
    params?: {
      page?: number
      limit?: number
      sortBy?: string
      sortOrder?: 'asc' | 'desc'
    }
  ): Promise<ApiResponse<{
    products: any[]
    total: number
    page: number
    limit: number
    totalPages: number
  }>> => {
    return api.get(`/products/category/${categoryId}`, { params })
  }
}