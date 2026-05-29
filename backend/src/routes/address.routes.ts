import { Router } from 'express';
import { body, param } from 'express-validator';
import AddressController from '../controllers/address.controller';
import { authMiddleware } from '../middleware/auth';
import { validate, commonValidators } from '../middleware/validation';

const router = Router();

/**
 * @route POST /api/addresses
 * @desc 添加地址
 * @access Private
 */
router.post(
  '/',
  authMiddleware,
  [
    body('contactName').notEmpty().trim().isLength({ min: 1, max: 20 }).withMessage('联系人姓名不能为空且长度不超过20字'),
    body('contactPhone').matches(/^1[3-9]\d{9}$/).withMessage('请输入有效的手机号码'),
    body('province').notEmpty().trim().withMessage('省份不能为空'),
    body('city').notEmpty().trim().withMessage('城市不能为空'),
    body('district').notEmpty().trim().withMessage('区县不能为空'),
    body('detail').notEmpty().trim().isLength({ max: 200 }).withMessage('详细地址不能为空且长度不超过200字'),
    body('isDefault').optional().isBoolean()
  ],
  validate,
  AddressController.createAddress
);

/**
 * @route GET /api/addresses
 * @desc 获取地址列表
 * @access Private
 */
router.get(
  '/',
  authMiddleware,
  AddressController.getAddresses
);

/**
 * @route GET /api/addresses/:id
 * @desc 获取地址详情
 * @access Private
 */
router.get(
  '/:id',
  authMiddleware,
  [
    param('id').custom(commonValidators.objectId('id').custom.options)
  ],
  validate,
  AddressController.getAddressById
);

/**
 * @route PUT /api/addresses/:id
 * @desc 更新地址
 * @access Private
 */
router.put(
  '/:id',
  authMiddleware,
  [
    param('id').custom(commonValidators.objectId('id').custom.options),
    body('contactName').optional().trim().isLength({ min: 1, max: 20 }),
    body('contactPhone').optional().matches(/^1[3-9]\d{9}$/),
    body('province').optional().trim(),
    body('city').optional().trim(),
    body('district').optional().trim(),
    body('detail').optional().trim().isLength({ max: 200 }),
    body('isDefault').optional().isBoolean()
  ],
  validate,
  AddressController.updateAddress
);

/**
 * @route DELETE /api/addresses/:id
 * @desc 删除地址
 * @access Private
 */
router.delete(
  '/:id',
  authMiddleware,
  [
    param('id').custom(commonValidators.objectId('id').custom.options)
  ],
  validate,
  AddressController.deleteAddress
);

/**
 * @route PUT /api/addresses/:id/default
 * @desc 设置默认地址
 * @access Private
 */
router.put(
  '/:id/default',
  authMiddleware,
  [
    param('id').custom(commonValidators.objectId('id').custom.options)
  ],
  validate,
  AddressController.setDefaultAddress
);

/**
 * @route GET /api/addresses/default
 * @desc 获取默认地址
 * @access Private
 */
router.get(
  '/default',
  authMiddleware,
  AddressController.getDefaultAddress
);

export default router;