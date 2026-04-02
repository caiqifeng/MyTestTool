import mongoose from 'mongoose';
import { ProductSpec } from '@shared/types';

export interface ICartItem {
  productId: string;
  name: string;
  price: number;
  quantity: number;
  image?: string;
  specs?: ProductSpec[];
  addedAt: Date;
}

export interface ICart extends mongoose.Document {
  userId: string;
  items: ICartItem[];
  updatedAt: Date;
}

export interface ICartModel extends mongoose.Model<ICart> {
  // Static methods
  getUserCart(userId: string): Promise<ICart | null>;
  addItem(userId: string, item: Omit<ICartItem, 'addedAt'>): Promise<ICart>;
  updateItemQuantity(userId: string, productId: string, quantity: number): Promise<ICart | null>;
  removeItem(userId: string, productId: string): Promise<ICart | null>;
  clearCart(userId: string): Promise<ICart | null>;
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

const cartItemSchema = new mongoose.Schema({
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
    min: 1,
    default: 1
  },
  image: {
    type: String,
    trim: true
  },
  specs: [productSpecSchema],
  addedAt: {
    type: Date,
    default: Date.now
  }
}, { _id: false });

const cartSchema = new mongoose.Schema<ICart, ICartModel>(
  {
    userId: {
      type: String,
      required: true,
      unique: true,
      index: true
    },
    items: [cartItemSchema]
  },
  {
    timestamps: true
  }
);

// Indexes
cartSchema.index({ userId: 1 });
cartSchema.index({ 'items.productId': 1 });
cartSchema.index({ updatedAt: -1 });

// Static methods
cartSchema.statics.getUserCart = async function(userId: string): Promise<ICart | null> {
  return this.findOne({ userId });
};

cartSchema.statics.addItem = async function(userId: string, item: Omit<ICartItem, 'addedAt'>): Promise<ICart> {
  const cart = await this.findOne({ userId });

  if (!cart) {
    // 创建新购物车
    const newCart = new this({
      userId,
      items: [{
        ...item,
        addedAt: new Date()
      }]
    });
    return await newCart.save();
  }

  // 检查商品是否已在购物车中
  const existingItemIndex = cart.items.findIndex(i => i.productId === item.productId);

  if (existingItemIndex >= 0) {
    // 更新现有商品数量
    cart.items[existingItemIndex].quantity += item.quantity;
    cart.items[existingItemIndex].addedAt = new Date();
  } else {
    // 添加新商品
    cart.items.push({
      ...item,
      addedAt: new Date()
    });
  }

  cart.markModified('items');
  return await cart.save();
};

cartSchema.statics.updateItemQuantity = async function(
  userId: string,
  productId: string,
  quantity: number
): Promise<ICart | null> {
  if (quantity < 1) {
    // 如果数量小于1，删除该商品
    return this.removeItem(userId, productId);
  }

  const cart = await this.findOne({ userId });

  if (!cart) {
    return null;
  }

  const itemIndex = cart.items.findIndex(i => i.productId === productId);

  if (itemIndex >= 0) {
    cart.items[itemIndex].quantity = quantity;
    cart.items[itemIndex].addedAt = new Date();
    cart.markModified('items');
    return await cart.save();
  }

  return cart;
};

cartSchema.statics.removeItem = async function(userId: string, productId: string): Promise<ICart | null> {
  const cart = await this.findOne({ userId });

  if (!cart) {
    return null;
  }

  cart.items = cart.items.filter(i => i.productId !== productId);
  cart.markModified('items');
  return await cart.save();
};

cartSchema.statics.clearCart = async function(userId: string): Promise<ICart | null> {
  const cart = await this.findOne({ userId });

  if (!cart) {
    return null;
  }

  cart.items = [];
  cart.markModified('items');
  return await cart.save();
};

const Cart = mongoose.model<ICart, ICartModel>('Cart', cartSchema);

export default Cart;