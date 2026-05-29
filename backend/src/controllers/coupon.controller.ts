import { Request, Response } from 'express';
import CouponModel from '../models/Coupon';
import OrderModel from '../models/Order';
import { asyncHandler } from '../middleware/error';

export class CouponController {
  /**
   * 获取可用优惠券列表
   */
  static getAvailableCoupons = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { orderAmount, productIds, categoryIds } = req.query;

    const now = new Date();
    const query: any = {
      isActive: true,
      startDate: { $lte: now },
      endDate: { $gte: now }
    };

    // 如果有使用限制，检查是否还有可用次数
    query.$or = [
      { usageLimit: { $exists: false } },
      { usageLimit: { $gt: 0 } },
      { $expr: { $lt: ['$usedCount', '$usageLimit'] } }
    ];

    const coupons = await CouponModel.find(query).sort({ discountValue: -1, createdAt: -1 });

    // 如果有订单金额，过滤符合条件的优惠券
    let availableCoupons = coupons;

    if (orderAmount) {
      const amount = parseFloat(orderAmount as string);
      const productIdArray = productIds ? (productIds as string).split(',') : undefined;
      const categoryIdArray = categoryIds ? (categoryIds as string).split(',') : undefined;

      availableCoupons = coupons.filter(coupon => {
        return coupon.canApplyToOrder(amount, productIdArray, categoryIdArray);
      });
    }

    // 检查用户是否已使用过优惠券
    const userCoupons = await OrderModel.find({
      userId: req.user.userId,
      couponId: { $exists: true }
    }).distinct('couponId');

    const result = availableCoupons.map((coupon: any) => {
      const isUsed = userCoupons.some((usedCouponId: any) =>
        usedCouponId.toString() === coupon._id.toString()
      );

      return {
        _id: coupon._id,
        code: coupon.code,
        name: coupon.name,
        description: coupon.description,
        discountType: coupon.discountType,
        discountValue: coupon.discountValue,
        minPurchaseAmount: coupon.minPurchaseAmount,
        maxDiscountAmount: coupon.maxDiscountAmount,
        startDate: coupon.startDate,
        endDate: coupon.endDate,
        usageLimit: coupon.usageLimit,
        usedCount: coupon.usedCount,
        isActive: coupon.isActive,
        applicableCategories: coupon.applicableCategories,
        applicableProducts: coupon.applicableProducts,
        isValid: coupon.isValid,
        isUsed,
        remainingUses: coupon.usageLimit ? coupon.usageLimit - coupon.usedCount : null,
        createdAt: coupon.createdAt,
        updatedAt: coupon.updatedAt
      };
    });

