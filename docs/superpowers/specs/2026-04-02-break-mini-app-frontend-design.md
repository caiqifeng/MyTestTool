---
name: break-mini-app-frontend-design
description: 面包店小程序前端实现设计方案 - 基于Vue 3 + uni-app + Vant的混合渐进式架构
type: design
---

# 面包店小程序前端设计方案

## 项目概述

**项目名称**: break-mini-app (面包店电商小程序)  
**目标平台**: 微信小程序 (主要) + H5 (兼容)  
**技术栈**: Vue 3 + TypeScript + uni-app + Pinia + Vant + Axios  
**设计理念**: 混合渐进式架构 - 从简单开始，保持架构演进能力  
**开发模式**: 敏捷迭代，分阶段实施

## 架构设计 (方案C: 混合渐进式架构)

### 核心原则
1. **初始简单**: 使用uni-app标准页面结构快速启动
2. **渐进演进**: 随着功能复杂化，逐步引入模块化和组件化
3. **状态管理分层**: 全局数据用Pinia，局部数据用组件状态
4. **组件复用**: 从基础组件开始，逐步抽离业务组件

### 技术栈确认
- **框架**: uni-app (Vue 3) + TypeScript (严格模式)
- **UI库**: Vant Weapp (微信小程序兼容版本)
- **状态管理**: Pinia (Vuex 5)
- **HTTP客户端**: Axios (带拦截器配置)
- **样式语言**: SCSS/Sass
- **构建工具**: uni-app CLI
- **代码质量**: ESLint + Prettier
- **测试框架**: Jest + Vue Test Utils (待修复配置)

### 文件结构设计
```
frontend/
├── pages/                    # 页面目录 (uni-app标准结构)
│   ├── index/               # 首页
│   │   ├── index.vue
│   │   └── index.scss
│   ├── product/             # 商品模块
│   │   ├── list/           # 商品列表页
│   │   ├── detail/         # 商品详情页
│   │   └── category/       # 分类页
│   ├── cart/               # 购物车模块
│   │   ├── index.vue       # 购物车主页
│   │   └── edit.vue        # 购物车编辑
│   ├── order/              # 订单模块
│   │   ├── confirm/        # 订单确认
│   │   ├── address/        # 地址管理
│   │   ├── payment/        # 支付页
│   │   └── list/           # 订单列表
│   └── user/               # 用户模块
│       ├── index.vue       # 个人中心
│       ├── profile/        # 个人资料
│       ├── address/        # 地址管理
│       └── coupon/         # 优惠券
├── components/             # 可复用组件库
│   ├── common/             # 通用基础组件
│   │   ├── BaseButton.vue
│   │   ├── BaseCard.vue
│   │   ├── BaseModal.vue
│   │   └── BaseLoading.vue
│   ├── product/            # 商品相关组件
│   │   ├── ProductCard.vue (已存在)
│   │   ├── ProductList.vue
│   │   └── CategoryNav.vue
│   ├── cart/               # 购物车组件
│   │   ├── CartItem.vue
│   │   └── CartTotal.vue
│   ├── order/              # 订单组件
│   │   ├── OrderCard.vue
│   │   └── AddressCard.vue
│   ├── layout/             # 布局组件
│   │   ├── NavBar.vue
│   │   ├── TabBar.vue
│   │   └── PageContainer.vue
│   └── business/           # 业务组件
│       └── BannerSwiper.vue
├── stores/                 # Pinia状态管理
│   ├── user.store.ts       # 用户状态
│   ├── cart.store.ts       # 购物车状态
│   ├── product.store.ts    # 商品状态
│   ├── order.store.ts      # 订单状态
│   └── index.ts            # 统一导出
├── utils/                  # 工具函数
│   ├── api/                # API封装层
│   │   ├── auth.api.ts
│   │   ├── product.api.ts
│   │   ├── order.api.ts
│   │   ├── cart.api.ts
│   │   ├── address.api.ts
│   │   ├── coupon.api.ts
│   │   └── index.ts
│   ├── auth/               # 认证工具
│   │   ├── wechat.ts       # 微信登录封装
│   │   └── token.ts        # Token管理
│   ├── wx/                 # 微信小程序API封装
│   │   ├── wxapi.ts        # 微信API统一封装
│   │   └── wxpay.ts        # 微信支付封装
│   ├── formatter.ts        # 数据格式化
│   ├── validator.ts        # 表单验证
│   └── helper.ts           # 辅助函数
├── types/                  # TypeScript类型定义
│   ├── api.d.ts            # API接口类型
│   ├── store.d.ts          # Store状态类型
│   ├── component.d.ts      # 组件Props/Events类型
│   └── wx.d.ts             # 微信API类型补充
├── styles/                 # 样式系统
│   ├── variables.scss      # 设计变量
│   ├── mixins.scss         # SCSS Mixin
│   ├── global.scss         # 全局样式
│   ├── components.scss     # 组件样式
│   └── theme/              # 主题配置
│       ├── light.scss      # 浅色主题
│       └── dark.scss       # 深色主题(可选)
├── static/                 # 静态资源
│   ├── images/             # 图片资源
│   │   ├── banner/         # Banner图片
│   │   ├── product/        # 商品图片
│   │   └── icons/          # 图标图片
│   └── fonts/              # 字体文件
├── config/                 # 配置文件
│   ├── app.config.ts       # 应用配置
│   ├── wx.config.ts        # 微信小程序配置
│   └── api.config.ts       # API配置
└── uni-app核心文件
    ├── pages.json          # 页面路由配置
    ├── manifest.json       # 应用manifest
    ├── App.vue             # 应用根组件
    ├── main.ts             # 应用入口
    └── uni.scss            # uni-app全局样式
```

