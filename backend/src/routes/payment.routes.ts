import { Router } from 'express';
import { body, param } from 'express-validator';
import PaymentController from '../controllers/payment.controller';
import { authMiddleware } from '../middleware/auth';
import { validate, commonValidators } from '../middleware/validation';

const router = Router();

/**
 * @route POST /api/payments/create
 * @desc 创建支付订单（微信支付）
 * @access Private
 */
router.post(
  '/create',
  authMiddleware,
  [
    body('orderId').notEmpty().withMessage('订单ID不能为空'),
    body('orderId').custom(commonValidators.objectId('orderId').custom.options)
  ],
  validate,
  PaymentController.createPayment
);

/**
 * @route POST /api/payments/callback
 * @desc 处理微信支付回调（不需要认证）
 * @access Public
 */
router.post(
  '/callback',
  [
    body('orderId').notEmpty().withMessage('订单ID不能为空'),
    body('transactionId').optional().isString(),
    body('paymentStatus').isIn(['SUCCESS', 'FAILED']).withMessage('无效的支付状态')
  ],
  validate,
  PaymentController.handlePaymentCallback
);

/**
 * @route GET /api/payments/status/:orderId
 * @desc 查询支付状态
 * @access Private
 */
router.get(
  '/status/:orderId',
  authMiddleware,
  [
    param('orderId').custom(commonValidators.objectId('orderId').custom.options)
  ],
  validate,
  PaymentController.getPaymentStatus
);

/**
 * @route POST /api/payments/refund
 * @desc 申请退款
 * @access Private
 */
router.post(
  '/refund',
  authMiddleware,
  [
    body('orderId').notEmpty().withMessage('订单ID不能为空'),
    body('orderId').custom(commonValidators.objectId('orderId').custom.options),
    body('refundAmount').isFloat({ min: 0.01 }).withMessage('退款金额必须大于0'),
    body('refundReason').optional().isString().trim().isLength({ max: 200 })
  ],
  validate,
  PaymentController.requestRefund
);

export default router;