import mongoose from 'mongoose';
import { OrderStatus, DeliveryType, PaymentMethod, PaymentStatus, OrderItem, ProductSpec } from '@shared/types';

export interface IOrder extends mongoose.Document {
  orderNumber: string;
  userId: string;
  items: OrderItem[];
  totalAmount: number;
  deliveryFee: number;
  discountAmount: number;
  finalAmount: number;
  deliveryType: DeliveryType;
  deliveryAddress?: {
    contactName: string;
    contactPhone: string;
    province: string;
    city: string;
    district: string;
    detail: string;
  };
  pickupTime?: Date;
  paymentMethod: PaymentMethod;
  paymentStatus: PaymentStatus;
  orderStatus: OrderStatus;
  remark?: string;
  couponId?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface IOrderModel extends mongoose.Model<IOrder> {
  // Static methods
  getStatusStats(startDate?: Date, endDate?: Date): Promise<{
    [key in OrderStatus]: number;
  }>;
  getUserOrders(userId: string, page?: number, limit?: number): Promise<{
    orders: IOrder[];
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

const orderItemSchema = new mongoose.Schema({
  productId: {
    type: String,
    required: true,
    index: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  price: {
    type: Number,
    required: true,
    min: 0
  },
  quantity: {
    type: Number,
    required: true,
    min: 1
  },
  image: {
    type: String,
    trim: true
  },
  specs: [productSpecSchema]
}, { _id: false });

const deliveryAddressSchema = new mongoose.Schema({
  contactName: {
    type: String,
    required: true,
    trim: true
  },
  contactPhone: {
    type: String,
    required: true,
    trim: true
  },
  province: {
    type: String,
    required: true,
    trim: true
  },
  city: {
    type: String,
    required: true,
    trim: true
  },
  district: {
    type: String,
    required: true,
    trim: true
  },
  detail: {
    type: String,
    required: true,
    trim: true
  }
}, { _id: false });

const orderSchema = new mongoose.Schema<IOrder, IOrderModel>(
  {
    orderNumber: {
      type: String,
      required: true,
      unique: true,
      index: true,
      trim: true
    },
    userId: {
      type: String,
      required: true,
      index: true
    },
    items: [orderItemSchema],
    totalAmount: {
      type: Number,
      required: true,
      min: 0
    },
    deliveryFee: {
      type: Number,
      required: true,
      default: 0,
      min: 0
    },
    discountAmount: {
      type: Number,
      required: true,
      default: 0,
      min: 0
    },
    finalAmount: {
      type: Number,
      required: true,
      min: 0
    },
    deliveryType: {
      type: String,
      enum: Object.values(DeliveryType),
      required: true,
      index: true
    },
    deliveryAddress: deliveryAddressSchema,
    pickupTime: {
      type: Date
    },
    paymentMethod: {
      type: String,
      enum: Object.values(PaymentMethod),
      required: true,
      index: true
    },
    paymentStatus: {
      type: String,
      enum: Object.values(PaymentStatus),
      default: PaymentStatus.PENDING,
      index: true
    },
    orderStatus: {
      type: String,
      enum: Object.values(OrderStatus),
      default: OrderStatus.PENDING,
      index: true
    },
    remark: {
      type: String,
      trim: true,
      maxlength: 500
    },
    couponId: {
      type: String,
      index: true
    }
  },
  {
    timestamps: true
  }
);

// Indexes
orderSchema.index({ createdAt: -1 });
orderSchema.index({ updatedAt: -1 });
orderSchema.index({ finalAmount: 1 });
orderSchema.index({ userId: 1, createdAt: -1 });

// Pre-save hook to generate order number
orderSchema.pre('save', async function(next) {
  if (this.isNew) {
    const date = new Date();
    const year = date.getFullYear().toString().slice(-2);
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');

    // Get count of orders today for sequence number
    const startOfDay = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const OrderModel = this.constructor as mongoose.Model<IOrder>;
    const count = await OrderModel.countDocuments({
      createdAt: { $gte: startOfDay }
    });

    const sequence = (count + 1).toString().padStart(4, '0');
    this.orderNumber = `${year}${month}${day}${sequence}`;
  }
  next();
});

// Static methods
orderSchema.statics.getStatusStats = async function(startDate?: Date, endDate?: Date): Promise<{
  [key in OrderStatus]: number;
}> {
  const query: any = {};

  if (startDate || endDate) {
    query.createdAt = {};
    if (startDate) query.createdAt.$gte = startDate;
    if (endDate) query.createdAt.$lte = endDate;
  }

  const stats = await this.aggregate([
    { $match: query },
    { $group: { _id: '$orderStatus', count: { $sum: 1 } } }
  ]);

  // Initialize result with all statuses set to 0
  const result = {} as { [key in OrderStatus]: number };
  Object.values(OrderStatus).forEach(status => {
    result[status] = 0;
  });

  // Fill in actual counts
  stats.forEach(stat => {
    result[stat._id as OrderStatus] = stat.count;
  });

  return result;
};

orderSchema.statics.getUserOrders = async function(
  userId: string,
  page: number = 1,
  limit: number = 10
): Promise<{
  orders: IOrder[];
  total: number;
  page: number;
  totalPages: number;
}> {
  const skip = (page - 1) * limit;

  const [orders, total] = await Promise.all([
    this.find({ userId })
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit),
    this.countDocuments({ userId })
  ]);

  return {
    orders,
    total,
    page,
    totalPages: Math.ceil(total / limit)
  };
};

const Order = mongoose.model<IOrder, IOrderModel>('Order', orderSchema);

export default Order;