## 核心页面设计

### 1. 首页 (`pages/index/index`)
**功能**:
- Banner轮播展示 (对接 `/api/banners` API)
- 商品分类快捷导航
- 热门/推荐商品展示区
- 限时优惠活动入口
- 搜索框 (全局搜索入口)

**UI元素**:
- 自定义导航栏 (店铺Logo、搜索入口)
- Banner轮播组件 (支持自动播放、跳转)
- 分类网格 (4-6个主要分类)
- 商品瀑布流/网格列表
- 底部标签栏 (首页/购物车/我的)

### 2. 商品模块
#### 2.1 商品列表页 (`pages/product/list`)
**功能**:
- 多维度筛选 (分类、价格、销量、新品)
- 排序选项 (综合、价格、销量)
- 关键词搜索
- 分页加载
- 商品网格展示

#### 2.2 商品详情页 (`pages/product/detail`)
**功能**:
- 商品图片轮播展示
- 基本信息 (名称、价格、库存)
- 商品规格选择 (尺寸、口味等)
- 商品详情 (富文本/图片)
- 加入购物车/立即购买按钮
- 相关商品推荐

### 3. 购物车模块 (`pages/cart/index`)
**功能**:
- 商品列表展示 (图片、名称、价格、数量)
- 数量增减、删除商品
- 全选/反选
- 优惠券选择和应用
- 价格明细 (商品总价、优惠、运费、实付)
- 结算按钮 (跳转订单确认页)

### 4. 订单模块
#### 4.1 订单确认页 (`pages/order/confirm`)
**功能**:
- 收货地址选择/管理入口
- 商品清单确认
- 订单备注输入
- 配送方式选择 (配送/自提)
- 配送时间选择
- 优惠券选择
- 价格计算展示
- 提交订单按钮

#### 4.2 地址管理页 (`pages/order/address`)
**功能**:
- 地址列表展示
- 新增/编辑地址
- 设为默认地址
- 地址删除确认
- 地址选择回传

#### 4.3 支付页 (`pages/order/payment`)
**功能**:
- 订单信息摘要
- 支付方式选择 (微信支付、余额、货到付款)
- 微信支付唤起
- 支付结果处理
- 订单状态更新

#### 4.4 订单列表页 (`pages/order/list`)
**功能**:
- 订单状态筛选 (全部、待支付、待发货、待收货、已完成)
- 订单卡片展示
- 订单详情查看
- 订单状态追踪
- 取消订单/确认收货操作

### 5. 用户模块 (`pages/user/index`)
**功能**:
- 用户头像和昵称展示
- 订单状态入口 (待支付、待发货等)
- 功能入口 (地址管理、优惠券、客服、设置)
- 订单列表快捷入口
- 退出登录

## 组件体系设计

### 基础组件 (基于Vant扩展)
1. **BaseButton**: 统一按钮样式和行为
   - 支持primary/secondary/ghost类型
   - 加载状态、禁用状态
   - 大小定制 (small/medium/large)

2. **BaseCard**: 卡片容器组件
   - 统一阴影、圆角
   - 标题、内容、操作区域插槽
   - 点击效果

3. **BaseModal**: 模态框组件
   - 支持多种动画效果
   - 标题、内容、底部按钮自定义
   - 异步关闭支持

