# 面包店小程序全栈系统实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现一个完整的面包店小程序全栈系统，包含用户端小程序、后台管理、RBAC权限控制、微信支付集成、实时库存管理等完整功能。

**Architecture:** 模块化单体应用架构，前端使用uni-app（Vue 3 + TypeScript）编译到微信小程序，后端使用Node.js/Express + MongoDB，基于JWT和角色声明的RBAC权限控制，管理功能集成在同一小程序中通过条件渲染实现。

**Tech Stack:** uni-app (Vue 3 + TypeScript), Node.js + Express + TypeScript, MongoDB + Mongoose, JWT认证, 微信小程序登录, 微信支付API, Socket.IO (可选实时通知)

---

## 项目文件结构

```
break-mini-app/
├── backend/                    # Node.js/Express后端
│   ├── src/
│   │   ├── config/           # 配置文件
│   │   ├── models/           # MongoDB模型
│   │   ├── routes/           # API路由
│   │   ├── controllers/      # 控制器层
│   │   ├── services/         # 业务逻辑层
│   │   ├── middleware/       # 中间件（认证、RBAC、日志等）
│   │   ├── utils/            # 工具函数
│   │   └── app.ts           # Express应用主文件
│   ├── tests/               # 后端测试
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.example
│
├── frontend/                  # uni-app小程序
│   ├── pages/               # 页面目录
│   │   ├── index/          # 首页
│   │   ├── product-detail/ # 商品详情页
│   │   ├── cart/           # 购物车页
│   │   ├── order-confirm/  # 订单确认页
│   │   ├── order-list/     # 我的订单页
│   │   ├── user-center/    # 用户中心页
│   │   ├── address/        # 地址管理页
│   │   ├── login/          # 登录页
│   │   └── admin/          # 管理页面（条件显示）
│   ├── components/         # 公共组件
│   ├── store/             # Pinia状态管理
│   ├── api/               # API请求封装
│   ├── utils/             # 工具函数
│   ├── static/            # 静态资源
│   ├── uni.scss           # 全局样式
│   ├── manifest.json      # 应用配置
│   ├── pages.json        # 页面配置
│   └── App.vue           # 应用入口
│
├── shared/                 # 共享代码
│   ├── types/             # TypeScript类型定义
│   └── constants/         # 常量定义
│
├── docker/                # Docker配置
├── docs/                  # 文档
└── package.json          # 根项目配置（workspace）
```

---

## 任务分解

### Task 1: 初始化项目结构和配置

**Files:**
- Create: `break-mini-app/package.json`
- Create: `break-mini-app/backend/package.json`
- Create: `break-mini-app/backend/tsconfig.json`
- Create: `break-mini-app/backend/.env.example`
- Create: `break-mini-app/frontend/package.json`
- Create: `break-mini-app/shared/package.json`

- [ ] **Step 1: 创建根目录和workspace配置**

```json
// break-mini-app/package.json
{
  "name": "break-mini-app",
  "version": "1.0.0",
  "private": true,
  "workspaces": [
    "backend",
    "frontend",
    "shared"
  ],
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "dev:backend": "cd backend && npm run dev",
    "dev:frontend": "cd frontend && npm run dev",
    "build": "npm run build:backend && npm run build:frontend",
    "build:backend": "cd backend && npm run build",
    "build:frontend": "cd frontend && npm run build",
    "test": "npm run test:backend && npm run test:frontend",
    "test:backend": "cd backend && npm test",
    "test:frontend": "cd frontend && npm test"
  },
  "devDependencies": {
    "concurrently": "^8.2.0"
  }
}
```

- [ ] **Step 2: 创建后端基础配置**

```json
// break-mini-app/backend/package.json
{
  "name": "break-mini-app-backend",
  "version": "1.0.0",
  "description": "面包店小程序后端API",
  "main": "dist/app.js",
  "scripts": {
    "dev": "tsx watch src/app.ts",
    "build": "tsc",
    "start": "node dist/app.js",
    "test": "jest",
    "test:watch": "jest --watch"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "dotenv": "^16.0.3",
    "mongoose": "^7.0.0",
    "jsonwebtoken": "^9.0.0",
    "bcryptjs": "^2.4.3",
    "helmet": "^7.0.0",
    "express-rate-limit": "^6.10.0",
    "express-validator": "^7.0.1",
    "winston": "^3.10.0",
    "socket.io": "^4.5.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.17",
    "@types/cors": "^2.8.13",
    "@types/jsonwebtoken": "^9.0.2",
    "@types/bcryptjs": "^2.4.2",
    "typescript": "^5.1.6",
    "tsx": "^3.12.0",
    "jest": "^29.5.0",
    "@types/jest": "^29.5.2",
    "ts-jest": "^29.1.0",
    "supertest": "^6.3.3"
  }
}
```

