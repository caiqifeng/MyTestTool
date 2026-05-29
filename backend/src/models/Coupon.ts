import mongoose from 'mongoose';

export interface ICoupon extends mongoose.Document {
  code: string;
  name: string;
  description?: string;
  discountType: 'percentage' | 'fixed';
  discountValue: number;
  minPurchaseAmount?: number;
  maxDiscountAmount?: number;
  startDate: Date;
  endDate: Date;
  usageLimit?: number;
  usedCount: number;
  isActive: boolean;
  applicableCategories?: string[];
  applicableProducts?: string[];
  createdAt: Date;
  updatedAt: Date;

  // Virtual properties
  isValid: boolean;

  // Instance methods
  canApplyToOrder(orderAmount: number, productIds?: string[], categoryIds?: string[]): boolean;
  calculateDiscount(orderAmount: number): number;
}

export interface ICouponModel extends mongoose.Model<ICoupon> {}

const couponSchema = new mongoose.Schema<ICoupon, ICouponModel>(
  {
    code: {
      type: String,
      required: true,
      unique: true,
      index: true,
      trim: true,
      uppercase: true
    },
    name: {
      type: String,
      required: true,
      trim: true,
      maxlength: 50
    },
    description: {
      type: String,
      trim: true,
      maxlength: 200
    },
    discountType: {
      type: String,
      enum: ['percentage', 'fixed'],
      required: true,
      index: true
    },
    discountValue: {
      type: Number,
      required: true,
      min: 0
    },
    minPurchaseAmount: {
      type: Number,
      min: 0
    },
    maxDiscountAmount: {
      type: Number,
      min: 0
    },
    startDate: {
      type: Date,
      required: true,
      index: true
    },
    endDate: {
      type: Date,
      required: true,
      index: true
    },
    usageLimit: {
      type: Number,
      min: 1
    },
    usedCount: {
      type: Number,
      default: 0,
      min: 0
    },
    isActive: {
      type: Boolean,
      default: true,
      index: true
    },
    applicableCategories: [{
      type: String,
      index: true
    }],
    applicableProducts: [{
      type: String,
      index: true
    }]
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
  }
);

// Indexes
couponSchema.index({ createdAt: -1 });
couponSchema.index({ updatedAt: -1 });
couponSchema.index({ startDate: 1, endDate: 1 });
couponSchema.index({ isActive: 1, startDate: 1, endDate: 1 });

// Virtual for checking if coupon is valid
couponSchema.virtual('isValid').get(function() {
  const now = new Date();
  return this.isActive &&
    now >= this.startDate &&
    now <= this.endDate &&
    (!this.usageLimit || this.usedCount < this.usageLimit);
});

// Method to check if coupon can be applied to an order
couponSchema.methods.canApplyToOrder = function(orderAmount: number, productIds?: string[], categoryIds?: string[]): boolean {
  // Check validity
  if (!this.isValid) {
    return false;
  }

  // Check minimum purchase amount
  if (this.minPurchaseAmount && orderAmount < this.minPurchaseAmount) {
    return false;
  }

  // Check applicable categories
  if (this.applicableCategories && this.applicableCategories.length > 0 && categoryIds) {
    const hasApplicableCategory = categoryIds.some(categoryId =>
      this.applicableCategories!.includes(categoryId)
    );
    if (!hasApplicableCategory) {
      return false;
    }
  }

  // Check applicable products
  if (this.applicableProducts && this.applicableProducts.length > 0 && productIds) {
    const hasApplicableProduct = productIds.some(productId =>
      this.applicableProducts!.includes(productId)
    );
    if (!hasApplicableProduct) {
      return false;
    }
  }

  return true;
};

// Method to calculate discount amount
couponSchema.methods.calculateDiscount = function(orderAmount: number): number {
  let discount = 0;

  if (this.discountType === 'percentage') {
    discount = orderAmount * (this.discountValue / 100);
    if (this.maxDiscountAmount && discount > this.maxDiscountAmount) {
      discount = this.maxDiscountAmount;
    }
  } else {
    discount = this.discountValue;
  }

  // Discount cannot exceed order amount
  return Math.min(discount, orderAmount);
};

const Coupon = mongoose.model<ICoupon, ICouponModel>('Coupon', couponSchema);

export default Coupon;