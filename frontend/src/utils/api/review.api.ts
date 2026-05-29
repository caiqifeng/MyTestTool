import request from './index';

export interface CreateReviewData {
  orderId: string;
  productId: string;
  rating: number;
  content: string;
  images?: string[];
  isAnonymous?: boolean;
}

export interface ReplyReviewData {
  content: string;
}

// 创建评价
export const createReview = (data: CreateReviewData) => {
  return request({
    url: '/reviews',
    method: 'POST',
    data,
  });
};

// 获取商品评价列表
export const getProductReviews = (productId: string, page: number = 1, limit: number = 10) => {
  return request({
    url: `/reviews/product/${productId}`,
    method: 'GET',
    params: { page, limit },
  });
};

// 获取用户评价列表
export const getUserReviews = (page: number = 1, limit: number = 10) => {
  return request({
    url: '/reviews/user',
    method: 'GET',
    params: { page, limit },
  });
};

// 商家回复评价
export const replyReview = (reviewId: string, data: ReplyReviewData) => {
  return request({
    url: `/reviews/${reviewId}/reply`,
    method: 'POST',
    data,
  });
};

// 删除评价
export const deleteReview = (reviewId: string) => {
  return request({
    url: `/reviews/${reviewId}`,
    method: 'DELETE',
  });
};
