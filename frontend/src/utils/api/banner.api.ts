import api, { ApiResponse } from './index'

interface Banner {
  _id: string
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

export const bannerApi = {
  // 获取banner列表
  getBanners: (params?: {
    activeOnly?: 'true' | 'false'
    limit?: number
  }): Promise<ApiResponse<{
    banners: Banner[]
  }>> => {
    return api.get('/banners', { params })
  },

  // 获取banner详情
  getBanner: (id: string): Promise<ApiResponse<{
    banner: Banner
  }>> => {
    return api.get(`/banners/${id}`)
  },

  // 创建banner（管理员）
  createBanner: (data: Omit<Banner, '_id' | 'createdAt' | 'updatedAt' | 'isCurrentlyActive'>): Promise<ApiResponse<{
    banner: Banner
  }>> => {
    return api.post('/banners', data)
  },

  // 更新banner（管理员）
  updateBanner: (id: string, data: Partial<Banner>): Promise<ApiResponse<{
    banner: Banner
  }>> => {
    return api.put(`/banners/${id}`, data)
  },

  // 删除banner（管理员）
  deleteBanner: (id: string): Promise<ApiResponse<{
    success: boolean
  }>> => {
    return api.delete(`/banners/${id}`)
  },

  // 更新banner排序（管理员）
  updateBannerOrder: (data: {
    orders: Array<{
      id: string
      sortOrder: number
    }>
  }): Promise<ApiResponse<{
    banners: Array<{
      _id: string
      title: string
      sortOrder: number
      updatedAt: string
    }>
  }>> => {
    return api.put('/banners/order', data)
  },

  // 批量更新banner状态（管理员）
  batchUpdateBannerStatus: (data: {
    ids: string[]
    isActive: boolean
  }): Promise<ApiResponse<{
    matchedCount: number
    modifiedCount: number
  }>> => {
    return api.put('/banners/batch-status', data)
  }
}