```json
// break-mini-app/backend/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node",
    "types": ["node", "jest"]
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

```bash
# break-mini-app/backend/.env.example
NODE_ENV=development
PORT=3000
MONGODB_URI=mongodb://localhost:27017/break_mini_app
JWT_SECRET=your_jwt_secret_key_here
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret
WECHAT_MCH_ID=your_wechat_merchant_id
WECHAT_API_KEY=your_wechat_api_key
REDIS_URL=redis://localhost:6379
```

- [ ] **Step 3: 创建前端uni-app基础配置**

```json
// break-mini-app/frontend/package.json
{
  "name": "break-mini-app-frontend",
  "version": "1.0.0",
  "description": "面包店小程序前端",
  "main": "main.js",
  "scripts": {
    "dev": "npm run dev:mp-weixin",
    "dev:mp-weixin": "uni -p mp-weixin",
    "build": "npm run build:mp-weixin",
    "build:mp-weixin": "uni build -p mp-weixin",
    "test": "jest",
    "lint": "eslint . --ext .vue,.js,.ts"
  },
  "dependencies": {
    "@dcloudio/uni-app": "^3.0.0",
    "pinia": "^2.1.0",
    "axios": "^1.3.4",
    "dayjs": "^1.11.7",
    "vant": "^4.0.0"
  },
  "devDependencies": {
    "@dcloudio/types": "^3.0.0",
    "@dcloudio/uni-cli-shared": "^3.0.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.1.6",
    "sass": "^1.62.0",
    "@vant/weapp": "^1.10.0",
    "@uni-helper/uni-ui-types": "^1.0.0",
    "jest": "^29.5.0",
    "@vue/test-utils": "^2.4.0",
    "eslint": "^8.40.0",
    "eslint-plugin-vue": "^9.15.0"
  }
}
```

- [ ] **Step 4: 创建共享类型包配置**

```json
// break-mini-app/shared/package.json
{
  "name": "break-mini-app-shared",
  "version": "1.0.0",
  "description": "共享类型和常量定义",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "prepublishOnly": "npm run build"
  },
  "devDependencies": {
    "typescript": "^5.1.6"
  }
}
```

```json
// break-mini-app/shared/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "declaration": true,
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

- [ ] **Step 5: 安装依赖并验证**

```bash
cd break-mini-app
npm install

cd backend
npm install

cd ../frontend
npm install

cd ../shared
npm install
```

运行：`cd break-mini-app && npm install`
预期：成功安装所有依赖

- [ ] **Step 6: 提交初始化代码**

```bash
git add break-mini-app/
git commit -m "feat: initialize project structure with backend, frontend, and shared packages"
```

### Task 2: 后端数据模型定义

**Files:**
- Create: `break-mini-app/shared/src/types/index.ts`
- Create: `break-mini-app/shared/src/constants/index.ts`
- Create: `break-mini-app/backend/src/models/User.ts`
- Create: `break-mini-app/backend/src/models/Product.ts`
- Create: `break-mini-app/backend/src/models/Category.ts`
- Create: `break-mini-app/backend/src/models/Order.ts`
- Create: `break-mini-app/backend/src/models/Address.ts`
- Create: `break-mini-app/backend/src/models/Coupon.ts`
- Create: `break-mini-app/backend/src/models/Banner.ts`
- Create: `break-mini-app/backend/tests/models/user.test.ts`

- [ ] **Step 1: 创建共享类型定义**

```typescript
// break-mini-app/shared/src/types/index.ts
export enum UserRole {
  CUSTOMER = 'customer',
  ADMIN = 'admin',
  STAFF = 'staff'
}

export enum OrderStatus {
  PENDING_PAYMENT = 'pending_payment',
  PAID = 'paid',
  PREPARING = 'preparing',
  READY_FOR_PICKUP = 'ready_for_pickup',
  OUT_FOR_DELIVERY = 'out_for_delivery',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  REFUNDED = 'refunded'
}

export enum ProductStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  OUT_OF_STOCK = 'out_of_stock'
}

export enum DeliveryType {
  PICKUP = 'pickup',
  DELIVERY = 'delivery'
}

export enum PaymentMethod {
  WECHAT = 'wechat',
  ALIPAY = 'alipay',
  CASH = 'cash'
}

export interface User {
  _id: string;
  openid: string;
  nickname: string;
  avatar: string;
  phone?: string;
  email?: string;
  role: UserRole;
  createdAt: Date;
  updatedAt: Date;
}

export interface Product {
  _id: string;
  name: string;
  description: string;
  price: number;
  originalPrice?: number;
  categoryId: string;
  images: string[];
  stock: number;
  salesCount: number;
  status: ProductStatus;
  specs?: Array<{
    name: string;
    value: string;
  }>;
  sortOrder: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Category {
  _id: string;
  name: string;
  description?: string;
  icon?: string;
  sortOrder: number;
  parentId?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface OrderItem {
  productId: string;
  name: string;
  price: number;
  quantity: number;
  image?: string;
}

export interface Order {
  _id: string;
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
  paymentStatus: 'pending' | 'paid' | 'refunded' | 'failed';
  orderStatus: OrderStatus;
  remark?: string;
  couponId?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Address {
  _id: string;
  userId: string;
  recipient: string;
  phone: string;
  province: string;
  city: string;
  district: string;
  detail: string;
  isDefault: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Coupon {
  _id: string;
  code: string;
  name: string;
  description: string;
  type: 'percentage' | 'fixed';
  value: number;
  minPurchaseAmount?: number;
  validFrom: Date;
  validTo: Date;
  usageLimit?: number;
  usedCount: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Banner {
  _id: string;
  title: string;
  image: string;
  linkType: 'product' | 'category' | 'url';
  linkTarget: string;
  sortOrder: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}
```

- [ ] **Step 2: 创建共享常量定义**