    res.json({
      success: true,
      data: {
        coupons: result
      }
    });
  });

  /**
   * 获取用户优惠券
   */
  static getUserCoupons = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    // 获取用户使用过的优惠券
    const userOrders = await OrderModel.find({
      userId: req.user.userId,
      couponId: { $exists: true }
    }).populate('couponId');

    const userCoupons = userOrders
      .filter((order: any) => order.couponId)
      .map((order: any) => ({
        coupon: order.couponId,
        orderId: order._id,
        orderNumber: order.orderNumber,
        usedAt: order.createdAt,
        discountAmount: order.discountAmount
      }));

    res.json({
      success: true,
      data: {
        coupons: userCoupons.map(item => ({
          _id: item.coupon._id,
          code: item.coupon.code,
          name: item.coupon.name,
          description: item.coupon.description,
          discountType: item.coupon.discountType,
          discountValue: item.coupon.discountValue,
          discountAmount: item.discountAmount,
          orderId: item.orderId,
          orderNumber: item.orderNumber,
          usedAt: item.usedAt,
          createdAt: item.coupon.createdAt
        }))
      }
    });
  });

  /**
   * 领取优惠券
   */
  static claimCoupon = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { code } = req.params;

    const coupon = await CouponModel.findOne({ code });

    if (!coupon) {
      return res.status(404).json({
        success: false,
        message: '优惠券不存在'
      });
    }

    // 检查优惠券是否有效
    if (!coupon.isValid) {
      return res.status(400).json({
        success: false,
        message: '优惠券无效或已过期'
      });
    }

    // 检查用户是否已领取过（这里简化处理，实际可能需要用户优惠券表）
    // 在实际应用中，可能需要创建用户优惠券关联表
    const userUsedCoupon = await OrderModel.findOne({
      userId: req.user.userId,
      couponId: coupon._id
    });

    if (userUsedCoupon) {
      return res.status(400).json({
        success: false,
        message: '您已使用过此优惠券'
      });
    }

    // 检查使用限制
    if (coupon.usageLimit && coupon.usedCount >= coupon.usageLimit) {
      return res.status(400).json({
        success: false,
        message: '优惠券已被领完'
      });
    }

    // 在实际应用中，这里应该创建用户优惠券记录
    // 目前简化处理，只返回优惠券信息

    res.json({
      success: true,
      data: {
        coupon: {
          _id: coupon._id,
          code: coupon.code,
          name: coupon.name,
          description: coupon.description,
          discountType: coupon.discountType,
          discountValue: coupon.discountValue,
          minPurchaseAmount: coupon.minPurchaseAmount,
          maxDiscountAmount: coupon.maxDiscountAmount,
          startDate: coupon.startDate,
          endDate: coupon.endDate,
          usageLimit: coupon.usageLimit,
          usedCount: coupon.usedCount,
          isActive: coupon.isActive,
          applicableCategories: coupon.applicableCategories,
          applicableProducts: coupon.applicableProducts,
          isValid: coupon.isValid,
          remainingUses: coupon.usageLimit ? coupon.usageLimit - coupon.usedCount : null,
          createdAt: coupon.createdAt,
          updatedAt: coupon.updatedAt
        }
      },
      message: '优惠券领取成功'
    });
  });

  /**
   * 验证优惠券
   */
  static validateCoupon = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证'
      });
    }

    const { code, orderAmount, productIds, categoryIds } = req.body;

    if (!code) {
      return res.status(400).json({
        success: false,
        message: '优惠券代码不能为空'
      });
    }

    const coupon = await CouponModel.findOne({ code });

    if (!coupon) {
      return res.status(404).json({
        success: false,
        message: '优惠券不存在'
      });
    }

    // 检查优惠券是否有效
    if (!coupon.isValid) {
      return res.status(400).json({
        success: false,
        message: '优惠券无效或已过期'
      });
    }

    // 检查用户是否已使用过
    const userUsedCoupon = await OrderModel.findOne({
      userId: req.user.userId,
      couponId: coupon._id
    });

    if (userUsedCoupon) {
      return res.status(400).json({
        success: false,
        message: '您已使用过此优惠券'
      });
    }

    // 如果有订单金额，验证是否满足条件
    if (orderAmount) {
      const amount = parseFloat(orderAmount);
      const productIdArray = productIds ? (productIds as string).split(',') : undefined;
      const categoryIdArray = categoryIds ? (categoryIds as string).split(',') : undefined;

      if (!coupon.canApplyToOrder(amount, productIdArray, categoryIdArray)) {
        return res.status(400).json({
          success: false,
          message: '优惠券不适用于当前订单'
        });
      }

      // 计算优惠金额
      const discountAmount = coupon.calculateDiscount(amount);

      return res.json({
        success: true,
        data: {
          coupon: {
            _id: coupon._id,
            code: coupon.code,
            name: coupon.name,
            description: coupon.description,
            discountType: coupon.discountType,
            discountValue: coupon.discountValue,
            minPurchaseAmount: coupon.minPurchaseAmount,
            maxDiscountAmount: coupon.maxDiscountAmount,
            discountAmount,
            startDate: coupon.startDate,
            endDate: coupon.endDate,
            usageLimit: coupon.usageLimit,
            usedCount: coupon.usedCount,
            isActive: coupon.isActive,
            applicableCategories: coupon.applicableCategories,
            applicableProducts: coupon.applicableProducts,
            isValid: coupon.isValid,
            remainingUses: coupon.usageLimit ? coupon.usageLimit - coupon.usedCount : null
          }
        },
        message: '优惠券验证成功'
      });
    }

    // 如果没有订单金额，只返回基本信息
    res.json({
      success: true,
      data: {
        coupon: {
          _id: coupon._id,
          code: coupon.code,
          name: coupon.name,
          description: coupon.description,
          discountType: coupon.discountType,
          discountValue: coupon.discountValue,
          minPurchaseAmount: coupon.minPurchaseAmount,
          maxDiscountAmount: coupon.maxDiscountAmount,
          startDate: coupon.startDate,
          endDate: coupon.endDate,
          usageLimit: coupon.usageLimit,
          usedCount: coupon.usedCount,
          isActive: coupon.isActive,
          applicableCategories: coupon.applicableCategories,
          applicableProducts: coupon.applicableProducts,
          isValid: coupon.isValid,
          remainingUses: coupon.usageLimit ? coupon.usageLimit - coupon.usedCount : null
        }
      },
      message: '优惠券验证成功'
    });
  });

  /**
   * 创建优惠券（管理员）
   */
  static createCoupon = asyncHandler(async (req: Request, res: Response) => {
    const {
      code,
      name,
      description,
      discountType,
      discountValue,
      minPurchaseAmount,
      maxDiscountAmount,
      startDate,
      endDate,
      usageLimit,
      applicableCategories,
      applicableProducts
    } = req.body;

    // 检查优惠券代码是否已存在
    const existingCoupon = await CouponModel.findOne({ code });
    if (existingCoupon) {
      return res.status(400).json({
        success: false,
        message: '优惠券代码已存在'
      });
    }

    // 验证日期
    const start = new Date(startDate);
    const end = new Date(endDate);
    if (start >= end) {
      return res.status(400).json({
        success: false,
        message: '结束日期必须晚于开始日期'
      });
    }

    // 验证折扣值
    if (discountType === 'percentage' && (discountValue <= 0 || discountValue > 100)) {
      return res.status(400).json({
        success: false,
        message: '百分比折扣必须在0-100之间'
      });
    }

    if (discountType === 'fixed' && discountValue <= 0) {
      return res.status(400).json({
        success: false,
        message: '固定折扣必须大于0'
      });
    }

    const coupon = new CouponModel({
      code: code.toUpperCase(),
      name,
      description,
      discountType,
      discountValue,
      minPurchaseAmount,
      maxDiscountAmount,
      startDate: start,
      endDate: end,
      usageLimit,
      applicableCategories,
      applicableProducts,
      isActive: true,
      usedCount: 0
    });

    await coupon.save();

    res.status(201).json({
      success: true,
      data: {
        coupon: {
          _id: coupon._id,
          code: coupon.code,
          name: coupon.name,
          description: coupon.description,
          discountType: coupon.discountType,
          discountValue: coupon.discountValue,
          minPurchaseAmount: coupon.minPurchaseAmount,
          maxDiscountAmount: coupon.maxDiscountAmount,
          startDate: coupon.startDate,
          endDate: coupon.endDate,
          usageLimit: coupon.usageLimit,
          usedCount: coupon.usedCount,
          isActive: coupon.isActive,
          applicableCategories: coupon.applicableCategories,
          applicableProducts: coupon.applicableProducts,
          isValid: coupon.isValid,
          createdAt: coupon.createdAt,
          updatedAt: coupon.updatedAt
        }
      },
      message: '优惠券创建成功'
    });
  });
}

export default CouponController;