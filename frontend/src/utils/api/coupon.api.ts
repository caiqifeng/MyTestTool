import api, { ApiResponse } from './index'

interface Coupon {
  _id: string
  code: string
  name: string
  description?: string
  discountType: 'percentage' | 'fixed'
  discountValue: number
  minOrderAmount?: number
  maxDiscountAmount?: number
  startDate: string
  endDate: string
  usageLimit?: number
  usedCount: number
  isActive: boolean
  applicableCategories?: string[]
  excludedProducts?: string[]
  createdAt: string
  updatedAt: string
}

export const couponApi = {
  // 获取优惠券列表
  getCoupons: (params?: {
    isActive?: boolean
    applicableOnly?: boolean
  }): Promise<ApiResponse<{
    coupons: Coupon[]
  }>> => {
    return api.get('/coupons', { params })
  },

  // 获取优惠券详情
  getCoupon: (id: string): Promise<ApiResponse<{
    coupon: Coupon
  }>> => {
    return api.get(`/coupons/${id}`)
  },

  // 验证优惠券
  validateCoupon: (code: string, orderAmount: number): Promise<ApiResponse<{
    coupon: Coupon
    isValid: boolean
    discountAmount: number
    message?: string
  }>> => {
    return api.post('/coupons/validate', { code, orderAmount })
  },

  // 用户领取优惠券
  claimCoupon: (code: string): Promise<ApiResponse<{
    coupon: Coupon
  }>> => {
    return api.post('/coupons/claim', { code })
  },

  // 获取用户优惠券
  getUserCoupons: (): Promise<ApiResponse<{
    coupons: Coupon[]
  }>> => {
    return api.get('/coupons/user')
  },

  // 使用优惠券
  useCoupon: (code: string, orderId: string): Promise<ApiResponse<{
    success: boolean
  }>> => {
    return api.post('/coupons/use', { code, orderId })
  }
}