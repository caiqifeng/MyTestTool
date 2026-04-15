import api, { ApiResponse } from './index'

interface PaymentParams {
  appId: string
  timeStamp: string
  nonceStr: string
  package: string
  signType: 'RSA'
  paySign: string
  orderNumber: string
  totalAmount: number
  description: string
}

interface CreatePaymentRequest {
  orderId: string
}

interface CreatePaymentResponse {
  paymentParams: PaymentParams
  order: {
    id: string
    orderNumber: string
    finalAmount: number
    paymentStatus: string
  }
}

interface PaymentStatusResponse {
  orderId: string
  orderNumber: string
  paymentStatus: string
  paymentMethod: string
  finalAmount: number
  createdAt: string
  updatedAt: string
}

interface RefundRequest {
  orderId: string
  refundAmount: number
  refundReason?: string
}

interface RefundResponse {
  refundId: string
  orderId: string
  refundAmount: number
  refundReason: string
  status: string
  createdAt: string
  estimatedCompletionTime: string
}

export const paymentApi = {
  // 创建支付订单
  createPayment: (data: CreatePaymentRequest): Promise<ApiResponse<CreatePaymentResponse>> => {
    return api.post('/payments/create', data)
  },

  // 查询支付状态
  getPaymentStatus: (orderId: string): Promise<ApiResponse<PaymentStatusResponse>> => {
    return api.get(`/payments/status/${orderId}`)
  },

  // 申请退款
  requestRefund: (data: RefundRequest): Promise<ApiResponse<RefundResponse>> => {
    return api.post('/payments/refund', data)
  },

  // 处理微信支付（小程序端）
  // 注意：此函数应在小程序端调用，使用微信小程序API
  handleWechatPayment: async (paymentParams: PaymentParams): Promise<boolean> => {
    return new Promise((resolve, reject) => {
      // 检查是否在小程序环境中
      if (typeof uni === 'undefined' || !uni.requestPayment) {
        reject(new Error('不在小程序环境中，无法调用微信支付'))
        return
      }

      uni.requestPayment({
        provider: 'wxpay',
        ...paymentParams,
        success: () => {
          resolve(true)
        },
        fail: (err: any) => {
          reject(new Error(`微信支付失败: ${err.errMsg || '未知错误'}`))
        }
      })
    })
  },

  // 模拟支付（开发环境使用）
  simulatePayment: (orderId: string): Promise<ApiResponse<{ success: boolean }>> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        // 模拟90%成功率
        const success = Math.random() < 0.9
        resolve({
          success: true,
          data: { success },
          message: success ? '模拟支付成功' : '模拟支付失败'
        })
      }, 1500)
    })
  }
}