```typescript
// break-mini-app/shared/src/constants/index.ts
export const DEFAULT_PAGE_SIZE = 10;
export const MAX_PAGE_SIZE = 100;

export const PRODUCT_CATEGORIES = [
  { id: 'bread', name: '面包', icon: '🍞' },
  { id: 'cake', name: '蛋糕', icon: '🎂' },
  { id: 'dessert', name: '甜点', icon: '🍰' },
  { id: 'drink', name: '饮品', icon: '🥤' },
  { id: 'sandwich', name: '三明治', icon: '🥪' }
] as const;

export const DELIVERY_FEE = 5; // 配送费5元
export const FREE_DELIVERY_THRESHOLD = 50; // 满50免配送费

export const ORDER_STATUS_MAP = {
  pending_payment: { label: '待支付', color: '#ff9900' },
  paid: { label: '已支付', color: '#1677ff' },
  preparing: { label: '制作中', color: '#722ed1' },
  ready_for_pickup: { label: '待自提', color: '#13c2c2' },
  out_for_delivery: { label: '配送中', color: '#52c41a' },
  completed: { label: '已完成', color: '#52c41a' },
  cancelled: { label: '已取消', color: '#f5222d' },
  refunded: { label: '已退款', color: '#f5222d' }
} as const;

export const PAYMENT_METHODS = [
  { value: 'wechat', label: '微信支付', icon: 'wechat-pay' },
  { value: 'alipay', label: '支付宝', icon: 'alipay' },
  { value: 'cash', label: '货到付款', icon: 'cash' }
] as const;
```

- [ ] **Step 3: 创建User模型测试**

```typescript
// break-mini-app/backend/tests/models/user.test.ts
import mongoose from 'mongoose';
import { UserModel } from '../../src/models/User';
import { UserRole } from '../../../shared/src/types';

describe('User Model', () => {
  beforeAll(async () => {
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/test');
  });

  afterAll(async () => {
    await mongoose.connection.close();
  });

  beforeEach(async () => {
    await UserModel.deleteMany({});
  });

  test('should create a user with required fields', async () => {
    const userData = {
      openid: 'test_openid_123',
      nickname: '测试用户',
      avatar: 'https://example.com/avatar.jpg',
      role: UserRole.CUSTOMER
    };

    const user = new UserModel(userData);
    const savedUser = await user.save();

    expect(savedUser._id).toBeDefined();
    expect(savedUser.openid).toBe(userData.openid);
    expect(savedUser.nickname).toBe(userData.nickname);
    expect(savedUser.avatar).toBe(userData.avatar);
    expect(savedUser.role).toBe(userData.role);
    expect(savedUser.createdAt).toBeDefined();
    expect(savedUser.updatedAt).toBeDefined();
  });

  test('should require openid field', async () => {
    const userData = {
      nickname: '测试用户',
      avatar: 'https://example.com/avatar.jpg',
      role: UserRole.CUSTOMER
    };

    const user = new UserModel(userData);
    await expect(user.save()).rejects.toThrow();
  });

  test('should default role to customer', async () => {
    const userData = {
      openid: 'test_openid_456',
      nickname: '测试用户2',
      avatar: 'https://example.com/avatar2.jpg'
    };

    const user = new UserModel(userData);
    const savedUser = await user.save();

    expect(savedUser.role).toBe(UserRole.CUSTOMER);
  });

  test('should validate phone format', async () => {
    const userData = {
      openid: 'test_openid_789',
      nickname: '测试用户3',
      avatar: 'https://example.com/avatar3.jpg',
      phone: 'invalid-phone'
    };

    const user = new UserModel(userData);
    await expect(user.save()).rejects.toThrow();
  });

  test('should validate email format', async () => {
    const userData = {
      openid: 'test_openid_999',
      nickname: '测试用户4',
      avatar: 'https://example.com/avatar4.jpg',
      email: 'invalid-email'
    };

    const user = new UserModel(userData);
    await expect(user.save()).rejects.toThrow();
  });
});
```

运行：`cd break-mini-app/backend && npm test -- tests/models/user.test.ts`
预期：FAIL with "Cannot find module '../../src/models/User'"

- [ ] **Step 4: 实现User模型**

```typescript
// break-mini-app/backend/src/models/User.ts
import mongoose from 'mongoose';
import { UserRole } from '../../../shared/src/types';

const userSchema = new mongoose.Schema({
  openid: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  nickname: {
    type: String,
    required: true,
    trim: true
  },
  avatar: {
    type: String,
    required: true
  },
  phone: {
    type: String,
    trim: true,
    match: /^1[3-9]\d{9}$/
  },
  email: {
    type: String,
    trim: true,
    lowercase: true,
    match: /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/
  },
  role: {
    type: String,
    enum: Object.values(UserRole),
    default: UserRole.CUSTOMER
  }
}, {
  timestamps: true
});

// 创建唯一索引确保openid唯一
userSchema.index({ openid: 1 }, { unique: true });

// 静态方法：通过openid查找用户
userSchema.statics.findByOpenid = function(openid: string) {
  return this.findOne({ openid });
};

// 静态方法：创建或更新用户
userSchema.statics.createOrUpdate = async function(userData: {
  openid: string;
  nickname: string;
  avatar: string;
  phone?: string;
  email?: string;
}) {
  return this.findOneAndUpdate(
    { openid: userData.openid },
    {
      $set: {
        nickname: userData.nickname,
        avatar: userData.avatar,
        ...(userData.phone && { phone: userData.phone }),
        ...(userData.email && { email: userData.email })
      }
    },
    { upsert: true, new: true, setDefaultsOnInsert: true }
  );
};

// 实例方法：检查用户角色
userSchema.methods.hasRole = function(role: UserRole | UserRole[]): boolean {
  if (Array.isArray(role)) {
    return role.includes(this.role as UserRole);
  }
  return this.role === role;
};

// 实例方法：是否是管理员
userSchema.methods.isAdmin = function(): boolean {
  return this.hasRole([UserRole.ADMIN, UserRole.STAFF]);
};

export const UserModel = mongoose.model('User', userSchema);
export type UserDocument = mongoose.Document & typeof userSchema;
```

