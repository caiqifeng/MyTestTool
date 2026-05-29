import api, { ApiResponse } from './index'

interface OrderItem {
  productId: string
  name: string
  price: number
  quantity: number
  image: string
  specs?: Record<string, string>
}

interface Order {
  _id: string
  orderNumber: string
  userId: string
  items: OrderItem[]
  subtotal: number
  deliveryFee: number
  discount: number
  total: number
  deliveryType: string
  deliveryAddressId?: string
  pickupTime?: string
  paymentMethod: string
  paymentStatus: string
  orderStatus: string
  remark?: string
  couponCode?: string
  createdAt: string
  updatedAt: string
}

interface CreateOrderRequest {
  items: OrderItem[]
  deliveryType: string
  deliveryAddressId?: string
  pickupTime?: string
  paymentMethod: string
  remark?: string
  couponCode?: string
}

export const orderApi = {
  // 创建订单
  createOrder: (data: CreateOrderRequest): Promise<ApiResponse<{ order: Order }>> => {
    return api.post('/orders', data)
  },

  // 获取订单列表
  getOrders: (params?: {
    page?: number
    limit?: number
    status?: string
    startDate?: string
    endDate?: string
  }): Promise<ApiResponse<{
    orders: Order[]
    total: number
    page: number
    limit: number
    totalPages: number
  }>> => {
    return api.get('/orders', { params })
  },

  // 获取订单详情
  getOrder: (id: string): Promise<ApiResponse<{ order: Order }>> => {
    return api.get(`/orders/${id}`)
  },

  // 取消订单
  cancelOrder: (id: string): Promise<ApiResponse<{ order: Order }>> => {
    return api.put(`/orders/${id}/cancel`)
  },

  // 更新订单状态（管理员）
  updateOrderStatus: (id: string, status: string): Promise<ApiResponse<{ order: Order }>> => {
    return api.put(`/orders/${id}/status`, { status })
  },

  // 获取订单统计
  getOrderStats: (): Promise<ApiResponse<{
    totalOrders: number
    totalRevenue: number
    pendingOrders: number
    completedOrders: number
    cancelledOrders: number
  }>> => {
    return api.get('/orders/stats')
  }
}