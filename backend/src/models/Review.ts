import mongoose from 'mongoose';

export interface IReview extends mongoose.Document {
  orderId: mongoose.Types.ObjectId;
  userId: mongoose.Types.ObjectId;
  productId: mongoose.Types.ObjectId;
  rating: number;
  content: string;
  images?: string[];
  reply?: {
    content: string;
    createdAt: Date;
  };
  isAnonymous: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface IReviewModel extends mongoose.Model<IReview> {
  getProductReviews(
    productId: string,
    page?: number,
    limit?: number
  ): Promise<{
    reviews: IReview[];
    total: number;
    averageRating: number;
  }>;
  getUserReviews(
    userId: string,
    page?: number,
    limit?: number
  ): Promise<{
    reviews: IReview[];
    total: number;
  }>;
}

const reviewSchema = new mongoose.Schema(
  {
    orderId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Order',
      required: true,
      index: true,
    },
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
      index: true,
    },
    productId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Product',
      required: true,
      index: true,
    },
    rating: {
      type: Number,
      required: true,
      min: 1,
      max: 5,
    },
    content: {
      type: String,
      required: true,
      trim: true,
      minlength: 5,
      maxlength: 500,
    },
    images: [
      {
        type: String,
      },
    ],
    reply: {
      content: {
        type: String,
        trim: true,
      },
      createdAt: {
        type: Date,
      },
    },
    isAnonymous: {
      type: Boolean,
      default: false,
    },
  },
  {
    timestamps: true,
  }
);

// 索引
reviewSchema.index({ productId: 1, createdAt: -1 });
reviewSchema.index({ userId: 1, createdAt: -1 });
reviewSchema.index({ orderId: 1, productId: 1 }, { unique: true });

// 静态方法：获取商品评价
reviewSchema.statics.getProductReviews = async function (
  productId: string,
  page: number = 1,
  limit: number = 10
) {
  const skip = (page - 1) * limit;

  const [reviews, total, ratingStats] = await Promise.all([
    this.find({ productId })
      .populate('userId', 'nickname avatar')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit)
      .lean(),
    this.countDocuments({ productId }),
    this.aggregate([
      { $match: { productId: new mongoose.Types.ObjectId(productId) } },
      { $group: { _id: null, averageRating: { $avg: '$rating' } } },
    ]),
  ]);

  return {
    reviews,
    total,
    averageRating: ratingStats[0]?.averageRating || 0,
  };
};

// 静态方法：获取用户评价
reviewSchema.statics.getUserReviews = async function (
  userId: string,
  page: number = 1,
  limit: number = 10
) {
  const skip = (page - 1) * limit;

  const [reviews, total] = await Promise.all([
    this.find({ userId })
      .populate('productId', 'name images price')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit)
      .lean(),
    this.countDocuments({ userId }),
  ]);

  return {
    reviews,
    total,
  };
};

export const ReviewModel = mongoose.model<IReview, IReviewModel>(
  'Review',
  reviewSchema
);