运行：`cd break-mini-app/backend && npm test -- tests/models/user.test.ts`
预期：PASS (所有测试通过)

- [ ] **Step 5: 实现Product模型**

```typescript
// break-mini-app/backend/src/models/Product.ts
import mongoose from 'mongoose';
import { ProductStatus } from '../../../shared/src/types';

const productSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true,
    index: true
  },
  description: {
    type: String,
    required: true,
    trim: true
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
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Category',
    required: true,
    index: true
  },
  images: [{
    type: String,
    required: true
  }],
  stock: {
    type: Number,
    required: true,
    min: 0,
    default: 0
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
  specs: [{
    name: { type: String, required: true },
    value: { type: String, required: true }
  }],
  sortOrder: {
    type: Number,
    default: 0
  }
}, {
  timestamps: true
});

// 复合索引：按分类和排序顺序查询
productSchema.index({ categoryId: 1, sortOrder: -1 });

// 复合索引：按状态和销量查询
productSchema.index({ status: 1, salesCount: -1 });

// 文本搜索索引
productSchema.index({ name: 'text', description: 'text' });

// 静态方法：减少库存
productSchema.statics.decreaseStock = async function(productId: string, quantity: number) {
  const result = await this.findByIdAndUpdate(
    productId,
    {
      $inc: { stock: -quantity, salesCount: quantity },
      $set: {
        status: this.stock - quantity <= 0 ? ProductStatus.OUT_OF_STOCK : ProductStatus.ACTIVE
      }
    },
    { new: true }
  );

  if (!result) {
    throw new Error('Product not found');
  }

  if (result.stock < 0) {
    throw new Error('Insufficient stock');
  }

  return result;
};

// 静态方法：搜索商品
productSchema.statics.search = function(keyword: string, options: {
  categoryId?: string;
  status?: ProductStatus;
  page?: number;
  limit?: number;
}) {
  const { categoryId, status, page = 1, limit = 10 } = options;
  const skip = (page - 1) * limit;

  const query: any = {};

  if (keyword) {
    query.$text = { $search: keyword };
  }

  if (categoryId) {
    query.categoryId = categoryId;
  }

  if (status) {
    query.status = status;
  }

  return this.find(query)
    .sort({ sortOrder: -1, createdAt: -1 })
    .skip(skip)
    .limit(limit)
    .populate('categoryId', 'name icon');
};

export const ProductModel = mongoose.model('Product', productSchema);
export type ProductDocument = mongoose.Document & typeof productSchema;
```

- [ ] **Step 6: 实现Category模型**

```typescript
// break-mini-app/backend/src/models/Category.ts
import mongoose from 'mongoose';

const categorySchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true,
    unique: true
  },
  description: {
    type: String,
    trim: true
  },
  icon: {
    type: String
  },
  sortOrder: {
    type: Number,
    default: 0
  },
  parentId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Category',
    default: null
  }
}, {
  timestamps: true
});

// 索引：按排序顺序查询
categorySchema.index({ sortOrder: -1, createdAt: -1 });

// 索引：查询子分类
categorySchema.index({ parentId: 1 });

// 静态方法：获取所有分类（树形结构）
categorySchema.statics.getCategoryTree = async function() {
  const categories = await this.find().sort({ sortOrder: -1 });

  const categoryMap = new Map();
  const rootCategories: any[] = [];

  // 第一遍：建立映射
  categories.forEach(category => {
    categoryMap.set(category._id.toString(), {
      ...category.toObject(),
      children: []
    });
  });

  // 第二遍：建立树形结构
  categories.forEach(category => {
    const categoryObj = categoryMap.get(category._id.toString());

    if (category.parentId) {
      const parent = categoryMap.get(category.parentId.toString());
      if (parent) {
        parent.children.push(categoryObj);
      }
    } else {
      rootCategories.push(categoryObj);
    }
  });

  return rootCategories;
};

export const CategoryModel = mongoose.model('Category', categorySchema);
export type CategoryDocument = mongoose.Document & typeof categorySchema;
```

- [ ] **Step 7: 实现Order模型**

