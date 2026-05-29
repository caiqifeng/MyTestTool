import { Router } from 'express';
import { body, param } from 'express-validator';
import CartController from '../controllers/cart.controller';
import { authMiddleware } from '../middleware/auth';
import { validate, commonValidators } from '../middleware/validation';

const router = Router();

/**
 * @route POST /api/cart/items
 * @desc 添加商品到购物车
 * @access Private
 */
router.post(
  '/items',
  authMiddleware,
  [
    body('productId').notEmpty().withMessage('商品ID不能为空'),
    body('quantity').isInt({ min: 1 }).withMessage('商品数量必须大于0'),
    body('specs').optional().isArray()
  ],
  validate,
  CartController.addToCart
);

/**
 * @route GET /api/cart
 * @desc 获取购物车
 * @access Private
 */
router.get(
  '/',
  authMiddleware,
  CartController.getCart
);

/**
 * @route PUT /api/cart/items/:productId
 * @desc 更新购物车商品数量
 * @access Private
 */
router.put(
  '/items/:productId',
  authMiddleware,
  [
    param('productId').notEmpty().withMessage('商品ID不能为空'),
    body('quantity').isFloat({ min: 0 }).withMessage('数量必须是非负数')
  ],
  validate,
  CartController.updateCartItem
);

/**
 * @route DELETE /api/cart/items/:productId
 * @desc 删除购物车商品
 * @access Private
 */
router.delete(
  '/items/:productId',
  authMiddleware,
  [
    param('productId').notEmpty().withMessage('商品ID不能为空')
  ],
  validate,
  CartController.removeCartItem
);

/**
 * @route DELETE /api/cart
 * @desc 清空购物车
 * @access Private
 */
router.delete(
  '/',
  authMiddleware,
  CartController.clearCart
);

/**
 * @route GET /api/cart/count
 * @desc 获取购物车商品数量
 * @access Private
 */
router.get(
  '/count',
  authMiddleware,
  CartController.getCartCount
);

export default router;