import { Router } from 'express';
import { body, param } from 'express-validator';
import CategoryController from '../controllers/category.controller';
import { authMiddleware } from '../middleware/auth';
import { requireAdmin } from '../middleware/rbac';
import { validate, commonValidators } from '../middleware/validation';

const router = Router();

/**
 * @route POST /api/categories
 * @desc 创建分类
 * @access Private (Admin)
 */
router.post(
  '/',
  authMiddleware,
  requireAdmin,
  [
    body('name').notEmpty().trim().isLength({ min: 1, max: 50 }).withMessage('分类名称不能为空且长度不超过50字'),
    body('description').optional().trim().isLength({ max: 200 }).withMessage('描述长度不超过200字'),
    body('icon').optional().trim(),
    body('sortOrder').optional().isInt({ min: 0 }),
    body('parentId').optional().trim()
  ],
  validate,
  CategoryController.createCategory
);

/**
 * @route GET /api/categories
 * @desc 获取分类列表
 * @access Public
 */
router.get(
  '/',
  CategoryController.getCategories
);

/**
 * @route GET /api/categories/tree
 * @desc 获取分类树
 * @access Public
 */
router.get(
  '/tree',
  CategoryController.getCategoryTree
);

/**
 * @route GET /api/categories/:id
 * @desc 获取分类详情
 * @access Public
 */
router.get(
  '/:id',
  [
    param('id').custom(commonValidators.objectId('id').custom.options)
  ],
  validate,
  CategoryController.getCategoryById
);

/**
 * @route PUT /api/categories/:id
 * @desc 更新分类
 * @access Private (Admin)
 */
router.put(
  '/:id',
  authMiddleware,
  requireAdmin,
  [
    param('id').custom(commonValidators.objectId('id').custom.options),
    body('name').optional().trim().isLength({ min: 1, max: 50 }),
    body('description').optional().trim().isLength({ max: 200 }),
    body('icon').optional().trim(),
    body('sortOrder').optional().isInt({ min: 0 }),
    body('parentId').optional().trim()
  ],
  validate,
  CategoryController.updateCategory
);

/**
 * @route DELETE /api/categories/:id
 * @desc 删除分类
 * @access Private (Admin)
 */
router.delete(
  '/:id',
  authMiddleware,
  requireAdmin,
  [
    param('id').custom(commonValidators.objectId('id').custom.options)
  ],
  validate,
  CategoryController.deleteCategory
);

export default router;