```typescript
// break-mini-app/backend/src/models/Order.ts
import mongoose from 'mongoose';
import { OrderStatus, DeliveryType, PaymentMethod } from '../../../shared/src/types';

const orderItemSchema = new mongoose.Schema({
  productId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Product',
    required: true
  },
  name: {
    type: String,
    required: true
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
    type: String
  }
});

const addressSchema = new mongoose.Schema({
  recipient: { type: String, required: true },
  phone: { type: String, required: true },
  province: { type: String, required: true },
  city: { type: String, required: true },
  district: { type: String, required: true },
  detail: { type: String, required: true }
});

const orderSchema = new mongoose.Schema({
  orderNumber: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
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
    min: 0,
    default: 0
  },
  discountAmount: {
    type: Number,
    required: true,
    min: 0,
    default: 0
  },
  finalAmount: {
    type: Number,
    required: true,
    min: 0
  },
  deliveryType: {
    type: String,
    enum: Object.values(DeliveryType),
    required: true
  },
  deliveryAddress: addressSchema,
  pickupTime: {
    type: Date
  },
  paymentMethod: {
    type: String,
    enum: Object.values(PaymentMethod),
    required: true
  },
  paymentStatus: {
    type: String,
    enum: ['pending', 'paid', 'refunded', 'failed'],
    default: 'pending',
    index: true
  },
  orderStatus: {
    type: String,
    enum: Object.values(OrderStatus),
    default: OrderStatus.PENDING_PAYMENT,
    index: true
  },
  remark: {
    type: String,
    trim: true
  },
  couponId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Coupon'
  }
}, {
  timestamps: true
});

// 生成订单号
orderSchema.pre('validate', function(next) {
  if (!this.orderNumber) {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
    this.orderNumber = `ORD${timestamp}${random}`;
  }
  next();
});

// 复合索引：按用户和状态查询
orderSchema.index({ userId: 1, orderStatus: 1 });

// 复合索引：按创建时间查询
orderSchema.index({ createdAt: -1 });

// 静态方法：按状态统计
orderSchema.statics.getStatusStats = async function(userId?: string) {
  const matchStage: any = {};
  if (userId) {
    matchStage.userId = new mongoose.Types.ObjectId(userId);
  }

  const result = await this.aggregate([
    { $match: matchStage },
    {
      $group: {
        _id: '$orderStatus',
        count: { $sum: 1 },
        totalAmount: { $sum: '$finalAmount' }
      }
    }
  ]);

  return result.reduce((acc: any, item) => {
    acc[item._id] = {
      count: item.count,
      totalAmount: item.totalAmount
    };
    return acc;
  }, {});
};

// 静态方法：获取用户订单
orderSchema.statics.getUserOrders = function(
  userId: string,
  options: {
    status?: OrderStatus;
    page?: number;
    limit?: number;
    startDate?: Date;
    endDate?: Date;
  }
) {
  const { status, page = 1, limit = 10, startDate, endDate } = options;
  const skip = (page - 1) * limit;

  const query: any = { userId };

  if (status) {
    query.orderStatus = status;
  }

  if (startDate || endDate) {
    query.createdAt = {};
    if (startDate) query.createdAt.$gte = startDate;
    if (endDate) query.createdAt.$lte = endDate;
  }

  return this.find(query)
    .sort({ createdAt: -1 })
    .skip(skip)
    .limit(limit)
    .populate('userId', 'nickname avatar')
    .populate('items.productId', 'name images');
};

export const OrderModel = mongoose.model('Order', orderSchema);
export type OrderDocument = mongoose.Document & typeof orderSchema;
```

- [ ] **Step 8: 实现其他模型**

```typescript
// break-mini-app/backend/src/models/Address.ts
import mongoose from 'mongoose';

const addressSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  recipient: {
    type: String,
    required: true,
    trim: true
  },
  phone: {
    type: String,
    required: true,
    match: /^1[3-9]\d{9}$/
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
  },
  isDefault: {
    type: Boolean,
    default: false
  }
}, {
  timestamps: true
});

// 确保每个用户只有一个默认地址
addressSchema.pre('save', async function(next) {
  if (this.isDefault) {
    await mongoose.model('Address').updateMany(
      { userId: this.userId, _id: { $ne: this._id } },
      { $set: { isDefault: false } }
    );
  }
  next();
});

// 静态方法：获取用户地址列表
addressSchema.statics.getUserAddresses = function(userId: string) {
  return this.find({ userId }).sort({ isDefault: -1, createdAt: -1 });
};

export const AddressModel = mongoose.model('Address', addressSchema);
export type AddressDocument = mongoose.Document & typeof addressSchema;
```

```typescript
// break-mini-app/backend/src/models/Coupon.ts
import mongoose from 'mongoose';

const couponSchema = new mongoose.Schema({
  code: {
    type: String,
    required: true,
    unique: true,
    uppercase: true,
    trim: true,
    index: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    trim: true
  },
  type: {
    type: String,
    enum: ['percentage', 'fixed'],
    required: true
  },
  value: {
    type: Number,
    required: true,
    min: 0
  },
  minPurchaseAmount: {
    type: Number,
    min: 0
  },
  validFrom: {
    type: Date,
    required: true
  },
  validTo: {
    type: Date,
    required: true
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
  }
}, {
  timestamps: true
});

// 检查优惠券是否可用
couponSchema.methods.isValid = function(amount?: number): boolean {
  const now = new Date();

  if (!this.isActive) return false;
  if (now < this.validFrom || now > this.validTo) return false;
  if (this.usageLimit && this.usedCount >= this.usageLimit) return false;
  if (amount && this.minPurchaseAmount && amount < this.minPurchaseAmount) return false;

  return true;
};

// 计算折扣金额
couponSchema.methods.calculateDiscount = function(amount: number): number {
  if (!this.isValid(amount)) return 0;

  if (this.type === 'percentage') {
    return Math.min(amount * this.value / 100, amount);
  } else {
    return Math.min(this.value, amount);
  }
};

export const CouponModel = mongoose.model('Coupon', couponSchema);
export type CouponDocument = mongoose.Document & typeof couponSchema;
```

```typescript
// break-mini-app/backend/src/models/Banner.ts
import mongoose from 'mongoose';

const bannerSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
    trim: true
  },
  image: {
    type: String,
    required: true
  },
  linkType: {
    type: String,
    enum: ['product', 'category', 'url'],
    required: true
  },
  linkTarget: {
    type: String,
    required: true
  },
  sortOrder: {
    type: Number,
    default: 0
  },
  isActive: {
    type: Boolean,
    default: true,
    index: true
  }
}, {
  timestamps: true
});

// 静态方法：获取有效banner
bannerSchema.statics.getActiveBanners = function() {
  return this.find({ isActive: true })
    .sort({ sortOrder: -1, createdAt: -1 })
    .limit(10);
};

export const BannerModel = mongoose.model('Banner', bannerSchema);
export type BannerDocument = mongoose.Document & typeof bannerSchema;
```

- [ ] **Step 9: 运行所有模型测试**

