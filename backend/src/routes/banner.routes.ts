import { Router } from 'express';
import { body, param, query } from 'express-validator';
import BannerController from '../controllers/banner.controller';
import { authMiddleware } from '../middleware/auth';
import { requireAdmin } from '../middleware/rbac';
import { validate, commonValidators } from '../middleware/validation';

const router = Router();

/**
 * @route GET /api/banners
 * @desc 获取轮播图列表
 * @access Public (部分功能需要管理员权限)
 */
router.get(
  '/',
  // [
  //   query('activeOnly').optional().isIn(['true', 'false']),
  //   query('limit').optional().isInt({ min: 1, max: 50 })
  // ],
  // validate,
  BannerController.getBanners
);

/**
 * @route GET /api/banners/:id
 * @desc 获取轮播图详情
 * @access Private (Admin only)
 */
router.get(
  '/:id',
  authMiddleware,
  requireAdmin,
  [
    param('id').custom(commonValidators.objectId('id').custom.options)
  ],
  validate,
  BannerController.getBannerById
);

/**
 * @route POST /api/banners
 * @desc 创建轮播图
 * @access Private (Admin only)
 */
router.post(
  '/',
  authMiddleware,
  requireAdmin,
  [
    body('title').notEmpty().trim().isLength({ max: 50 }).withMessage('标题不能为空且长度不超过50字'),
    body('description').optional().trim().isLength({ max: 200 }),
    body('image').notEmpty().trim().withMessage('图片不能为空'),
    body('linkType').isIn(['product', 'category', 'url']).withMessage('链接类型无效'),
    body('linkTarget')
      .if(body('linkType').not().equals('url'))
      .notEmpty()
      .withMessage('链接目标不能为空'),
    body('sortOrder').optional().isInt(),
    body('isActive').optional().isBoolean(),
    body('startDate').optional().isISO8601(),
    body('endDate').optional().isISO8601()
  ],
  validate,
  BannerController.createBanner
);

/**
 * @route PUT /api/banners/:id
 * @desc 更新轮播图
 * @access Private (Admin only)
 */
router.put(
  '/:id',
  authMiddleware,
  requireAdmin,
  [
    param('id').custom(commonValidators.objectId('id').custom.options),
    body('title').optional().trim().isLength({ max: 50 }),
    body('description').optional().trim().isLength({ max: 200 }),
    body('image').optional().trim(),
    body('linkType').optional().isIn(['product', 'category', 'url']),
    body('linkTarget')
      .if(body('linkType').exists().not().equals('url'))
      .notEmpty()
      .withMessage('链接目标不能为空'),
    body('sortOrder').optional().isInt(),
    body('isActive').optional().isBoolean(),
    body('startDate').optional().isISO8601(),
    body('endDate').optional().isISO8601()
  ],
  validate,
  BannerController.updateBanner
);

/**
 * @route DELETE /api/banners/:id
 * @desc 删除轮播图
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
  BannerController.deleteBanner
);

/**
 * @route PUT /api/banners/order
 * @desc 更新轮播图排序
 * @access Private (Admin only)
 */
router.put(
  '/order',
  authMiddleware,
  requireAdmin,
  [
    body('orders').isArray({ min: 1 }).withMessage('排序数据不能为空'),
    body('orders.*.id').notEmpty().withMessage('轮播图ID不能为空'),
    body('orders.*.sortOrder').isInt().withMessage('排序值必须是整数')
  ],
  validate,
  BannerController.updateBannerOrder
);

/**
 * @route PUT /api/banners/batch-status
 * @desc 批量更新轮播图状态
 * @access Private (Admin only)
 */
router.put(
  '/batch-status',
  authMiddleware,
  requireAdmin,
  [
    body('ids').isArray({ min: 1 }).withMessage('轮播图ID列表不能为空'),
    body('ids.*').notEmpty().withMessage('轮播图ID不能为空'),
    body('isActive').isBoolean().withMessage('状态必须是布尔值')
  ],
  validate,
  BannerController.batchUpdateBannerStatus
);

export default router;