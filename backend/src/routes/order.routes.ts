import { Router } from 'express';
import { body, param, query } from 'express-validator';
import OrderController from '../controllers/order.controller';
import { authMiddleware } from '../middleware/auth';
import { requireAdmin } from '../middleware/rbac';
import { validate, commonValidators } from '../middleware/validation';
import { DeliveryType, PaymentMethod, OrderStatus, PaymentStatus } from '../../../shared/src/types';

const router = Router();

/**
 * @route POST /api/orders
 * @desc 创建订单
 * @access Private
 */
router.post(
  '/',
  authMiddleware,
  [
    body('items').isArray({ min: 1 }).withMessage('购物车不能为空'),
    body('items.*.productId').notEmpty().withMessage('商品ID不能为空'),
    body('items.*.quantity').isInt({ min: 1 }).withMessage('商品数量必须大于0'),
    body('items.*.price').isFloat({ min: 0 }).withMessage('商品价格必须大于等于0'),
    body('deliveryType').isIn(Object.values(DeliveryType)).withMessage('无效的配送方式'),
    body('deliveryAddressId')
      .if(body('deliveryType').equals(DeliveryType.DELIVERY))
      .notEmpty()
      .withMessage('配送地址不能为空'),
    body('pickupTime')
      .if(body('deliveryType').equals(DeliveryType.PICKUP))
      .notEmpty()
      .isISO8601()
      .withMessage('提货时间必须为有效日期'),
    body('paymentMethod').isIn(Object.values(PaymentMethod)).withMessage('无效的支付方式'),
    body('remark').optional().isString().trim().isLength({ max: 500 }),
    body('couponCode').optional().isString().trim()
  ],
  validate,
  OrderController.createOrder
);

/**
 * @route GET /api/orders
 * @desc 获取订单列表
 * @access Private
 */
router.get(
  '/',
  authMiddleware,
  [
    query('page').optional().isInt({ min: 1 }),
    query('limit').optional().isInt({ min: 1, max: 100 }),
    query('status').optional().isIn(Object.values(OrderStatus)),
    query('startDate').optional().isISO8601(),
    query('endDate').optional().isISO8601()
  ],
  validate,
  OrderController.getOrders
);

/**
 * @route GET /api/orders/:id
 * @desc 获取订单详情
 * @access Private
 */
router.get(
  '/:id',
  authMiddleware,
  [
    param('id').custom(commonValidators.objectId('id').custom.options)
  ],
  validate,
  OrderController.getOrderById
);

/**
 * @route DELETE /api/orders/:id/cancel
 * @desc 取消订单
 * @access Private
 */
router.delete(
  '/:id/cancel',
  authMiddleware,
  [
    param('id').custom(commonValidators.objectId('id').custom.options)
  ],
  validate,
  OrderController.cancelOrder
);

/**
 * @route PUT /api/orders/:id/status
 * @desc 更新订单状态（管理员）
 * @access Private (Admin only)
 */
router.put(
  '/:id/status',
  authMiddleware,
  requireAdmin,
  [
    param('id').custom(commonValidators.objectId('id').custom.options),
    body('status').isIn(Object.values(OrderStatus)).withMessage('无效的订单状态')
  ],
  validate,
  OrderController.updateOrderStatus
);

/**
 * @route PUT /api/orders/:id/payment-status
 * @desc 更新支付状态（管理员）
 * @access Private (Admin only)
 */
router.put(
  '/:id/payment-status',
  authMiddleware,
  requireAdmin,
  [
    param('id').custom(commonValidators.objectId('id').custom.options),
    body('paymentStatus').isIn(Object.values(PaymentStatus)).withMessage('无效的支付状态')
  ],
  validate,
  OrderController.updatePaymentStatus
);

/**
 * @route GET /api/orders/stats/overview
 * @desc 获取订单统计（管理员）
 * @access Private (Admin only)
 */
router.get(
  '/stats/overview',
  authMiddleware,
  requireAdmin,
  [
    query('startDate').optional().isISO8601(),
    query('endDate').optional().isISO8601()
  ],
  validate,
  OrderController.getOrderStats
);

export default router;