```bash
cd break-mini-app/backend
npm test -- tests/models/user.test.ts
```

运行：`npm test`
预期：所有模型测试通过

- [ ] **Step 10: 提交模型代码**

```bash
git add break-mini-app/shared/src/ break-mini-app/backend/src/models/ break-mini-app/backend/tests/
git commit -m "feat: implement data models for User, Product, Category, Order, Address, Coupon, and Banner"
```

### Task 3: 后端Express应用配置和中间件

**Files:**
- Create: `break-mini-app/backend/src/config/index.ts`
- Create: `break-mini-app/backend/src/middleware/auth.ts`
- Create: `break-mini-app/backend/src/middleware/rbac.ts`
- Create: `break-mini-app/backend/src/middleware/error.ts`
- Create: `break-mini-app/backend/src/middleware/validation.ts`
- Create: `break-mini-app/backend/src/utils/jwt.ts`
- Create: `break-mini-app/backend/src/app.ts`
- Create: `break-mini-app/backend/tests/middleware/auth.test.ts`
- Create: `break-mini-app/backend/tests/middleware/rbac.test.ts`

- [ ] **Step 1: 创建配置模块**

```typescript
// break-mini-app/backend/src/config/index.ts
import dotenv from 'dotenv';
import path from 'path';

// 加载环境变量
dotenv.config();

interface Config {
  env: string;
  port: number;
  mongodbUri: string;
  jwtSecret: string;
  wechat: {
    appId: string;
    appSecret: string;
    mchId: string;
    apiKey: string;
  };
  redisUrl: string;
  corsOrigin: string[];
  rateLimit: {
    windowMs: number;
    max: number;
  };
}

const config: Config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '3000', 10),
  mongodbUri: process.env.MONGODB_URI || 'mongodb://localhost:27017/break_mini_app',
  jwtSecret: process.env.JWT_SECRET || 'your_jwt_secret_key_here',
  wechat: {
    appId: process.env.WECHAT_APP_ID || '',
    appSecret: process.env.WECHAT_APP_SECRET || '',
    mchId: process.env.WECHAT_MCH_ID || '',
    apiKey: process.env.WECHAT_API_KEY || ''
  },
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',
  corsOrigin: (process.env.CORS_ORIGIN || 'http://localhost:8080').split(','),
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15分钟
    max: 100 // 每个IP每15分钟100个请求
  }
};

// 验证必要环境变量
const requiredEnvVars = ['JWT_SECRET'];
if (config.env === 'production') {
  requiredEnvVars.push('MONGODB_URI');
}

for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    throw new Error(`Missing required environment variable: ${envVar}`);
  }
}

export default config;
```

- [ ] **Step 2: 创建JWT工具**

```typescript
// break-mini-app/backend/src/utils/jwt.ts
import jwt from 'jsonwebtoken';
import config from '../config';
import { UserRole } from '../../../shared/src/types';

interface TokenPayload {
  userId: string;
  role: UserRole;
  openid?: string;
}

export class JWTService {
  static generateToken(payload: TokenPayload): string {
    return jwt.sign(payload, config.jwtSecret, {
      expiresIn: '7d'
    });
  }

  static verifyToken(token: string): TokenPayload {
    try {
      return jwt.verify(token, config.jwtSecret) as TokenPayload;
    } catch (error) {
      throw new Error('Invalid token');
    }
  }

  static generateRefreshToken(payload: TokenPayload): string {
    return jwt.sign(payload, config.jwtSecret, {
      expiresIn: '30d'
    });
  }

  static decodeToken(token: string): TokenPayload | null {
    try {
      return jwt.decode(token) as TokenPayload;
    } catch (error) {
      return null;
    }
  }
}

export default JWTService;
```

- [ ] **Step 3: 创建认证中间件测试**

```typescript
// break-mini-app/backend/tests/middleware/auth.test.ts
import { Request, Response, NextFunction } from 'express';
import { authMiddleware } from '../../src/middleware/auth';
import JWTService from '../../src/utils/jwt';

jest.mock('../../src/utils/jwt');

describe('Auth Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: NextFunction;

  beforeEach(() => {
    mockRequest = {
      headers: {}
    };
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    nextFunction = jest.fn();
  });

  test('should return 401 if no authorization header', () => {
    authMiddleware(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(mockResponse.json).toHaveBeenCalledWith({
      success: false,
      message: 'No authorization token provided'
    });
    expect(nextFunction).not.toHaveBeenCalled();
  });

  test('should return 401 if token format is invalid', () => {
    mockRequest.headers = {
      authorization: 'InvalidFormat'
    };

    authMiddleware(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(mockResponse.json).toHaveBeenCalledWith({
      success: false,
      message: 'Invalid token format'
    });
    expect(nextFunction).not.toHaveBeenCalled();
  });

  test('should return 401 if token is invalid', () => {
    mockRequest.headers = {
      authorization: 'Bearer invalid.token.here'
    };

    (JWTService.verifyToken as jest.Mock).mockImplementation(() => {
      throw new Error('Invalid token');
    });

    authMiddleware(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(mockResponse.json).toHaveBeenCalledWith({
      success: false,
      message: 'Invalid token'
    });
    expect(nextFunction).not.toHaveBeenCalled();
  });

  test('should attach user to request and call next if token is valid', () => {
    const mockUser = {
      userId: '123',
      role: 'customer',
      openid: 'test_openid'
    };

    mockRequest.headers = {
      authorization: 'Bearer valid.token.here'
    };

    (JWTService.verifyToken as jest.Mock).mockReturnValue(mockUser);

    authMiddleware(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockRequest.user).toEqual(mockUser);
    expect(nextFunction).toHaveBeenCalled();
    expect(mockResponse.status).not.toHaveBeenCalled();
    expect(mockResponse.json).not.toHaveBeenCalled();
  });
});
```

