import api, { ApiResponse } from './index'

interface Address {
  _id: string
  userId: string
  name: string
  phone: string
  province: string
  city: string
  district: string
  detail: string
  postalCode?: string
  isDefault: boolean
  createdAt: string
  updatedAt: string
}

export const addressApi = {
  // 获取地址列表
  getAddresses: (): Promise<ApiResponse<{
    addresses: Address[]
  }>> => {
    return api.get('/addresses')
  },

  // 获取地址详情
  getAddress: (id: string): Promise<ApiResponse<{
    address: Address
  }>> => {
    return api.get(`/addresses/${id}`)
  },

  // 创建地址
  createAddress: (data: Omit<Address, '_id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<ApiResponse<{
    address: Address
  }>> => {
    return api.post('/addresses', data)
  },

  // 更新地址
  updateAddress: (id: string, data: Partial<Address>): Promise<ApiResponse<{
    address: Address
  }>> => {
    return api.put(`/addresses/${id}`, data)
  },

  // 删除地址
  deleteAddress: (id: string): Promise<ApiResponse<{
    success: boolean
  }>> => {
    return api.delete(`/addresses/${id}`)
  },

  // 设置默认地址
  setDefaultAddress: (id: string): Promise<ApiResponse<{
    address: Address
  }>> => {
    return api.put(`/addresses/${id}/default`)
  }
}