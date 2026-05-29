import { Request, Response } from 'express';
import { ReviewModel } from '../models/Review';
import { OrderModel } from '../models/Order';
import { OrderStatus } from '../../../shared/dist/types';

class ReviewController {
  // 创建评价
  async createReview(req: Request, res: Response) {
    try {
      const { orderId, productId, rating, content, images, isAnonymous } = req.body;
      const userId = req.user?.userId;

      if (!userId) {
        return res.status(401).json({
          success: false,
          message: '请先登录',
        });
      }

      // 验证订单是否存在且属于当前用户
      const order = await OrderModel.findOne({
        _id: orderId,
        userId,
      });

      if (!order) {
        return res.status(404).json({
          success: false,
          message: '订单不存在',
        });
      }

      // 验证订单是否已完成
      if (order.orderStatus !== OrderStatus.COMPLETED) {
        return res.status(400).json({
          success: false,
          message: '只能评价已完成的订单',
        });
      }

      // 验证商品是否在订单中
      const orderItem = order.items.find(
        (item) => item.productId.toString() === productId
      );

      if (!orderItem) {
        return res.status(400).json({
          success: false,
          message: '该商品不在订单中',
        });
      }

      // 检查是否已评价
      const existingReview = await ReviewModel.findOne({
        orderId,
        productId,
      });

      if (existingReview) {
        return res.status(400).json({
          success: false,
          message: '该商品已评价',
        });
      }

      // 创建评价
      const review = await ReviewModel.create({
        orderId,
        userId,
        productId,
        rating,
        content,
        images: images || [],
        isAnonymous: isAnonymous || false,
      });

      res.status(201).json({
        success: true,
        message: '评价成功',
        data: review,
      });
    } catch (error: any) {
      console.error('创建评价失败:', error);
      res.status(500).json({
        success: false,
        message: '创建评价失败',
        error: error.message,
      });
    }
  }

  // 获取商品评价列表
  async getProductReviews(req: Request, res: Response) {
    try {
      const { productId } = req.params;
      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 10;

      const result = await ReviewModel.getProductReviews(productId, page, limit);

      res.json({
        success: true,
        data: result,
      });
    } catch (error: any) {
      console.error('获取商品评价失败:', error);
      res.status(500).json({
        success: false,
        message: '获取商品评价失败',
        error: error.message,
      });
    }
  }

  // 获取用户评价列表
  async getUserReviews(req: Request, res: Response) {
    try {
      const userId = req.user?.userId;

      if (!userId) {
        return res.status(401).json({
          success: false,
          message: '请先登录',
        });
      }

      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 10;

      const result = await ReviewModel.getUserReviews(userId, page, limit);

      res.json({
        success: true,
        data: result,
      });
    } catch (error: any) {
      console.error('获取用户评价失败:', error);
      res.status(500).json({
        success: false,
        message: '获取用户评价失败',
        error: error.message,
      });
    }
  }

  // 商家回复评价
  async replyReview(req: Request, res: Response) {
    try {
      const { reviewId } = req.params;
      const { content } = req.body;

      const review = await ReviewModel.findById(reviewId);

      if (!review) {
        return res.status(404).json({
          success: false,
          message: '评价不存在',
        });
      }

      if (review.reply) {
        return res.status(400).json({
          success: false,
          message: '已回复过该评价',
        });
      }

      review.reply = {
        content,
        createdAt: new Date(),
      };

      await review.save();

      res.json({
        success: true,
        message: '回复成功',
        data: review,
      });
    } catch (error: any) {
      console.error('回复评价失败:', error);
      res.status(500).json({
        success: false,
        message: '回复评价失败',
        error: error.message,
      });
    }
  }

  // 删除评价（管理员）
  async deleteReview(req: Request, res: Response) {
    try {
      const { reviewId } = req.params;

      const review = await ReviewModel.findByIdAndDelete(reviewId);

      if (!review) {
        return res.status(404).json({
          success: false,
          message: '评价不存在',
        });
      }

      res.json({
        success: true,
        message: '删除成功',
      });
    } catch (error: any) {
      console.error('删除评价失败:', error);
      res.status(500).json({
        success: false,
        message: '删除评价失败',
        error: error.message,
      });
    }
  }
}

export default new ReviewController();