运行：`cd break-mini-app/backend && npm test -- tests/middleware/auth.test.ts`
预期：FAIL with "Cannot find module '../../src/middleware/auth'"

- [ ] **Step 4: 实现认证中间件**

```typescript
// break-mini-app/backend/src/middleware/auth.ts
import { Request, Response, NextFunction } from 'express';
import JWTService from '../utils/jwt';
import { UserRole } from '../../../shared/src/types';

declare global {
  namespace Express {
    interface Request {
      user?: {
        userId: string;
        role: UserRole;
        openid?: string;
      };
    }
  }
}

export const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({
      success: false,
      message: 'No authorization token provided'
    });
  }

  const tokenParts = authHeader.split(' ');

  if (tokenParts.length !== 2 || tokenParts[0] !== 'Bearer') {
    return res.status(401).json({
      success: false,
      message: 'Invalid token format'
    });
  }

  const token = tokenParts[1];

  try {
    const decoded = JWTService.verifyToken(token);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({
      success: false,
      message: 'Invalid token'
    });
  }
};

// 可选的认证中间件，不强制要求登录
export const optionalAuthMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return next();
  }

  const tokenParts = authHeader.split(' ');

  if (tokenParts.length !== 2 || tokenParts[0] !== 'Bearer') {
    return next();
  }

  const token = tokenParts[1];

  try {
    const decoded = JWTService.verifyToken(token);
    req.user = decoded;
    next();
  } catch (error) {
    next();
  }
};
```

运行：`cd break-mini-app/backend && npm test -- tests/middleware/auth.test.ts`
预期：PASS (所有测试通过)

- [ ] **Step 5: 实现RBAC中间件测试**

```typescript
// break-mini-app/backend/tests/middleware/rbac.test.ts
import { Request, Response, NextFunction } from 'express';
import { requireRole } from '../../src/middleware/rbac';
import { UserRole } from '../../../shared/src/types';

describe('RBAC Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: NextFunction;

  beforeEach(() => {
    mockRequest = {};
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    nextFunction = jest.fn();
  });

  test('should return 401 if user not authenticated', () => {
    requireRole(UserRole.ADMIN)(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(mockResponse.json).toHaveBeenCalledWith({
      success: false,
      message: 'Authentication required'
    });
    expect(nextFunction).not.toHaveBeenCalled();
  });

  test('should return 403 if user does not have required role', () => {
    mockRequest.user = {
      userId: '123',
      role: UserRole.CUSTOMER
    };

    requireRole(UserRole.ADMIN)(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockResponse.status).toHaveBeenCalledWith(403);
    expect(mockResponse.json).toHaveBeenCalledWith({
      success: false,
      message: 'Insufficient permissions'
    });
    expect(nextFunction).not.toHaveBeenCalled();
  });

  test('should call next if user has required role', () => {
    mockRequest.user = {
      userId: '123',
      role: UserRole.ADMIN
    };

    requireRole(UserRole.ADMIN)(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(nextFunction).toHaveBeenCalled();
    expect(mockResponse.status).not.toHaveBeenCalled();
    expect(mockResponse.json).not.toHaveBeenCalled();
  });

  test('should allow multiple roles', () => {
    mockRequest.user = {
      userId: '123',
      role: UserRole.STAFF
    };

    requireRole([UserRole.ADMIN, UserRole.STAFF])(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(nextFunction).toHaveBeenCalled();
    expect(mockResponse.status).not.toHaveBeenCalled();
    expect(mockResponse.json).not.toHaveBeenCalled();
  });
});
```

运行：`cd break-mini-app/backend && npm test -- tests/middleware/rbac.test.ts`
预期：FAIL with "Cannot find module '../../src/middleware/rbac'"

- [ ] **Step 6: 实现RBAC中间件**

```typescript
// break-mini-app/backend/src/middleware/rbac.ts
import { Request, Response, NextFunction } from 'express';
import { UserRole } from '../../../shared/src/types';

export const requireRole = (role: UserRole | UserRole[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Authentication required'
      });
    }

    const requiredRoles = Array.isArray(role) ? role : [role];
    const hasRole = requiredRoles.includes(req.user.role);

    if (!hasRole) {
      return res.status(403).json({
        success: false,
        message: 'Insufficient permissions'
      });
    }

    next();
  };
};

// 检查是否是管理员（admin或staff）
export const requireAdmin = requireRole([UserRole.ADMIN, UserRole.STAFF]);

// 检查是否是普通用户
export const requireCustomer = requireRole(UserRole.CUSTOMER);
```

运行：`cd break-mini-app/backend && npm test -- tests/middleware/rbac.test.ts`
预期：PASS (所有测试通过)

- [ ] **Step 7: 实现错误处理中间件**

```typescript
// break-mini-app/backend/src/middleware/error.ts
import { Request, Response, NextFunction } from 'express';
import config from '../config';

interface AppError extends Error {
  statusCode?: number;
  code?: number;
}

export const errorMiddleware = (
  error: AppError,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const statusCode = error.statusCode || 500;
  const message = error.message || 'Internal Server Error';

  // 记录错误
  if (config.env !== 'test') {
    console.error(`[${new Date().toISOString()}] ${req.method} ${req.url}`, {
      error: message,
      stack: config.env === 'development' ? error.stack : undefined,
      body: req.body,
      query: req.query,
      params: req.params
    });
  }

  res.status(statusCode).json({
    success: false,
    message,
    ...(config.env === 'development' && { stack: error.stack })
  });
};

// 404处理中间件
export const notFoundMiddleware = (req: Request, res: Response) => {
  res.status(404).json({
    success: false,
    message: `Route ${req.method} ${req.url} not found`
  });
};

// 异步错误包装器
export const asyncHandler = (fn: Function) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};
```

