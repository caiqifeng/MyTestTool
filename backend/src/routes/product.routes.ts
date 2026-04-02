import { Router } from 'express';
import { body, param, query } from 'express-validator';
import ProductController from '../controllers/product.controller';
import { authMiddleware, optionalAuthMiddleware } from '../middleware/auth';
import { requireAdmin } from '../middleware/rbac';
import { validate, commonValidators } from '../middleware/validation';
import { ProductStatus } from '../../../shared/src/types';

const router = Router();

/**
 * @route GET /api/products
 * @desc 获取商品列表
 * @access Public
 */
router.get(
  '/',
  [
    query('page').optional().isInt({ min: 1 }),
    query('limit').optional().isInt({ min: 1, max: 100 }),
    query('categoryId').optional().isString().trim(),
    query('status').optional().isIn(['active', 'inactive', 'out_of_stock', 'coming_soon']),
    query('keyword').optional().isString().trim(),
    query('sortBy').optional().isIn(['price', 'sales', 'createdAt', 'sortOrder']),
    query('sortOrder').optional().isIn(['asc', 'desc'])
  ],
  validate,
  ProductController.getProducts
);

/**
 * @route GET /api/products/:id
 * @desc 获取商品详情
 * @access Public
 */
router.get(
  '/:id',
  [
    param('id').custom(commonValidators.objectId('id').custom.options)
  ],
  validate,
  ProductController.getProductById
);

/**
 * @route POST /api/products
 * @desc 创建商品（管理员）
 * @access Private (Admin only)
 */
router.post(
  '/',
  authMiddleware,
  requireAdmin,
  [
    body('name').notEmpty().trim().isLength({ max: 100 }).withMessage('商品名称不能为空且长度不超过100字'),
    body('description').optional().trim().isLength({ max: 1000 }),
    body('price').isFloat({ min: 0 }).withMessage('价格必须大于等于0'),
    body('originalPrice').optional().isFloat({ min: 0 }),
    body('categoryId').notEmpty().withMessage('分类不能为空'),
    body('images').optional().isArray(),
    body('stock').optional().isInt({ min: 0 }),
    body('specs').optional().isArray(),
    body('sortOrder').optional().isInt(),
    body('status').optional().isIn(Object.values(ProductStatus))
  ],
  validate,
  ProductController.createProduct
);

/**
 * @route PUT /api/products/:id
 * @desc 更新商品（管理员）
 * @access Private (Admin only)
 */
router.put(
  '/:id',
  authMiddleware,
  requireAdmin,
  [
    param('id').custom(commonValidators.objectId('id').custom.options),
    body('name').optional().trim().isLength({ max: 100 }),
    body('description').optional().trim().isLength({ max: 1000 }),
    body('price').optional().isFloat({ min: 0 }),
    body('originalPrice').optional().isFloat({ min: 0 }),
    body('categoryId').optional().isString(),
    body('images').optional().isArray(),
    body('stock').optional().isInt({ min: 0 }),
    body('specs').optional().isArray(),
    body('sortOrder').optional().isInt(),
    body('status').optional().isIn(Object.values(ProductStatus))
  ],
  validate,
  ProductController.updateProduct
);

/**
 * @route DELETE /api/products/:id
 * @desc 删除商品（管理员）
 * @access Private (Admin only)
 */
router.delete(
  '/:id',
  authMiddleware,
  requireAdmin,
  [
    param('id').custom(commonValidators.objectId('id').custom.options)
  ],
  validate,
  ProductController.deleteProduct
);

/**
 * @route PUT /api/products/:id/stock
 * @desc 更新商品库存（管理员）
 * @access Private (Admin only)
 */
router.put(
  '/:id/stock',
  authMiddleware,
  requireAdmin,
  [
    param('id').custom(commonValidators.objectId('id').custom.options),
    body('stock').isInt({ min: 0 }).withMessage('库存必须是非负数')
  ],
  validate,
  ProductController.updateStock
);

/**
 * @route GET /api/products/popular
 * @desc 获取热门商品
 * @access Public
 */
router.get(
  '/popular',
  [
    query('limit').optional().isInt({ min: 1, max: 50 })
  ],
  validate,
  ProductController.getPopularProducts
);

/**
 * @route GET /api/products/category/:categoryId
 * @desc 获取分类下的商品
 * @access Public
 */
router.get(
  '/category/:categoryId',
  [
    param('categoryId').custom(commonValidators.objectId('categoryId').custom.options),
    query('page').optional().isInt({ min: 1 }),
    query('limit').optional().isInt({ min: 1, max: 100 })
  ],
  validate,
  ProductController.getProductsByCategory
);

export default router;