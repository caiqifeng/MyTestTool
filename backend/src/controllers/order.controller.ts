import { Request, Response } from 'express';
import OrderModel from '../models/Order';
import ProductModel from '../models/Product';
import CouponModel from '../models/Coupon';
import AddressModel from '../models/Address';
import {
  OrderStatus,
  DeliveryType,
  PaymentMethod,
  PaymentStatus,
  OrderItem,
  ProductSpec
} from '../../../shared/src/types';
import { asyncHandler } from '../middleware/error';

export class OrderController {
  /**
   * 创建订单
   */
  static createOrder = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const {
      items,
      deliveryType,
      deliveryAddressId,
      pickupTime,
      paymentMethod,
      remark,
      couponCode
    } = req.body;

    // 验证购物车项
    if (!items || !Array.isArray(items) || items.length === 0) {
      return res.status(400).json({
        success: false,
        message: '购物车不能为空'
      });
    }

    // 验证配送方式
    if (!Object.values(DeliveryType).includes(deliveryType)) {
      return res.status(400).json({
        success: false,
        message: '无效的配送方式'
      });
    }

    // 验证支付方式
    if (!Object.values(PaymentMethod).includes(paymentMethod)) {
      return res.status(400).json({
        success: false,
        message: '无效的支付方式'
      });
    }

    // 如果是配送，需要地址
    let deliveryAddress = null;
    if (deliveryType === DeliveryType.DELIVERY) {
      if (!deliveryAddressId) {
        return res.status(400).json({
          success: false,
          message: '配送地址不能为空'
        });
      }

      const address = await AddressModel.findOne({
        _id: deliveryAddressId,
        userId: req.user.userId
      });

      if (!address) {
        return res.status(404).json({
          success: false,
          message: '地址不存在'
        });
      }

      deliveryAddress = {
        contactName: address.contactName,
        contactPhone: address.contactPhone,
        province: address.province,
        city: address.city,
        district: address.district,
        detail: address.detail
      };
    }

    // 如果是自提，需要提货时间
    if (deliveryType === DeliveryType.PICKUP && !pickupTime) {
      return res.status(400).json({
        success: false,
        message: '提货时间不能为空'
      });
    }

    // 验证商品库存和价格
    let totalAmount = 0;
    const orderItems: OrderItem[] = [];

    for (const item of items) {
      const product = await ProductModel.findById(item.productId);

      if (!product) {
        return res.status(404).json({
          success: false,
          message: `商品不存在: ${item.productId}`
        });
      }

      if (product.stock < item.quantity) {
        return res.status(400).json({
          success: false,
          message: `商品库存不足: ${product.name}`
        });
      }

      if (product.price !== item.price) {
        return res.status(400).json({
          success: false,
          message: `商品价格已更新: ${product.name}`
        });
      }

      totalAmount += product.price * item.quantity;

      orderItems.push({
        productId: product._id.toString(),
        name: product.name,
        price: product.price,
        quantity: item.quantity,
        image: product.images[0] || '',
        specs: item.specs || []
      });
    }

    // 计算配送费
    const deliveryFee = deliveryType === DeliveryType.DELIVERY ? 5 : 0; // 配送费5元

    // 验证优惠券
    let discountAmount = 0;
    let couponId = undefined;

    if (couponCode) {
      const coupon = await CouponModel.findOne({
        code: couponCode,
        isActive: true,
        startDate: { $lte: new Date() },
        endDate: { $gte: new Date() },
        usageLimit: { $gt: 0 }
      });

      if (!coupon) {
        return res.status(400).json({
          success: false,
          message: '优惠券无效或已过期'
        });
      }

      // 检查用户是否已使用过此优惠券
      const usedCoupon = await OrderModel.findOne({
        userId: req.user.userId,
        couponId: coupon._id
      });

      if (usedCoupon) {
        return res.status(400).json({
          success: false,
          message: '此优惠券已使用过'
        });
      }

      // 计算优惠金额
      if (coupon.discountType === 'percentage') {
        discountAmount = totalAmount * (coupon.discountValue / 100);
      } else {
        discountAmount = coupon.discountValue;
      }

      // 优惠金额不能超过订单总额
      discountAmount = Math.min(discountAmount, totalAmount);
      couponId = coupon._id.toString();
    }

    const finalAmount = totalAmount + deliveryFee - discountAmount;