4. **BaseLoading**: 加载状态组件
   - 全屏加载、局部加载
   - 自定义加载文案、图标
   - 骨架屏支持

### 业务组件
1. **ProductCard**: 商品卡片 (已存在，需扩展)
   - 图片懒加载
   - 价格显示 (现价/原价)
   - 库存状态提示
   - 加入购物车按钮

2. **CartItem**: 购物车商品项
   - 勾选状态
   - 数量加减器
   - 价格计算
   - 删除确认

3. **OrderCard**: 订单卡片
   - 订单状态标签
   - 商品摘要
   - 价格信息
   - 操作按钮组

4. **AddressCard**: 地址卡片
   - 联系人信息
   - 地址详情
   - 默认地址标识
   - 编辑/删除操作

### 布局组件
1. **NavBar**: 自定义导航栏
   - 返回按钮 (可配置)
   - 标题 (居中)
   - 右侧操作按钮
   - 沉浸式适配

2. **TabBar**: 底部标签栏
   - 图标+文字组合
   - 红点/数字角标
   - 路由跳转
   - 选中状态

3. **PageContainer**: 页面容器
   - 统一页面边距
   - 滚动容器
   - 加载状态
   - 空状态展示

## 状态管理策略

### Pinia Store结构

```typescript
// stores/user.store.ts
interface UserState {
  userInfo: User | null;
  isLoggedIn: boolean;
  token: string | null;
  refreshToken: string | null;
}

// stores/cart.store.ts
interface CartState {
  items: CartItem[];
  selectedItems: string[]; // 选中的商品ID
  coupon?: Coupon; // 应用的优惠券
}

// stores/product.store.ts  
interface ProductState {
  products: Product[];
  categories: Category[];
  currentProduct: Product | null;
  searchHistory: string[];
}

// stores/order.store.ts
interface OrderState {
  currentOrder: Order | null; // 当前正在创建的订单
  orders: Order[]; // 历史订单
  addresses: Address[]; // 收货地址
  coupons: Coupon[]; // 可用优惠券
}
```

### 状态使用原则
1. **全局共享数据**使用Pinia store
   - 用户登录状态
   - 购物车数据
   - 商品分类信息
   - 订单状态

2. **页面局部状态**使用组件data/reactive
   - 表单输入
   - 页面内筛选条件
   - 临时UI状态

3. **跨页面共享状态**使用store
   - 商品详情 → 购物车
   - 购物车 → 订单确认
   - 地址选择 → 订单确认

## API集成方案

### Axios配置
```typescript
// utils/api/index.ts
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加token
api.interceptors.request.use(config => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  response => response.data,
  error => {
    // Token过期处理
    if (error.response?.status === 401) {
      return handleTokenExpired(error);
    }
    // 统一错误提示
    showToast(error.response?.data?.message || '网络错误');
    return Promise.reject(error);
  }
);
```

### API模块划分
```typescript
// utils/api/auth.api.ts
export const authApi = {
  // 微信登录
  wechatLogin: (code: string, userInfo?: Partial<User>) => 
    api.post<{ token: string; user: User }>('/auth/wechat-login', { code, ...userInfo }),
  
  // 获取当前用户
  getCurrentUser: () => api.get<User>('/auth/me'),
  
  // 刷新token
  refreshToken: (refreshToken: string) => 
    api.post<{ token: string }>('/auth/refresh-token', { refreshToken }),
};

// utils/api/product.api.ts
export const productApi = {
  // 获取商品列表
  getProducts: (params?: ProductQueryParams) => 
    api.get<{ products: Product[]; total: number }>('/products', { params }),
  
  // 获取商品详情
  getProduct: (id: string) => api.get<Product>(`/products/${id}`),
  
  // 获取商品分类
  getCategories: () => api.get<Category[]>('/categories'),
};

// utils/api/order.api.ts
export const orderApi = {
  // 创建订单
  createOrder: (orderData: CreateOrderDto) => 
    api.post<Order>('/orders', orderData),
  
  // 获取订单列表
  getOrders: (params?: OrderQueryParams) => 
    api.get<{ orders: Order[]; total: number }>('/orders', { params }),
  
  // 获取订单详情
  getOrder: (id: string) => api.get<Order>(`/orders/${id}`),
};
```

## 样式系统设计

