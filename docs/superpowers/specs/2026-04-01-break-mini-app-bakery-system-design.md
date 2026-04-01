# 面包店小程序全栈系统设计规范

> **设计确认日期**: 2026-04-01  
> **项目状态**: 实施中（部分完成）  
> **上次计划审查**: 2026-03-31

## 项目概述

**目标**: 实现一个完整的面包店小程序全栈系统，包含用户端小程序、后台管理、RBAC权限控制、微信支付集成、实时库存管理等完整功能。

**核心需求**:
- 用户端：商品浏览、购物车、下单支付、订单管理、地址管理
- 管理端：商品管理、订单处理、用户管理、数据统计
- 权限控制：基于角色的访问控制（RBAC）
- 微信生态集成：小程序登录、微信支付
- 实时功能：库存管理、订单状态通知

## 架构决策 ✅ 已确认

### 整体架构
- **模式**: 模块化单体应用
- **部署**: 单一代码库，多包工作区（monorepo）
- **通信**: RESTful API + 可选WebSocket实时通知

### 包结构
```
break-mini-app/
├── backend/          # Node.js/Express后端API
├── frontend/         # uni-app小程序前端
├── shared/           # 共享类型和常量定义
└── docs/            # 文档和设计规范
```

### 数据流
1. 小程序前端 (uni-app) → HTTP API → Express后端
2. Express后端 ↔ MongoDB数据库
3. 共享类型确保前后端类型安全

## 技术栈 ✅ 已确认

### 后端技术栈
- **运行时**: Node.js + TypeScript
- **框架**: Express.js
- **数据库**: MongoDB + Mongoose ODM
- **认证**: JWT + 微信小程序登录
- **安全**: Helmet, CORS, 速率限制, 输入验证
- **实时**: Socket.IO（可选）

### 前端技术栈
- **框架**: uni-app (Vue 3 + TypeScript)
- **状态管理**: Pinia
- **UI组件库**: Vant Weapp
- **HTTP客户端**: Axios
- **构建目标**: 微信小程序

### 开发工具
- **包管理**: npm workspaces
- **构建工具**: TypeScript编译器
- **测试框架**: Jest (后端), Vue Test Utils (前端)
- **代码质量**: ESLint, Prettier

## 数据模型设计 ✅ 已实现

### 核心模型（MongoDB + Mongoose）
1. **User模型** (`backend/src/models/User.ts`)
   - openid (唯一索引), nickname, avatar, phone, email
   - role: customer/admin/staff
   - 实例方法: hasRole(), isAdmin()

2. **Product模型** (`backend/src/models/Product.ts`)
   - name, description, price, originalPrice, categoryId
   - images, stock, salesCount, status (active/inactive/out_of_stock)
   - specs规格数组, sortOrder排序

3. **Category模型** (`backend/src/models/Category.ts`)
   - name, description, icon, parentId, sortOrder

4. **Order模型** (`backend/src/models/Order.ts`)
   - orderNumber订单号, userId, items订单项数组
   - totalAmount总金额, deliveryFee配送费, discountAmount优惠
   - deliveryType (pickup/delivery), paymentMethod, orderStatus

5. **辅助模型**
   - Address地址模型
   - Coupon优惠券模型  
   - Banner轮播图模型

### 共享类型定义 (`shared/src/types/`)
- `UserRole`: customer/admin/staff枚举
- `OrderStatus`: 8种订单状态枚举
- `ProductStatus`: 3种商品状态枚举
- `DeliveryType`: pickup/delivery枚举
- `PaymentMethod`: wechat/alipay/cash枚举
- 完整接口定义: User, Product, Category, Order, Address, Coupon, Banner

### 共享常量 (`shared/src/constants/`)
- DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
- PRODUCT_CATEGORIES产品分类
- DELIVERY_FEE, FREE_DELIVERY_THRESHOLD
- ORDER_STATUS_MAP状态映射
- PAYMENT_METHODS支付方式

## API设计 🔄 部分实现

### REST API架构
- **分层结构**: 路由 → 控制器 → 服务 → 模型
- **HTTP方法**: RESTful规范 (GET/POST/PUT/DELETE)
- **响应格式**: JSON统一响应体
- **错误处理**: 统一错误中间件

### 中间件实现 (`backend/src/middleware/`)
1. **auth.ts**: JWT认证中间件
2. **rbac.ts**: 基于角色的访问控制
3. **error.ts**: 统一错误处理中间件
4. **validation.ts**: 请求参数验证

### 已实现API端点
- **认证相关** (`backend/src/routes/auth.routes.ts`)
  - POST /api/auth/wechat-login - 微信小程序登录
  - POST /api/auth/refresh-token - 刷新令牌
  - GET /api/auth/profile - 获取用户资料

- **产品相关** (`backend/src/controllers/product.controller.ts`)
  - GET /api/products - 获取产品列表
  - GET /api/products/:id - 获取产品详情