- [ ] **Step 8: 实现验证中间件**

```typescript
// break-mini-app/backend/src/middleware/validation.ts
import { Request, Response, NextFunction } from 'express';
import { validationResult } from 'express-validator';

export const validate = (validations: any[]) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    await Promise.all(validations.map(validation => validation.run(req)));

    const errors = validationResult(req);
    if (errors.isEmpty()) {
      return next();
    }

    res.status(400).json({
      success: false,
      message: 'Validation failed',
      errors: errors.array()
    });
  };
};

// 通用验证规则
export const commonValidators = {
  objectId: (field: string) => ({
    custom: {
      options: (value: string) => {
        if (!value) return true;
        return /^[0-9a-fA-F]{24}$/.test(value);
      },
      errorMessage: `${field} must be a valid ObjectId`
    }
  }),

  email: {
    isEmail: true,
    errorMessage: 'Invalid email address'
  },

  phone: {
    matches: {
      options: /^1[3-9]\d{9}$/,
      errorMessage: 'Invalid phone number format'
    }
  },

  password: {
    isLength: {
      options: { min: 6 },
      errorMessage: 'Password must be at least 6 characters long'
    }
  },

  positiveNumber: (field: string) => ({
    custom: {
      options: (value: number) => value > 0,
      errorMessage: `${field} must be a positive number`
    }
  }),

  nonNegativeNumber: (field: string) => ({
    custom: {
      options: (value: number) => value >= 0,
      errorMessage: `${field} must be a non-negative number`
    }
  })
};
```

- [ ] **Step 9: 实现Express主应用**

```typescript
// break-mini-app/backend/src/app.ts
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import mongoose from 'mongoose';
import config from './config';
import { errorMiddleware, notFoundMiddleware } from './middleware/error';
import { authMiddleware } from './middleware/auth';

// 导入路由（稍后实现）
// import authRoutes from './routes/auth';
// import productRoutes from './routes/products';
// import orderRoutes from './routes/orders';
// import adminRoutes from './routes/admin';

class App {
  public app: express.Application;

  constructor() {
    this.app = express();
    this.connectDatabase();
    this.initializeMiddlewares();
    this.initializeRoutes();
    this.initializeErrorHandling();
  }

  private connectDatabase(): void {
    mongoose
      .connect(config.mongodbUri)
      .then(() => {
        console.log('Connected to MongoDB');
      })
      .catch((error) => {
        console.error('MongoDB connection error:', error);
        process.exit(1);
      });

    mongoose.connection.on('error', (error) => {
      console.error('MongoDB error:', error);
    });

    mongoose.connection.on('disconnected', () => {
      console.log('MongoDB disconnected');
    });
  }

  private initializeMiddlewares(): void {
    // 安全中间件
    this.app.use(helmet());

    // CORS配置
    this.app.use(cors({
      origin: config.corsOrigin,
      credentials: true
    }));

    // 请求体解析
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // 速率限制
    if (config.env === 'production') {
      this.app.use(rateLimit(config.rateLimit));
    }

    // 请求日志
    this.app.use((req, res, next) => {
      if (config.env !== 'test') {
        console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
      }
      next();
    });
  }

  private initializeRoutes(): void {
    // 健康检查
    this.app.get('/health', (req, res) => {
      res.json({
        success: true,
        message: 'Server is healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
      });
    });

    // API路由
    // this.app.use('/api/auth', authRoutes);
    // this.app.use('/api/products', productRoutes);
    // this.app.use('/api/orders', orderRoutes);
    // this.app.use('/api/admin', authMiddleware, requireAdmin, adminRoutes);

    // 静态文件服务（如果需要）
    this.app.use('/uploads', express.static('uploads'));
  }

  private initializeErrorHandling(): void {
    // 404处理
    this.app.use(notFoundMiddleware);

    // 全局错误处理
    this.app.use(errorMiddleware);
  }

  public start(): void {
    this.app.listen(config.port, () => {
      console.log(`Server is running on port ${config.port}`);
      console.log(`Environment: ${config.env}`);
      console.log(`MongoDB: ${config.mongodbUri}`);
    });
  }
}

export default App;
```

- [ ] **Step 10: 创建入口文件并测试启动**

```typescript
// break-mini-app/backend/src/index.ts
import App from './app';

const app = new App();
app.start();

// 优雅关闭
process.on('SIGINT', () => {
  console.log('SIGINT received. Shutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('SIGTERM received. Shutting down gracefully...');
  process.exit(0);
});
```

```bash
# 测试启动
cd break-mini-app/backend
npm run build
npm start
```

运行：`cd break-mini-app/backend && npm run build`
预期：TypeScript编译成功

运行：`npm start`
预期：服务器启动，显示"MongoDB connection error"（因为没有运行MongoDB实例）

- [ ] **Step 11: 提交中间件和配置代码**

```bash
git add break-mini-app/backend/src/config/ break-mini-app/backend/src/middleware/ break-mini-app/backend/src/utils/ break-mini-app/backend/src/app.ts break-mini-app/backend/src/index.ts break-mini-app/backend/tests/middleware/
git commit -m "feat: implement Express app configuration, middleware (auth, rbac, error, validation), and JWT utilities"
```