    // 创建订单
    const order = new OrderModel({
      userId: req.user.userId,
      items: orderItems,
      totalAmount,
      deliveryFee,
      discountAmount,
      finalAmount,
      deliveryType,
      deliveryAddress,
      pickupTime: deliveryType === DeliveryType.PICKUP ? new Date(pickupTime) : undefined,
      paymentMethod,
      paymentStatus: PaymentStatus.PENDING,
      orderStatus: OrderStatus.PENDING,
      remark,
      couponId
    });

    await order.save();

    // 更新商品库存
    for (const item of orderItems) {
      await ProductModel.findByIdAndUpdate(item.productId, {
        $inc: { stock: -item.quantity, salesCount: item.quantity }
      });
    }

    // 更新优惠券使用次数
    if (couponId) {
      await CouponModel.findByIdAndUpdate(couponId, {
        $inc: { usageLimit: -1, usedCount: 1 }
      });
    }

    res.status(201).json({
      success: true,
      data: {
        order: {
          _id: order._id,
          orderNumber: order.orderNumber,
          userId: order.userId,
          items: order.items,
          totalAmount: order.totalAmount,
          deliveryFee: order.deliveryFee,
          discountAmount: order.discountAmount,
          finalAmount: order.finalAmount,
          deliveryType: order.deliveryType,
          deliveryAddress: order.deliveryAddress,
          pickupTime: order.pickupTime,
          paymentMethod: order.paymentMethod,
          paymentStatus: order.paymentStatus,
          orderStatus: order.orderStatus,
          remark: order.remark,
          couponId: order.couponId,
          createdAt: order.createdAt,
          updatedAt: order.updatedAt
        }
      }
    });
  });

  /**
   * 获取订单列表
   */
  static getOrders = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const {
      page = 1,
      limit = 10,
      status,
      startDate,
      endDate
    } = req.query;

    const pageNum = parseInt(page as string);
    const limitNum = parseInt(limit as string);
    const skip = (pageNum - 1) * limitNum;

    const query: any = { userId: req.user.userId };

    // 状态过滤
    if (status && Object.values(OrderStatus).includes(status as OrderStatus)) {
      query.orderStatus = status;
    }

    // 日期范围过滤
    if (startDate || endDate) {
      query.createdAt = {};
      if (startDate) query.createdAt.$gte = new Date(startDate as string);
      if (endDate) query.createdAt.$lte = new Date(endDate as string);
    }

    const [orders, total] = await Promise.all([
      OrderModel.find(query)
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limitNum),
      OrderModel.countDocuments(query)
    ]);

    res.json({
      success: true,
      data: {
        orders: orders.map((order: any) => ({
          _id: order._id,
          orderNumber: order.orderNumber,
          items: order.items,
          totalAmount: order.totalAmount,
          deliveryFee: order.deliveryFee,
          discountAmount: order.discountAmount,
          finalAmount: order.finalAmount,
          deliveryType: order.deliveryType,
          paymentMethod: order.paymentMethod,
          paymentStatus: order.paymentStatus,
          orderStatus: order.orderStatus,
          createdAt: order.createdAt,
          updatedAt: order.updatedAt
        })),
        pagination: {
          page: pageNum,
          limit: limitNum,
          total,
          pages: Math.ceil(total / limitNum)
        }
      }
    });
  });

  /**
   * 获取订单详情
   */
  static getOrderById = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { id } = req.params;

    const order = await OrderModel.findOne({
      _id: id,
      userId: req.user.userId
    });

    if (!order) {
      return res.status(404).json({
        success: false,
        message: '订单不存在'
      });
    }

    res.json({
      success: true,
      data: {
        order: {
          _id: order._id,
          orderNumber: order.orderNumber,
          userId: order.userId,
          items: order.items,
          totalAmount: order.totalAmount,
          deliveryFee: order.deliveryFee,
          discountAmount: order.discountAmount,
          finalAmount: order.finalAmount,
          deliveryType: order.deliveryType,
          deliveryAddress: order.deliveryAddress,
          pickupTime: order.pickupTime,
          paymentMethod: order.paymentMethod,
          paymentStatus: order.paymentStatus,
          orderStatus: order.orderStatus,
          remark: order.remark,
          couponId: order.couponId,
          createdAt: order.createdAt,
          updatedAt: order.updatedAt
        }
      }
    });
  });

  /**
   * 取消订单
   */
  static cancelOrder = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { id } = req.params;

    const order = await OrderModel.findOne({
      _id: id,
      userId: req.user.userId
    });

    if (!order) {
      return res.status(404).json({
        success: false,
        message: '订单不存在'
      });
    }

    // 检查订单状态是否可以取消
    const cancellableStatuses = [
      OrderStatus.PENDING,
      'paid',
      OrderStatus.CONFIRMED
    ];

    if (!cancellableStatuses.includes(order.orderStatus)) {
      return res.status(400).json({
        success: false,
        message: '订单当前状态不可取消'
      });
    }

    // 更新订单状态
    order.orderStatus = OrderStatus.CANCELLED;
    await order.save();

    // 恢复商品库存
    for (const item of order.items) {
      await ProductModel.findByIdAndUpdate(item.productId, {
        $inc: { stock: item.quantity, salesCount: -item.quantity }
      });
    }

    // 恢复优惠券使用次数
    if (order.couponId) {
      await CouponModel.findByIdAndUpdate(order.couponId, {
        $inc: { usageLimit: 1, usedCount: -1 }
      });
    }

    res.json({
      success: true,
      data: {
        order: {
          _id: order._id,
          orderNumber: order.orderNumber,
          orderStatus: order.orderStatus,
          updatedAt: order.updatedAt
        }
      },
      message: '订单取消成功'
    });
  });

  /**
   * 更新订单状态（管理员）
   */
  static updateOrderStatus = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const { status } = req.body;

    if (!Object.values(OrderStatus).includes(status as OrderStatus)) {
      return res.status(400).json({
        success: false,
        message: '无效的订单状态'
      });
    }

    const order = await OrderModel.findById(id);

    if (!order) {
      return res.status(404).json({
        success: false,
        message: '订单不存在'
      });
    }

    // 更新订单状态
    order.orderStatus = status as OrderStatus;
    await order.save();

    res.json({
      success: true,
      data: {
        order: {
          _id: order._id,
          orderNumber: order.orderNumber,
          orderStatus: order.orderStatus,
          updatedAt: order.updatedAt
        }
      },
      message: '订单状态更新成功'
    });
  });

  /**
   * 更新支付状态（管理员）
   */
  static updatePaymentStatus = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const { paymentStatus } = req.body;

    if (!Object.values(PaymentStatus).includes(paymentStatus as PaymentStatus)) {
      return res.status(400).json({
        success: false,
        message: '无效的支付状态'
      });
    }

    const order = await OrderModel.findById(id);

    if (!order) {
      return res.status(404).json({
        success: false,
        message: '订单不存在'
      });
    }

    // 更新支付状态
    order.paymentStatus = paymentStatus as PaymentStatus;

    // 如果支付成功，更新订单状态为已支付
    if (paymentStatus === PaymentStatus.PAID && order.orderStatus === OrderStatus.PENDING) {
      (order as any).orderStatus = 'paid';
    }

    await order.save();

    res.json({
      success: true,
      data: {
        order: {
          _id: order._id,
          orderNumber: order.orderNumber,
          paymentStatus: order.paymentStatus,
          orderStatus: order.orderStatus,
          updatedAt: order.updatedAt
        }
      },
      message: '支付状态更新成功'
    });
  });

  /**
   * 获取订单统计（管理员）
   */
  static getOrderStats = asyncHandler(async (req: Request, res: Response) => {
    const { startDate, endDate } = req.query;

    const start = startDate ? new Date(startDate as string) : undefined;
    const end = endDate ? new Date(endDate as string) : undefined;

    // 获取状态统计
    const statusStats = await OrderModel.getStatusStats(start, end);

    // 获取销售总额
    const salesResult = await OrderModel.aggregate([
      {
        $match: {
          orderStatus: OrderStatus.COMPLETED,
          ...(start || end ? {
            createdAt: {
              ...(start ? { $gte: start } : {}),
              ...(end ? { $lte: end } : {})
            }
          } : {})
        }
      },
      {
        $group: {
          _id: null,
          totalSales: { $sum: '$finalAmount' },
          orderCount: { $sum: 1 }
        }
      }
    ]);

    const totalSales = salesResult[0]?.totalSales || 0;
    const completedOrderCount = salesResult[0]?.orderCount || 0;

    // 获取最近订单
    const recentOrders = await OrderModel.find()
      .sort({ createdAt: -1 })
      .limit(5)
      .select('orderNumber userId finalAmount orderStatus createdAt');

    res.json({
      success: true,
      data: {
        stats: {
          status: statusStats,
          totalSales,
          completedOrderCount
        },
        recentOrders
      }
    });
  });
}

export default OrderController;