### 待实现API端点
- 订单管理: /api/orders
- 购物车: /api/cart  
- 地址管理: /api/addresses
- 优惠券: /api/coupons
- 轮播图: /api/banners
- 管理接口: /api/admin/*

## 前端架构 📋 待实现

### uni-app目录结构（计划）
```
frontend/src/
├── pages/           # 小程序页面
│   ├── index/      # 首页
│   ├── product-detail/ # 商品详情
│   ├── cart/       # 购物车
│   ├── order-confirm/ # 订单确认
│   ├── order-list/ # 我的订单
│   ├── user-center/ # 用户中心
│   ├── address/    # 地址管理
│   ├── login/      # 登录页
│   └── admin/      # 管理页面（条件渲染）
├── components/     # 公共组件
├── store/         # Pinia状态管理
├── api/           # API请求封装
├── utils/         # 工具函数
├── static/        # 静态资源
├── uni.scss       # 全局样式
├── manifest.json  # 应用配置
├── pages.json     # 页面配置
└── App.vue        # 应用入口
```

### 状态管理设计
- **Pinia Store模块**:
  - userStore: 用户信息、登录状态
  - cartStore: 购物车商品、数量、总价
  - orderStore: 订单列表、当前订单状态
  - productStore: 商品列表、分类、筛选

### UI组件规划
- **Vant Weapp组件库**: 按钮、表单、弹窗、轮播等
- **自定义组件**: 商品卡片、订单项、地址选择器
- **条件渲染**: 用户/管理员界面切换

## 开发工作流 ✅ 已配置

### 包管理工作区
```json
// package.json (根)
{
  "workspaces": ["backend", "frontend", "shared"],
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "dev:backend": "cd backend && npm run dev",
    "dev:frontend": "cd frontend && npm run dev",
    "build": "npm run build:backend && npm run build:frontend",
    "test": "npm run test:backend && npm run test:frontend"
  }
}
```

### 后端开发脚本
```json
// backend/package.json
{
  "scripts": {
    "dev": "tsx watch src/app.ts",
    "build": "tsc",
    "start": "node dist/app.js",
    "test": "jest",
    "test:watch": "jest --watch"
  }
}
```

### 前端开发脚本
```json
// frontend/package.json  
{
  "scripts": {
    "dev": "npm run dev:mp-weixin",
    "dev:mp-weixin": "uni -p mp-weixin",
    "build": "npm run build:mp-weixin",
    "build:mp-weixin": "uni build -p mp-weixin",
    "test": "jest",
    "lint": "eslint . --ext .vue,.js,.ts"
  }
}
```

## 当前实施状态

### ✅ 已完成
1. **项目初始化** (Task 1)
   - Monorepo工作区配置
   - 所有package.json文件
   - TypeScript配置
   - 环境变量模板

2. **数据模型** (Task 2)
   - 所有7个MongoDB模型实现
   - 共享类型定义 (shared/src/types/)
   - 共享常量定义 (shared/src/constants/)
   - User模型测试

3. **后端基础架构** (额外实现)
   - Express应用配置 (`backend/src/app.ts`)
   - 中间件: auth, rbac, error, validation
   - JWT工具函数 (`backend/src/utils/jwt.ts`)
   - 配置管理 (`backend/src/config/index.ts`)

4. **部分控制器和路由**
   - 认证控制器 (`backend/src/controllers/auth.controller.ts`)
   - 产品控制器 (`backend/src/controllers/product.controller.ts`)
   - 认证路由 (`backend/src/routes/auth.routes.ts`)

### 🔄 进行中
1. **后端API实现**
   - 需要完成剩余控制器: order, cart, address, coupon, banner
   - 需要完成剩余路由文件
   - 需要实现服务层业务逻辑

2. **前端开发**
   - `frontend/src`目录为空，需要实现所有uni-app页面和组件
   - 需要配置uni-app项目结构
   - 需要实现Pinia状态管理
   - 需要集成Vant Weapp组件

3. **测试覆盖**
   - 后端模型测试部分完成
   - 需要添加控制器和服务测试
   - 前端测试待配置

### 📋 待开始
1. **微信集成**
   - 微信小程序登录实现
   - 微信支付API集成
2. **管理功能**
   - 管理员界面条件渲染
   - 数据统计和报表
3. **部署配置**
   - Docker容器化
   - 生产环境配置

## Git提交历史
```
2ec875e feat: implement Express app configuration, middleware (auth, rbac, error, validation), and JWT utilities
03ea1dc Fix code quality issues in data models  
f4faa30 feat: implement data models for User, Product, Category, Order, Address, Coupon, and Banner
bff0dd1 feat: initialize project structure with backend, frontend, and shared packages
```

## 后续实施策略

### 推荐方法: 子代理驱动开发 (Subagent-Driven Development)
基于项目结构和当前状态，建议采用并行实施策略：

1. **后端子代理**: 完成剩余API控制器、路由和服务层
2. **前端子代理**: 实现uni-app页面、组件和状态管理  
3. **共享子代理**: 完善类型定义和工具函数

### 实施优先级
1. **高优先级**: 完成核心用户流程
   - 用户认证 → 商品浏览 → 购物车 → 下单支付
2. **中优先级**: 管理功能
   - 商品管理 → 订单处理 → 用户管理
3. **低优先级**: 增强功能
   - 实时通知 → 数据分析 → 营销功能

### 质量保证
- 每个功能模块配套单元测试
- API端点集成测试
- 前端组件测试
- 类型安全通过共享类型保证

---

**设计确认**: 所有架构和技术栈决策已在2026-04-01确认通过用户审阅。

**下一步**: 使用superpowers:subagent-driven-development技能启动并行实施。