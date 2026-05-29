import { paymentApi } from './api/payment.api'

export interface PaymentStatus {
  orderId: string
  orderNumber: string
  paymentStatus: string
  paymentMethod: string
  finalAmount: number
  createdAt: string
  updatedAt: string
  isExpired: boolean
  remainingTime: number | null
}

export interface PaymentPollingOptions {
  interval?: number  // 轮询间隔，默认3秒
  timeout?: number  // 超时时间，默认5分钟
  onSuccess?: (status: PaymentStatus) => void
  onError?: (error: Error) => void
  onTimeout?: () => void
  onStatusChange?: (status: PaymentStatus) => void
}

export class PaymentPollingService {
  private orderId: string
  private options: Required<PaymentPollingOptions>
  private pollingInterval: number | null = null
  private startTime: number = 0
  private lastStatus: string = ''
  private isStopped: boolean = false

  constructor(orderId: string, options: PaymentPollingOptions = {}) {
    this.orderId = orderId
    this.options = {
      interval: options.interval || 3000, // 3秒
      timeout: options.timeout || 5 * 60 * 1000, // 5分钟
      onSuccess: options.onSuccess || (() => {}),
      onError: options.onError || (() => {}),
      onTimeout: options.onTimeout || (() => {}),
      onStatusChange: options.onStatusChange || (() => {})
    }
  }

  /**
   * 开始轮询支付状态
   */
  start(): void {
    if (this.isStopped) {
      console.warn('支付轮询服务已停止，无法重新开始')
      return
    }

    this.startTime = Date.now()
    this.lastStatus = ''

    // 立即检查一次
    this.checkPaymentStatus()

    // 设置轮询间隔
    this.pollingInterval = setInterval(() => {
      this.checkPaymentStatus()
    }, this.options.interval) as unknown as number
  }

  /**
   * 停止轮询
   */
  stop(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
      this.pollingInterval = null
    }
    this.isStopped = true
  }

  /**
   * 检查是否超时
   */
  private checkTimeout(): boolean {
    const elapsed = Date.now() - this.startTime
    if (elapsed > this.options.timeout) {
      this.stop()
      this.options.onTimeout()
      return true
    }
    return false
  }

  /**
   * 检查支付状态
   */
  private async checkPaymentStatus(): Promise<void> {
    if (this.isStopped) {
      return
    }

    // 检查超时
    if (this.checkTimeout()) {
      return
    }

    try {
      const response = await paymentApi.getPaymentStatus(this.orderId)

      if (!response.success || !response.data) {
        throw new Error(response.message || '获取支付状态失败')
      }

      const status = response.data as PaymentStatus

      // 检查状态变化
      if (status.paymentStatus !== this.lastStatus) {
        this.lastStatus = status.paymentStatus
        this.options.onStatusChange(status)

        // 根据状态执行相应操作
        switch (status.paymentStatus) {
          case 'paid':
            this.stop()
            this.options.onSuccess(status)
            break

          case 'failed':
            this.stop()
            this.options.onError(new Error('支付失败'))
            break

          case 'refunded':
            this.stop()
            this.options.onError(new Error('订单已退款'))
            break

          // 对于pending状态，继续轮询
        }
      }

      // 检查是否过期
      if (status.isExpired) {
        this.stop()
        this.options.onTimeout()
      }

    } catch (error: any) {
      console.error('检查支付状态失败:', error)

      // 如果错误是网络相关，可以继续轮询
      if (error.message.includes('网络') || error.message.includes('连接')) {
        // 网络错误，继续轮询
        return
      }

      // 其他错误停止轮询
      this.stop()
      this.options.onError(error)
    }
  }

  /**
   * 手动查询支付状态（单次）
   */
  static async getPaymentStatus(orderId: string): Promise<PaymentStatus> {
    const response = await paymentApi.getPaymentStatus(orderId)

    if (!response.success || !response.data) {
      throw new Error(response.message || '获取支付状态失败')
    }

    return response.data as PaymentStatus
  }

  /**
   * 启动支付轮询的便捷方法
   */
  static startPolling(
    orderId: string,
    options: PaymentPollingOptions
  ): PaymentPollingService {
    const service = new PaymentPollingService(orderId, options)
    service.start()
    return service
  }
}

/**
 * 检查订单支付状态的便捷函数
 */
export async function checkPaymentStatus(orderId: string): Promise<PaymentStatus> {
  return PaymentPollingService.getPaymentStatus(orderId)
}

/**
 * 启动支付轮询的便捷函数
 */
export function startPaymentPolling(
  orderId: string,
  options: PaymentPollingOptions
): PaymentPollingService {
  return PaymentPollingService.startPolling(orderId, options)
}