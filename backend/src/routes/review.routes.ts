import { Router } from 'express';
import ReviewController from '../controllers/review.controller';
import { authMiddleware } from '../middleware/auth';
import { requireAdmin } from '../middleware/rbac';

const router = Router();

// 创建评价（需要登录）
router.post('/', authMiddleware, ReviewController.createReview);

// 获取商品评价列表（公开）
router.get('/product/:productId', ReviewController.getProductReviews);

// 获取用户评价列表（需要登录）
router.get('/user', authMiddleware, ReviewController.getUserReviews);

// 商家回复评价（需要管理员权限）
router.post('/:reviewId/reply', authMiddleware, requireAdmin, ReviewController.replyReview);

// 删除评价（需要管理员权限）
router.delete('/:reviewId', authMiddleware, requireAdmin, ReviewController.deleteReview);

export default router;
