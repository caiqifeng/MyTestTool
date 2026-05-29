import api, { ApiResponse } from './index'

// 前端使用的地址接口
interface Address {
  _id: string
  userId: string
  name: string  // 前端使用 name
  phone: string // 前端使用 phone
  province: string
  city: string
  district: string
  detail: string
  postalCode?: string
  isDefault: boolean
  createdAt: string
  updatedAt: string
}

// 后端需要的地址接口
interface BackendAddress {
  _id: string
  userId: string
  contactName: string  // 后端使用 contactName
  contactPhone: string // 后端使用 contactPhone
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
    return api.get('/addresses').then(response => {
      // 转换字段名：后端 contactName/contactPhone -> 前端 name/phone
      if (response.success && response.data.addresses) {
        response.data.addresses = response.data.addresses.map((addr: any) => ({
          _id: addr._id,
          userId: addr.userId,
          name: addr.contactName,    // 转换
          phone: addr.contactPhone,  // 转换
          province: addr.province,
          city: addr.city,
          district: addr.district,
          detail: addr.detail,
          postalCode: addr.postalCode,
          isDefault: addr.isDefault,
          createdAt: addr.createdAt,
          updatedAt: addr.updatedAt
        }))
      }
      return response
    })
  },

  // 获取地址详情
  getAddress: (id: string): Promise<ApiResponse<{
    address: Address
  }>> => {
    return api.get(`/addresses/${id}`).then(response => {
      // 转换字段名：后端 contactName/contactPhone -> 前端 name/phone
      if (response.success && response.data.address) {
        const backendAddr = response.data.address
        response.data.address = {
          _id: backendAddr._id,
          userId: backendAddr.userId,
          name: backendAddr.contactName,    // 转换
          phone: backendAddr.contactPhone,  // 转换
          province: backendAddr.province,
          city: backendAddr.city,
          district: backendAddr.district,
          detail: backendAddr.detail,
          postalCode: backendAddr.postalCode,
          isDefault: backendAddr.isDefault,
          createdAt: backendAddr.createdAt,
          updatedAt: backendAddr.updatedAt
        }
      }
      return response
    })
  },

  // 创建地址
  createAddress: (data: Omit<Address, '_id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<ApiResponse<{
    address: Address
  }>> => {
    // 转换字段名：前端 name/phone -> 后端 contactName/contactPhone
    const backendData = {
      contactName: data.name,
      contactPhone: data.phone,
      province: data.province,
      city: data.city,
      district: data.district,
      detail: data.detail,
      postalCode: data.postalCode,
      isDefault: data.isDefault
    }
    return api.post('/addresses', backendData)
  },

  // 更新地址
  updateAddress: (id: string, data: Partial<Address>): Promise<ApiResponse<{
    address: Address
  }>> => {
    // 转换字段名：前端 name/phone -> 后端 contactName/contactPhone
    const backendData: any = {}
    if (data.name !== undefined) backendData.contactName = data.name
    if (data.phone !== undefined) backendData.contactPhone = data.phone
    if (data.province !== undefined) backendData.province = data.province
    if (data.city !== undefined) backendData.city = data.city
    if (data.district !== undefined) backendData.district = data.district
    if (data.detail !== undefined) backendData.detail = data.detail
    if (data.postalCode !== undefined) backendData.postalCode = data.postalCode
    if (data.isDefault !== undefined) backendData.isDefault = data.isDefault

    return api.put(`/addresses/${id}`, backendData)
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
    return api.put(`/addresses/${id}/default`).then(response => {
      // 转换字段名：后端 contactName/contactPhone -> 前端 name/phone
      if (response.success && response.data.address) {
        const backendAddr = response.data.address
        response.data.address = {
          _id: backendAddr._id,
          userId: backendAddr.userId,
          name: backendAddr.contactName || '',    // 转换，可能后端不返回完整地址信息
          phone: backendAddr.contactPhone || '',  // 转换，可能后端不返回完整地址信息
          province: backendAddr.province || '',
          city: backendAddr.city || '',
          district: backendAddr.district || '',
          detail: backendAddr.detail || '',
          postalCode: backendAddr.postalCode,
          isDefault: backendAddr.isDefault,
          createdAt: backendAddr.createdAt,
          updatedAt: backendAddr.updatedAt
        }
      }
      return response
    })
  }
}