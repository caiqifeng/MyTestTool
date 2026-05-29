export enum UserRole {
  CUSTOMER = 'customer',
  ADMIN = 'admin',
  STAFF = 'staff'
}

export enum OrderStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  PROCESSING = 'processing',
  READY_FOR_PICKUP = 'ready_for_pickup',
  OUT_FOR_DELIVERY = 'out_for_delivery',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  REFUNDED = 'refunded'
}

export enum ProductStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  OUT_OF_STOCK = 'out_of_stock',
  COMING_SOON = 'coming_soon'
}

export enum DeliveryType {
  DELIVERY = 'delivery',
  PICKUP = 'pickup'
}

export enum PaymentMethod {
  WECHAT_PAY = 'wechat_pay',
  ALIPAY = 'alipay',
  CASH = 'cash',
  CARD = 'card'
}

export enum PaymentStatus {
  PENDING = 'pending',
  PAID = 'paid',
  FAILED = 'failed',
  REFUNDED = 'refunded'
}

export interface User {
  _id?: string;
  openid: string;
  nickname: string;
  avatar?: string;
  phone?: string;
  email?: string;
  role: UserRole;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface ProductSpec {
  name: string;
  value: string;
}

export interface Product {
  _id?: string;
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
  createdAt?: Date;
  updatedAt?: Date;
}

export interface Category {
  _id?: string;
  name: string;
  description?: string;
  icon?: string;
  sortOrder: number;
  parentId?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface OrderItem {
  productId: string;
  name: string;
  price: number;
  quantity: number;
  image?: string;
  specs?: ProductSpec[];
}

export interface Address {
  _id?: string;
  userId: string;
  contactName: string;
  contactPhone: string;
  province: string;
  city: string;
  district: string;
  detail: string;
  isDefault: boolean;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface Order {
  _id?: string;
  orderNumber: string;
  userId: string;
  items: OrderItem[];
  totalAmount: number;
  deliveryFee: number;
  discountAmount: number;
  finalAmount: number;
  deliveryType: DeliveryType;
  deliveryAddress?: Address;
  pickupTime?: Date;
  paymentMethod: PaymentMethod;
  paymentStatus: PaymentStatus;
  orderStatus: OrderStatus;
  remark?: string;
  couponId?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface Coupon {
  _id?: string;
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
  createdAt?: Date;
  updatedAt?: Date;
}

export interface Banner {
  _id?: string;
  title: string;
  description?: string;
  image: string;
  linkType: 'product' | 'category' | 'url';
  linkTarget?: string;
  sortOrder: number;
  isActive: boolean;
  startDate?: Date;
  endDate?: Date;
  createdAt?: Date;
  updatedAt?: Date;
}