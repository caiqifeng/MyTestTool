import { Router } from 'express';
import { body, param, query } from 'express-validator';
import CouponController from '../controllers/coupon.controller';
import { authMiddleware } from '../middleware/auth';
import { requireAdmin } from '../middleware/rbac';
import { validate, commonValidators } from '../middleware/validation';

const router = Router();

/**
 * @route GET /api/coupons/available
 * @desc 获取可用优惠券列表
 * @access Private
 */
router.get(
  '/available',
  authMiddleware,
  [
    query('orderAmount').optional().isFloat({ min: 0 }),
    query('productIds').optional().isString(),
    query('categoryIds').optional().isString()
  ],
  validate,
  CouponController.getAvailableCoupons
);

/**
 * @route GET /api/coupons/my
 * @desc 获取用户优惠券
 * @access Private
 */
router.get(
  '/my',
  authMiddleware,
  CouponController.getUserCoupons
);

/**
 * @route POST /api/coupons/:code/claim
 * @desc 领取优惠券
 * @access Private
 */
router.post(
  '/:code/claim',
  authMiddleware,
  [
    param('code').notEmpty().trim().withMessage('优惠券代码不能为空')
  ],
  validate,
  CouponController.claimCoupon
);

/**
 * @route POST /api/coupons/validate
 * @desc 验证优惠券
 * @access Private
 */
router.post(
  '/validate',
  authMiddleware,
  [
    body('code').notEmpty().trim().withMessage('优惠券代码不能为空'),
    body('orderAmount').optional().isFloat({ min: 0 }),
    body('productIds').optional().isString(),
    body('categoryIds').optional().isString()
  ],
  validate,
  CouponController.validateCoupon
);

/**
 * @route POST /api/coupons
 * @desc 创建优惠券（管理员）
 * @access Private (Admin only)
 */
router.post(
  '/',
  authMiddleware,
  requireAdmin,
  [
    body('code').notEmpty().trim().withMessage('优惠券代码不能为空'),
    body('name').notEmpty().trim().isLength({ max: 50 }).withMessage('优惠券名称不能为空且长度不超过50字'),
    body('description').optional().trim().isLength({ max: 200 }),
    body('discountType').isIn(['percentage', 'fixed']).withMessage('折扣类型无效'),
    body('discountValue').isFloat({ min: 0 }).withMessage('折扣值必须大于等于0'),
    body('minPurchaseAmount').optional().isFloat({ min: 0 }),
    body('maxDiscountAmount').optional().isFloat({ min: 0 }),
    body('startDate').isISO8601().withMessage('开始日期格式无效'),
    body('endDate').isISO8601().withMessage('结束日期格式无效'),
    body('usageLimit').optional().isInt({ min: 1 }),
    body('applicableCategories').optional().isArray(),
    body('applicableProducts').optional().isArray()
  ],
  validate,
  CouponController.createCoupon
);

export default router;