### 品牌色系 (面包店主题)
```scss
// variables.scss
// 主色调 - 温暖面包感
$color-primary: #FF6B35;    // 橙色 - 主按钮、重要元素
$color-primary-light: #FF9B70; // 浅橙色 - 悬浮状态
$color-primary-dark: #D94B1A;  // 深橙色 - 按下状态

// 辅助色 - 清新感
$color-secondary: #4ECDC4;     // 青绿色 - 次要按钮、标签
$color-secondary-light: #8AE0D8;
$color-secondary-dark: #2BA9A1;

// 中性色
$color-text-primary: #333333;   // 主要文字
$color-text-secondary: #666666; // 次要文字
$color-text-tertiary: #999999;  // 辅助文字
$color-border: #E0E0E0;         // 边框色
$color-background: #F8F8F8;     // 背景色
$color-white: #FFFFFF;
$color-black: #000000;

// 功能色
$color-success: #52C41A;        // 成功
$color-warning: #FAAD14;        // 警告
$color-error: #FF4D4F;          // 错误
$color-info: #1890FF;           // 信息

// 间距系统
$spacing-unit: 8px;
$spacing-xs: $spacing-unit * 0.5;  // 4px
$spacing-sm: $spacing-unit;        // 8px
$spacing-md: $spacing-unit * 2;    // 16px
$spacing-lg: $spacing-unit * 3;    // 24px
$spacing-xl: $spacing-unit * 4;    // 32px
$spacing-xxl: $spacing-unit * 6;   // 48px

// 圆角系统
$border-radius-sm: 4px;
$border-radius-md: 8px;
$border-radius-lg: 12px;
$border-radius-xl: 16px;
$border-radius-round: 999px;

// 字体系统
$font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
              'Helvetica Neue', Arial, sans-serif, 'Apple Color Emoji';
$font-size-xs: 12px;
$font-size-sm: 14px;
$font-size-md: 16px;
$font-size-lg: 18px;
$font-size-xl: 20px;
$font-size-xxl: 24px;

// 阴影系统
$shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
$shadow-md: 0 4px 12px rgba(0, 0, 0, 0.12);
$shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.16);
$shadow-xl: 0 12px 48px rgba(0, 0, 0, 0.2);
```

### 响应式设计
```scss
// mixins.scss
// 响应式断点
$breakpoint-sm: 576px;
$breakpoint-md: 768px;
$breakpoint-lg: 992px;
$breakpoint-xl: 1200px;

@mixin respond-to($breakpoint) {
  @if $breakpoint == sm {
    @media (min-width: $breakpoint-sm) { @content; }
  } @else if $breakpoint == md {
    @media (min-width: $breakpoint-md) { @content; }
  } @else if $breakpoint == lg {
    @media (min-width: $breakpoint-lg) { @content; }
  } @else if $breakpoint == xl {
    @media (min-width: $breakpoint-xl) { @content; }
  }
}

// 弹性布局工具
@mixin flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

@mixin flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

@mixin flex-column {
  display: flex;
  flex-direction: column;
}

// 文字溢出省略
@mixin text-ellipsis($lines: 1) {
  @if $lines == 1 {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  } @else {
    display: -webkit-box;
    -webkit-line-clamp: $lines;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}
```

## 实施优先级计划

### 第一阶段：基础框架搭建 (预计: 2-3天)
**目标**: 修复项目配置，创建基础结构
1. 修复uni-app配置文件 (`pages.json`, `manifest.json`)
2. 修复前端测试配置 (Jest + Vue Test Utils)
3. 创建基础目录结构
4. 配置Pinia状态管理
5. 配置Axios API层
6. 设置SCSS样式系统
7. 创建基础组件 (`BaseButton`, `BaseCard`等)

### 第二阶段：核心功能开发 (预计: 3-4天)
**目标**: 实现商品浏览和购物车基础功能
1. 首页开发 (Banner轮播 + 商品推荐)
2. 商品列表页 (筛选、排序、分页)
3. 商品详情页 (规格选择、加入购物车)
4. 购物车页面 (商品管理、价格计算)
5. 微信登录集成
6. 页面路由配置

### 第三阶段：订单流程实现 (预计: 3-4天)
**目标**: 完成从购物车到支付的完整流程
1. 订单确认页 (地址选择、优惠券应用)
2. 地址管理功能 (增删改查)
3. 支付页面集成 (微信支付)
4. 订单列表页 (状态筛选、详情查看)
5. 订单状态追踪

### 第四阶段：用户体验优化 (预计: 2-3天)
**目标**: 完善用户中心，优化交互体验
1. 个人中心页面
2. 优惠券管理
3. 搜索功能优化
4. 图片懒加载
5. 骨架屏加载效果
6. 错误边界处理

