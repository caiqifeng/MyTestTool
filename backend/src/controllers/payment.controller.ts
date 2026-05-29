import { Request, Response } from 'express';
import OrderModel from '../models/Order';
import PaymentLog from '../models/PaymentLog';
import { PaymentMethod, PaymentStatus, OrderStatus } from '../../../shared/src/types';
import { asyncHandler } from '../middleware/error';
import config from '../config';

export class PaymentController {
  /**
   * 创建支付订单（微信支付）
   */
  static createPayment = asyncHandler(async (req: Request, res: Response) => {
    console.log('=== createPayment called ===')
    if (!req.user) {
      console.log('No user, returning 401')
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { orderId } = req.body;

    if (!orderId) {
      return res.status(400).json({
        success: false,
        message: '订单ID不能为空'
      });
    }

    // 查找订单
    console.log('Looking for order:', orderId)
    const order = await OrderModel.findById(orderId);
    console.log('Order found:', order ? order._id : 'null')
    if (!order) {
      return res.status(404).json({
        success: false,
        message: '订单不存在'
      });
    }

    // 验证订单归属
    console.log('Verifying order ownership:', order.userId, req.user.userId)
    if (order.userId !== req.user.userId) {
      console.log('Ownership mismatch, returning 403')
      return res.status(403).json({
        success: false,
        message: '无权操作此订单'
      });
    }
    console.log('Order ownership verified')

    // 检查订单状态
    if (order.paymentStatus === PaymentStatus.PAID) {
      return res.status(400).json({
        success: false,
        message: '订单已支付'
      });
    }

    if (order.orderStatus === OrderStatus.CANCELLED) {
      console.log('Order cancelled, returning 400')
      return res.status(400).json({
        success: false,
        message: '订单已取消'
      });
    }
    console.log('Order status check passed')

    // 检查支付方式
    console.log('Checking payment method:', order.paymentMethod)
    if (order.paymentMethod !== PaymentMethod.WECHAT_PAY) {
      console.log('Invalid payment method, returning 400')
      return res.status(400).json({
        success: false,
        message: '仅支持微信支付'
      });
    }
    console.log('Payment method check passed')

    // 检查重复支付
    console.log('Checking duplicate payment...')
    const isDuplicate = await PaymentController.checkDuplicatePayment(orderId, req.user.userId);
    console.log('Duplicate payment check result:', isDuplicate)
    if (isDuplicate) {
      console.log('Duplicate payment detected, returning 400')
      return res.status(400).json({
        success: false,
        message: '订单已在处理中，请勿重复支付'
      });
    }
    console.log('Duplicate payment check passed')

    // 模拟微信支付参数生成
    // 在实际环境中，这里应该调用微信支付V3 API生成支付参数
    console.log('Generating wechat payment params...')
    console.log('Calling PaymentController.generateWechatPaymentParams directly')
    const paymentParams = await PaymentController.generateWechatPaymentParams(order);
    console.log('Payment params generated:', paymentParams)

    // 验证支付签名
    console.log('Validating payment signature...')
    if (!PaymentController.validatePaymentSignature(paymentParams)) {
      return res.status(400).json({
        success: false,
        message: '支付参数验证失败'
      });
    }

    // 更新订单支付状态为处理中
    console.log('Updating order payment status to PENDING')
    order.paymentStatus = PaymentStatus.PENDING;
    await order.save();
    console.log('Order saved')

    // 记录支付日志
    console.log('Logging payment...')
    await PaymentController.logPayment(
      orderId,
      req.user.userId,
      order.paymentMethod,
      order.finalAmount,
      PaymentStatus.PENDING,
      { orderId },
      { paymentParams: { ...paymentParams, paySign: '[REDACTED]' } },
      undefined,
      undefined,
      req
    );
    console.log('Payment logged')
    console.log('res object:', res)
    console.log('About to return response...')
    console.log('Calling res.status(200)...')
    const statusResult = res.status(200)
    console.log('statusResult:', statusResult)
    console.log('statusResult === res:', statusResult === res)
    console.log('Calling res.json()...')
    return statusResult.json({
      success: true,
      data: {
        paymentParams,
        order: {
          id: order._id,
          orderNumber: order.orderNumber,
          finalAmount: order.finalAmount,
          paymentStatus: order.paymentStatus
        }
      }
    });
  });

  /**
   * 处理微信支付回调
   */
  static handlePaymentCallback = asyncHandler(async (req: Request, res: Response) => {
    // 在实际环境中，这里需要验证微信支付回调的签名
    const { orderId, transactionId, paymentStatus } = req.body;

    if (!orderId) {
      return res.status(400).json({
        success: false,
        message: '订单ID不能为空'
      });
    }

    const order = await OrderModel.findById(orderId);
    if (!order) {
      return res.status(404).json({
        success: false,
        message: '订单不存在'
      });
    }

    // 检查支付状态
    let paymentLogStatus: PaymentStatus;
    let errorMessage: string | undefined;

    if (paymentStatus === 'SUCCESS') {
      // 支付成功
      order.paymentStatus = PaymentStatus.PAID;
      paymentLogStatus = PaymentStatus.PAID;

      // 如果订单状态是待处理，更新为已确认
      if (order.orderStatus === OrderStatus.PENDING) {
        order.orderStatus = OrderStatus.CONFIRMED;
      }

      // 保存交易ID
      (order as any).transactionId = transactionId;
    } else {
      // 支付失败
      order.paymentStatus = PaymentStatus.FAILED;
      paymentLogStatus = PaymentStatus.FAILED;
      errorMessage = '支付失败';
    }

    await order.save();

    // 记录支付回调日志
    await PaymentController.logPayment(
      orderId,
      order.userId,
      order.paymentMethod,
      order.finalAmount,
      paymentLogStatus,
      req.body,
      { paymentStatus, transactionId },
      errorMessage,
      transactionId,
      req
    );

    // 返回微信支付要求格式
    res.json({
      code: 'SUCCESS',
      message: '成功'
    });
  });

  /**
   * 查询支付状态
   */
  static getPaymentStatus = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { orderId } = req.params;

    const order = await OrderModel.findById(orderId);
    if (!order) {
      return res.status(404).json({
        success: false,
        message: '订单不存在'
      });
    }

    // 验证订单归属
    if (order.userId !== req.user.userId) {
      return res.status(403).json({
        success: false,
        message: '无权查看此订单'
      });
    }

    // 检查支付是否超时（超过30分钟未支付的订单）
    let isExpired = false;
    if (order.paymentStatus === PaymentStatus.PENDING) {
      const thirtyMinutesAgo = new Date(Date.now() - 30 * 60 * 1000);
      if (order.createdAt < thirtyMinutesAgo) {
        isExpired = true;
        // 可以在这里自动取消订单，但需要谨慎处理
      }
    }

    return res.status(200).json({
      success: true,
      data: {
        orderId: order._id,
        orderNumber: order.orderNumber,
        paymentStatus: order.paymentStatus,
        paymentMethod: order.paymentMethod,
        finalAmount: order.finalAmount,
        createdAt: order.createdAt,
        updatedAt: order.updatedAt,
        isExpired,
        // 如果是待支付状态，返回剩余时间（秒）
        remainingTime: isExpired ? 0 : order.paymentStatus === PaymentStatus.PENDING
          ? Math.max(0, Math.floor((30 * 60 * 1000 - (Date.now() - order.createdAt.getTime())) / 1000))
          : null
      }
    });
  });

  /**
   * 退款申请
   */
  static requestRefund = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { orderId, refundAmount, refundReason } = req.body;

    if (!orderId) {
      return res.status(400).json({
        success: false,
        message: '订单ID不能为空'
      });
    }

    const order = await OrderModel.findById(orderId);
    if (!order) {
      return res.status(404).json({
        success: false,
        message: '订单不存在'
      });
    }

    // 验证订单归属
    console.log('Verifying order ownership:', order.userId, req.user.userId)
    if (order.userId !== req.user.userId) {
      console.log('Ownership mismatch, returning 403')
      return res.status(403).json({
        success: false,
        message: '无权操作此订单'
      });
    }
    console.log('Order ownership verified')

    // 检查订单状态
    if (order.paymentStatus !== PaymentStatus.PAID) {
      return res.status(400).json({
        success: false,
        message: '只有已支付的订单才能退款'
      });
    }

    // 检查退款金额
    const refundAmountNum = parseFloat(refundAmount);
    if (isNaN(refundAmountNum) || refundAmountNum <= 0) {
      return res.status(400).json({
        success: false,
        message: '退款金额无效'
      });
    }

    if (refundAmountNum > order.finalAmount) {
      return res.status(400).json({
        success: false,
        message: '退款金额不能超过订单金额'
      });
    }

    // 模拟退款申请
    // 在实际环境中，这里应该调用微信支付退款API
    const refundData = {
      refundId: `REF_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      orderId: order._id,
      refundAmount: refundAmountNum,
      refundReason: refundReason || '用户申请退款',
      status: 'PROCESSING',
      createdAt: new Date(),
      estimatedCompletionTime: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000) // 3天后
    };

    // 记录退款申请日志
    await PaymentController.logPayment(
      orderId,
      req.user.userId,
      order.paymentMethod,
      refundAmountNum,
      PaymentStatus.REFUNDED,
      req.body,
      refundData,
      undefined,
      undefined,
      req
    );
    console.log('Payment logged')
    console.log('res object:', typeof res.status, res.status)

    return res.status(200).json({
      success: true,
      data: refundData,
      message: '退款申请已提交，正在处理中'
    });
  });

  /**
   * 记录支付日志
   */
  private static async logPayment(
    orderId: string,
    userId: string,
    paymentMethod: PaymentMethod,
    amount: number,
    status: PaymentStatus,
    requestData?: any,
    responseData?: any,
    errorMessage?: string,
    transactionId?: string,
    req?: Request
  ): Promise<void> {
    try {
      console.log('logPayment called', orderId, userId)
      await PaymentLog.create({
        orderId,
        userId,
        transactionId,
        paymentMethod,
        amount,
        status,
        requestData,
        responseData,
        errorMessage,
        ipAddress: req?.ip || req?.headers['x-forwarded-for'] || req?.socket.remoteAddress,
        userAgent: req?.headers['user-agent']
      });
      console.log('Payment log created')
    } catch (error) {
      console.error('记录支付日志失败:', error);
      // 不抛出错误，避免影响主流程
    }
  }

  /**
   * 检查重复支付
   */
  private static async checkDuplicatePayment(orderId: string, userId: string): Promise<boolean> {
    console.log('checkDuplicatePayment called', orderId, userId)
    try {
      // 查找最近10分钟内同一订单的成功支付记录
      const tenMinutesAgo = new Date(Date.now() - 10 * 60 * 1000);
      console.log('Searching for existing payment since', tenMinutesAgo)

      const existingPayment = await PaymentLog.findOne({
        orderId,
        userId,
        status: PaymentStatus.PAID,
        createdAt: { $gte: tenMinutesAgo }
      });
      console.log('Existing payment result:', existingPayment)

      return !!existingPayment;
    } catch (error) {
      console.error('检查重复支付失败:', error);
      return false;
    }
  }

  /**
   * 验证支付签名（模拟实现）
   */
  private static validatePaymentSignature(paymentParams: any): boolean {
    // 模拟签名验证
    // 在实际环境中，这里需要验证微信支付的签名
    return true;
  }

  /**
   * 生成微信支付参数（模拟或真实实现）
   */
  private static async generateWechatPaymentParams(order: any): Promise<any> {
    // 根据配置决定使用模拟支付还是真实支付
    if (config.wechat.useMockPayment) {
      return this.generateMockWechatPaymentParams(order);
    } else {
      return this.generateRealWechatPaymentParams(order);
    }
  }

  /**
   * 生成模拟微信支付参数
   */
  private static async generateMockWechatPaymentParams(order: any): Promise<any> {
    const timestamp = Math.floor(Date.now() / 1000);
    const nonceStr = Math.random().toString(36).substring(2, 15);

    // 模拟支付参数（实际需要微信支付API生成）
    return {
      appId: config.wechat.appId || '模拟AppID',
      timeStamp: timestamp.toString(),
      nonceStr: nonceStr,
      package: `prepay_id=MOCK_PREPAY_ID_${order._id}`,
      signType: 'RSA' as const,
      paySign: `MOCK_PAY_SIGN_${timestamp}_${nonceStr}`,
      // 小程序额外参数
      orderNumber: order.orderNumber,
      totalAmount: order.finalAmount,
      description: `订单支付 - ${order.orderNumber}`
    };
  }

  /**
   * 生成真实微信支付参数（待实现）
   */
  private static async generateRealWechatPaymentParams(order: any): Promise<any> {
    // TODO: 实现真实微信支付V3 API调用
    // 需要：
    // 1. 调用微信支付统一下单API
    // 2. 使用商户证书签名
    // 3. 返回小程序调起支付所需参数

    console.warn('真实微信支付未实现，请配置WECHAT_USE_MOCK_PAYMENT=true或实现支付逻辑');
    console.warn('需要配置以下环境变量：');
    console.warn('- WECHAT_APP_ID: 小程序AppID');
    console.warn('- WECHAT_MCH_ID: 商户号');
    console.warn('- WECHAT_API_V3_KEY: API V3密钥');
    console.warn('- WECHAT_CERT_PATH: 证书路径');
    console.warn('- WECHAT_KEY_PATH: 私钥路径');

    // 检查必要配置
    if (!config.wechat.appId || !config.wechat.mchId || !config.wechat.apiV3Key) {
      throw new Error('微信支付配置不完整，请检查环境变量');
    }

    // 临时返回模拟参数，但标记为开发环境
    const mockParams = await this.generateMockWechatPaymentParams(order);
    return {
      ...mockParams,
      _warning: '真实支付未实现，当前为模拟参数'
    };
  }
}

export default PaymentController;