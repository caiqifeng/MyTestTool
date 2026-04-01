import { Router } from 'express';
import { body, param, query } from 'express-validator';
import AuthController from '../controllers/auth.controller';
import { authMiddleware, optionalAuthMiddleware } from '../middleware/auth';
import { requireAdmin } from '../middleware/rbac';
import { validate, commonValidators } from '../middleware/validation';

const router = Router();

/**
 * @route POST /api/auth/wechat-login
 * @desc 微信小程序登录
 * @access Public
 */
router.post(
  '/wechat-login',
  [
    body('code').notEmpty().withMessage('微信code不能为空'),
    body('nickname').optional().isString().trim(),
    body('avatar').optional().isURL().withMessage('头像必须是有效的URL')
  ],
  validate,
  AuthController.wechatLogin
);

/**
 * @route POST /api/auth/refresh-token
 * @desc 刷新访问令牌
 * @access Public
 */
router.post(
  '/refresh-token',
  [
    body('refreshToken').notEmpty().withMessage('刷新令牌不能为空')
  ],
  validate,
  AuthController.refreshToken
);

/**
 * @route GET /api/auth/me
 * @desc 获取当前用户信息
 * @access Private
 */
router.get(
  '/me',
  authMiddleware,
  AuthController.getCurrentUser
);

/**
 * @route PUT /api/auth/profile
 * @desc 更新用户信息
 * @access Private
 */
router.put(
  '/profile',
  authMiddleware,
  [
    body('nickname').optional().isString().trim().isLength({ min: 1, max: 50 }),
    body('phone').optional().matches(/^1[3-9]\d{9}$/).withMessage('手机号格式不正确'),
    body('email').optional().isEmail().withMessage('邮箱格式不正确')
  ],
  validate,
  AuthController.updateProfile
);

/**
 * @route GET /api/auth/users
 * @desc 管理员获取用户列表
 * @access Private (Admin only)
 */
router.get(
  '/users',
  authMiddleware,
  requireAdmin,
  [
    query('page').optional().isInt({ min: 1 }),
    query('limit').optional().isInt({ min: 1, max: 100 }),
    query('role').optional().isIn(['customer', 'admin', 'staff']),
    query('search').optional().isString().trim()
  ],
  validate,
  AuthController.getUsers
);

/**
 * @route PUT /api/auth/users/:userId/role
 * @desc 管理员更新用户角色
 * @access Private (Admin only)
 */
router.put(
  '/users/:userId/role',
  authMiddleware,
  requireAdmin,
  [
    param('userId').custom(commonValidators.objectId('userId').custom.options),
    body('role').isIn(['customer', 'admin', 'staff']).withMessage('角色无效')
  ],
  validate,
  AuthController.updateUserRole
);

export default router;