### 第五阶段：性能优化和测试 (预计: 2-3天)
**目标**: 提升性能，完善测试
1. 代码分包优化
2. 图片压缩和CDN
3. API请求缓存
4. 组件单元测试
5. E2E测试用例
6. 性能监控接入

## 技术风险与应对措施

### 已知问题
1. **测试配置问题**: `@vue/test-utils`路径错误
   - **解决方案**: 检查jest配置，修复模块路径映射

2. **uni-app配置缺失**: 缺少`pages.json`等核心文件
   - **解决方案**: 基于uni-app模板创建标准配置文件

3. **微信小程序兼容性**: Vant组件在微信小程序中的适配
   - **解决方案**: 使用`@vant/weapp`专门的小程序版本

4. **TypeScript类型定义**: 与后端共享类型的同步
   - **解决方案**: 完善共享类型库，建立类型同步机制

### 性能优化点
1. **图片懒加载**: 使用uni-app的`lazy-load`属性
2. **组件懒加载**: 路由级别的代码分割
3. **API请求缓存**: 高频接口添加缓存策略
4. **状态持久化**: 购物车等数据本地存储
5. **预加载策略**: 关键页面数据预加载

## 验收标准

### 功能完整性
- [ ] 首页Banner和商品推荐正常展示
- [ ] 商品列表筛选、排序功能正常
- [ ] 商品详情页规格选择和加入购物车正常
- [ ] 购物车商品增删改查功能正常
- [ ] 微信登录和用户信息获取正常
- [ ] 订单创建、支付流程完整
- [ ] 地址管理和优惠券功能正常

### 用户体验
- [ ] 页面加载速度 < 2秒 (首屏)
- [ ] 交互响应时间 < 200ms
- [ ] 错误提示清晰友好
- [ ] 移动端适配良好
- [ ] 微信小程序API调用正常

### 代码质量
- [ ] TypeScript类型覆盖率 > 90%
- [ ] 组件单元测试覆盖率 > 80%
- [ ] 无ESLint错误
- [ ] 代码结构符合设计规范
- [ ] API错误处理完善

### 兼容性
- [ ] 微信小程序版本正常运行
- [ ] H5版本基本功能可用
- [ ] iOS/Android平台表现一致
- [ ] 主流微信版本兼容

## 后续演进路线

### 短期优化 (1个月内)
1. 引入状态持久化 (localStorage)
2. 添加性能监控 (埋点统计)
3. 优化图片加载策略
4. 增加PWA支持 (H5版本)

### 中期扩展 (1-3个月)
1. 多店铺支持架构
2. 会员积分系统
3. 拼团/秒杀功能
4. 客服聊天系统
5. 数据统计分析后台

### 长期规划 (3-6个月)
1. 微前端架构改造
2. 多平台发布 (支付宝小程序、抖音小程序)
3. 国际化支持
4. 自定义主题系统
5. 插件化架构

## 设计决策说明

### 为什么选择混合渐进式架构？
1. **平衡开发效率和质量**: 初期使用简单结构快速验证，后期逐步优化
2. **降低技术风险**: 避免过度设计，根据实际需求演进架构
3. **团队友好**: 新成员容易上手，逐步学习复杂概念
4. **维护成本可控**: 技术债务有计划地偿还

### 为什么选择Vant而非其他UI库？
1. **微信小程序原生支持**: `@vant/weapp`专门为小程序优化
2. **设计风格合适**: Vant的简约风格适合电商应用
3. **社区活跃**: 文档完善，问题解决资源丰富
4. **与Vue 3兼容**: 官方支持Vue 3版本

### TypeScript严格程度选择
采用**严格模式**但允许必要的`any`类型，平衡类型安全和开发效率：
- 核心业务逻辑严格类型
- 第三方库接口适当放宽
- UI组件Props/Events完整类型
- API请求/响应完整类型

### 状态管理边界划分
明确Store和组件状态的职责边界：
- **Store管理**: 跨页面共享、持久化、业务逻辑复杂的数据
- **组件状态管理**: 表单输入、UI交互状态、临时数据
- **Props传递**: 父子组件数据流
- **Event通信**: 兄弟组件/非直接关系组件通信

---

**设计审核**:
- [x] 无TBD/TODO占位符
- [x] 内部一致性检查通过
- [x] 范围适中，适合单个实施计划
- [x] 无重大歧义，需求明确
- [x] 技术方案可行，风险评估充分

**下一步**: 用户审阅此spec，确认后进入实施计划阶段。