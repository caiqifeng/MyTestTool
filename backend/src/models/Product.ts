import mongoose from 'mongoose';
import { ProductStatus, ProductSpec } from '../../../shared/dist/types';

export interface IProduct extends mongoose.Document {
  name: string;
  description?: string;
  price: number;
  originalPrice?: number;
  categoryId: string;
  images: string[];
  stock: number;
  salesCount: number;
  status: ProductStatus;
  specs?: ProductSpec[];
  sortOrder: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface IProductModel extends mongoose.Model<IProduct> {
  // Static methods
  decreaseStock(productId: string, quantity: number): Promise<IProduct | null>;
  search(keyword: string, categoryId?: string, page?: number, limit?: number): Promise<{
    products: IProduct[];
    total: number;
    page: number;
    totalPages: number;
  }>;
}

const productSpecSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  value: {
    type: String,
    required: true,
    trim: true
  }
}, { _id: false });

const productSchema = new mongoose.Schema<IProduct, IProductModel>(
  {
    name: {
      type: String,
      required: true,
      trim: true,
      maxlength: 100,
      index: true
    },
    description: {
      type: String,
      trim: true,
      maxlength: 1000
    },
    price: {
      type: Number,
      required: true,
      min: 0
    },
    originalPrice: {
      type: Number,
      min: 0
    },
    categoryId: {
      type: String,
      required: true,
      index: true
    },
    images: [{
      type: String,
      required: true,
      trim: true
    }],
    stock: {
      type: Number,
      required: true,
      default: 0,
      min: 0
    },
    salesCount: {
      type: Number,
      default: 0,
      min: 0
    },
    status: {
      type: String,
      enum: Object.values(ProductStatus),
      default: ProductStatus.ACTIVE,
      index: true
    },
    specs: [productSpecSchema],
    sortOrder: {
      type: Number,
      default: 0,
      index: true
    }
  },
  {
    timestamps: true
  }
);

// Indexes
productSchema.index({ createdAt: -1 });
productSchema.index({ updatedAt: -1 });
productSchema.index({ price: 1 });
productSchema.index({ stock: 1 });
productSchema.index({ name: 'text', description: 'text' });

// Static methods
productSchema.statics.decreaseStock = async function(productId: string, quantity: number): Promise<IProduct | null> {
  // Validate quantity is a positive integer
  if (!Number.isInteger(quantity)) {
    throw new Error('Quantity must be an integer');
  }

  if (quantity <= 0) {
    throw new Error('Quantity must be greater than 0');
  }

  const product = await this.findById(productId);
  if (!product) {
    return null;
  }

  if (product.stock < quantity) {
    throw new Error(`Insufficient stock. Available: ${product.stock}, Requested: ${quantity}`);
  }

  product.stock -= quantity;
  product.salesCount += quantity;

  // Update status if stock becomes 0
  if (product.stock === 0) {
    product.status = ProductStatus.OUT_OF_STOCK;
  }

  return await product.save();
};

productSchema.statics.search = async function(
  keyword: string,
  categoryId?: string,
  page: number = 1,
  limit: number = 10
): Promise<{
  products: IProduct[];
  total: number;
  page: number;
  totalPages: number;
}> {
  const skip = (page - 1) * limit;

  const query: any = {};

  // Add text search
  if (keyword) {
    query.$text = { $search: keyword };
  }

  // Add category filter
  if (categoryId) {
    query.categoryId = categoryId;
  }

  // Only show active products
  query.status = ProductStatus.ACTIVE;

  const [products, total] = await Promise.all([
    this.find(query)
      .sort({ sortOrder: 1, createdAt: -1 })
      .skip(skip)
      .limit(limit),
    this.countDocuments(query)
  ]);

  return {
    products,
    total,
    page,
    totalPages: Math.ceil(total / limit)
  };
};

const Product = mongoose.model<IProduct, IProductModel>('Product', productSchema);

export default Product;