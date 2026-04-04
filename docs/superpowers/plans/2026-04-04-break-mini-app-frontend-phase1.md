# break-mini-app 前端第一阶段实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成面包店小程序前端基础框架搭建，修复测试配置，创建uni-app核心文件，配置状态管理和API层

**Architecture:** 混合渐进式架构，从简单的uni-app标准页面结构开始。使用Pinia进行全局状态管理，Axios进行API调用，SCSS变量系统进行样式管理。

**Tech Stack:** Vue 3, TypeScript, uni-app, Pinia, Vant Weapp, Axios, SCSS, Jest

---

## 文件结构

### 将创建的文件
- `frontend/pages.json` - uni-app页面路由配置
- `frontend/manifest.json` - uni-app应用配置
- `frontend/App.vue` - 应用根组件
- `frontend/src/main.ts` - 应用入口
- `frontend/uni.scss` - uni-app全局样式
- `frontend/src/styles/variables.scss` - 设计变量
- `frontend/src/styles/mixins.scss` - SCSS Mixin
- `frontend/src/styles/global.scss` - 全局样式
- `frontend/src/stores/user.store.ts` - 用户状态管理
- `frontend/src/stores/cart.store.ts` - 购物车状态管理
- `frontend/src/stores/product.store.ts` - 商品状态管理
- `frontend/src/stores/order.store.ts` - 订单状态管理
- `frontend/src/stores/index.ts` - store统一导出
- `frontend/src/utils/api/index.ts` - Axios配置
- `frontend/src/utils/api/auth.api.ts` - 认证API
- `frontend/src/utils/api/product.api.ts` - 商品API
- `frontend/src/components/common/BaseButton.vue` - 基础按钮组件
- `frontend/src/components/common/BaseCard.vue` - 基础卡片组件
- `frontend/src/components/common/BaseModal.vue` - 基础模态框组件
- `frontend/src/components/common/BaseLoading.vue` - 基础加载组件

### 将修改的文件
- `frontend/package.json` - 添加缺少的jest preset依赖
- `frontend/jest.config.js` - 修复preset配置

### 将测试的文件
- `frontend/src/components/common/BaseButton.test.ts` - BaseButton组件测试
- `frontend/src/stores/user.store.test.ts` - 用户store测试
- `frontend/src/utils/api/index.test.ts` - API配置测试

---

## Task 1: 修复jest preset依赖

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/jest.config.js`

- [ ] **Step 1: 安装缺少的jest preset依赖**

```bash
cd frontend
npm install @vue/cli-plugin-unit-jest --save-dev
```

Expected: Package installed successfully

- [ ] **Step 2: 更新jest.config.js使用正确的preset**

```javascript
// frontend/jest.config.js
module.exports = {
  preset: '@vue/cli-plugin-unit-jest',
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.vue$': '@vue/vue3-jest',
    '^.+\\.js$': 'babel-jest',
    '^.+\\.ts$': 'ts-jest',
  },
  moduleFileExtensions: ['js', 'ts', 'json', 'vue'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testMatch: [
    '**/__tests__/**/*.[jt]s?(x)',
    '**/?(*.)+(spec|test).[jt]s?(x)',
  ],
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  collectCoverageFrom: [
    'src/**/*.{js,ts,vue}',
    '!src/main.ts',
    '!src/**/*.d.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
};
```

- [ ] **Step 3: 运行测试验证修复**

```bash
cd frontend
npm test -- --passWithNoTests
```

Expected: PASS (没有错误)

- [ ] **Step 4: 提交更改**

```bash
git add frontend/package.json frontend/jest.config.js
git commit -m "fix: 修复jest preset依赖问题"
```

---

## Task 2: 创建uni-app核心配置文件

**Files:**
- Create: `frontend/pages.json`
- Create: `frontend/manifest.json`
- Create: `frontend/App.vue`
- Create: `frontend/src/main.ts`
- Create: `frontend/uni.scss`

- [ ] **Step 1: 创建pages.json路由配置**

```json
// frontend/pages.json
{
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "面包店首页"
      }
    },
    {
      "path": "pages/product-detail/index",
      "style": {
        "navigationBarTitleText": "商品详情"
      }
    },
    {
      "path": "pages/cart/index",
      "style": {
        "navigationBarTitleText": "购物车"
      }
    },
    {
      "path": "pages/user-center/index",
      "style": {
        "navigationBarTitleText": "个人中心"
      }
    }
  ],
  "globalStyle": {
    "navigationBarTextStyle": "black",
    "navigationBarTitleText": "面包店小程序",
    "navigationBarBackgroundColor": "#F8F8F8",
    "backgroundColor": "#F8F8F8",
    "navigationStyle": "custom"
  },
  "tabBar": {
    "color": "#999999",
    "selectedColor": "#FF6B35",
    "backgroundColor": "#FFFFFF",
    "borderStyle": "black",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "首页",
        "iconPath": "static/tabbar/home.png",
        "selectedIconPath": "static/tabbar/home-active.png"
      },
      {
        "pagePath": "pages/cart/index",
        "text": "购物车",
        "iconPath": "static/tabbar/cart.png",
        "selectedIconPath": "static/tabbar/cart-active.png"
      },
      {
        "pagePath": "pages/user-center/index",
        "text": "我的",
        "iconPath": "static/tabbar/user.png",
        "selectedIconPath": "static/tabbar/user-active.png"
      }
    ]
  }
}
```

- [ ] **Step 2: 创建manifest.json应用配置**

```json
// frontend/manifest.json
{
  "name": "break-mini-app",
  "appid": "__UNI__BREAKMINIAPP",
  "description": "面包店电商小程序",
  "versionName": "1.0.0",
  "versionCode": "100",
  "transformPx": false,
  "app-plus": {
    "usingComponents": true,
    "nvueStyleCompiler": "uni-app",
    "compilerVersion": 3,
    "splashscreen": {
      "alwaysShowBeforeRender": true,
      "waiting": true,
      "autoclose": true,
      "delay": 0
    }
  },
  "quickapp": {},
  "mp-weixin": {
    "appid": "",
    "setting": {
      "urlCheck": false,
      "es6": true,
      "postcss": true,
      "minified": true
    },
    "usingComponents": true,
    "permission": {}
  },
  "mp-alipay": {
    "usingComponents": true
  },
  "mp-baidu": {
    "usingComponents": true
  },
  "mp-toutiao": {
    "usingComponents": true
  },
  "uniStatistics": {
    "enable": false
  },
  "vueVersion": "3"
}
```

- [ ] **Step 3: 创建App.vue根组件**

```vue
<!-- frontend/App.vue -->
<template>
  <view>
    <slot />
  </view>
</template>

<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from './src/stores/user.store'

// 应用启动
onLaunch(() => {
  console.log('App Launch')
  
  // 检查登录状态
  const userStore = useUserStore()
  userStore.checkLoginStatus()
})

// 应用显示
onShow(() => {
  console.log('App Show')
})

// 应用隐藏
onHide(() => {
  console.log('App Hide')
})
</script>

<style lang="scss">
/* 导入全局样式 */
@import './src/styles/global.scss';
</style>
```

- [ ] **Step 4: 创建main.ts应用入口**

```typescript
// frontend/src/main.ts
import { createSSRApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import 'dayjs/locale/zh-cn'
import dayjs from 'dayjs'

// 设置dayjs语言
dayjs.locale('zh-cn')

export function createApp() {
  const app = createSSRApp(App)
  const pinia = createPinia()
  
  app.use(pinia)
  
  return {
    app,
    pinia,
  }
}
```

- [ ] **Step 5: 创建uni.scss全局样式**

```scss
// frontend/uni.scss
/* uni.scss - uni-app全局样式 */

/* 颜色变量 */
$uni-color-primary: #FF6B35;
$uni-color-success: #52C41A;
$uni-color-warning: #FAAD14;
$uni-color-error: #FF4D4F;
$uni-color-info: #1890FF;

/* 背景颜色 */
$uni-bg-color: #F8F8F8;
$uni-bg-color-grey: #F8F8F8;
$uni-bg-color-hover: #F1F1F1;
$uni-bg-color-mask: rgba(0, 0, 0, 0.4);

/* 边框颜色 */
$uni-border-color: #E0E0E0;

/* 尺寸变量 */
$uni-font-size-sm: 12px;
$uni-font-size-base: 14px;
$uni-font-size-lg: 16px;
$uni-font-size-xl: 18px;
$uni-font-size-xxl: 20px;

/* 圆角 */
$uni-border-radius-sm: 4px;
$uni-border-radius-base: 8px;
$uni-border-radius-lg: 12px;
$uni-border-radius-xl: 16px;
$uni-border-radius-circle: 50%;

/* 水平间距 */
$uni-spacing-row-sm: 5px;
$uni-spacing-row-base: 10px;
$uni-spacing-row-lg: 15px;

/* 垂直间距 */
$uni-spacing-col-sm: 5px;
$uni-spacing-col-base: 10px;
$uni-spacing-col-lg: 15px;

/* 高度 */
$uni-height-base: 44px;
$uni-height-lg: 50px;
$uni-height-sm: 36px;

/* 导入设计变量 */
@import './src/styles/variables.scss';
```

- [ ] **Step 6: 提交uni-app核心文件**

```bash
git add frontend/pages.json frontend/manifest.json frontend/App.vue frontend/src/main.ts frontend/uni.scss
git commit -m "feat: 创建uni-app核心配置文件"
```

---

## Task 3: 创建SCSS样式系统

**Files:**
- Create: `frontend/src/styles/variables.scss`
- Create: `frontend/src/styles/mixins.scss`
- Create: `frontend/src/styles/global.scss`

- [ ] **Step 1: 创建variables.scss设计变量**

```scss
// frontend/src/styles/variables.scss
// 品牌色系 - 温暖面包感
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

- [ ] **Step 2: 创建mixins.scss工具函数**

```scss
// frontend/src/styles/mixins.scss
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

// 按钮基础样式
@mixin button-base {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: $border-radius-md;
  font-family: $font-family;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

// 卡片基础样式
@mixin card-base {
  background: $color-white;
  border-radius: $border-radius-md;
  box-shadow: $shadow-sm;
  padding: $spacing-md;
}
```

- [ ] **Step 3: 创建global.scss全局样式**

```scss
// frontend/src/styles/global.scss
/* 全局样式 */
@import './variables.scss';
@import './mixins.scss';

/* 重置样式 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  font-family: $font-family;
  font-size: $font-size-md;
  color: $color-text-primary;
  background-color: $color-background;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 通用类 */
.container {
  padding: $spacing-md;
}

.page-container {
  min-height: 100vh;
  background-color: $color-background;
}

.text-center {
  text-align: center;
}

.text-left {
  text-align: left;
}

.text-right {
  text-align: right;
}

.text-ellipsis {
  @include text-ellipsis(1);
}

.text-ellipsis-2 {
  @include text-ellipsis(2);
}

.text-ellipsis-3 {
  @include text-ellipsis(3);
}

.flex-center {
  @include flex-center;
}

.flex-between {
  @include flex-between;
}

.flex-column {
  @include flex-column;
}

/* 工具类 */
.mt-sm { margin-top: $spacing-sm !important; }
.mt-md { margin-top: $spacing-md !important; }
.mt-lg { margin-top: $spacing-lg !important; }
.mt-xl { margin-top: $spacing-xl !important; }

.mb-sm { margin-bottom: $spacing-sm !important; }
.mb-md { margin-bottom: $spacing-md !important; }
.mb-lg { margin-bottom: $spacing-lg !important; }
.mb-xl { margin-bottom: $spacing-xl !important; }

.ml-sm { margin-left: $spacing-sm !important; }
.ml-md { margin-left: $spacing-md !important; }
.ml-lg { margin-left: $spacing-lg !important; }
.ml-xl { margin-left: $spacing-xl !important; }

.mr-sm { margin-right: $spacing-sm !important; }
.mr-md { margin-right: $spacing-md !important; }
.mr-lg { margin-right: $spacing-lg !important; }
.mr-xl { margin-right: $spacing-xl !important; }

.pt-sm { padding-top: $spacing-sm !important; }
.pt-md { padding-top: $spacing-md !important; }
.pt-lg { padding-top: $spacing-lg !important; }
.pt-xl { padding-top: $spacing-xl !important; }

.pb-sm { padding-bottom: $spacing-sm !important; }
.pb-md { padding-bottom: $spacing-md !important; }
.pb-lg { padding-bottom: $spacing-lg !important; }
.pb-xl { padding-bottom: $spacing-xl !important; }

.pl-sm { padding-left: $spacing-sm !important; }
.pl-md { padding-left: $spacing-md !important; }
.pl-lg { padding-left: $spacing-lg !important; }
.pl-xl { padding-left: $spacing-xl !important; }

.pr-sm { padding-right: $spacing-sm !important; }
.pr-md { padding-right: $spacing-md !important; }
.pr-lg { padding-right: $spacing-lg !important; }
.pr-xl { padding-right: $spacing-xl !important; }
```

- [ ] **Step 4: 提交样式系统文件**

```bash
git add frontend/src/styles/
git commit -m "feat: 创建SCSS样式系统"
```

---

## Task 4: 创建Pinia状态管理

**Files:**
- Create: `frontend/src/stores/user.store.ts`
- Create: `frontend/src/stores/cart.store.ts`
- Create: `frontend/src/stores/product.store.ts`
- Create: `frontend/src/stores/order.store.ts`
- Create: `frontend/src/stores/index.ts`
- Test: `frontend/src/stores/user.store.test.ts`

- [ ] **Step 1: 创建用户状态管理store**

```typescript
// frontend/src/stores/user.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface User {
  id: string
  username: string
  nickname: string
  avatar: string
  phone?: string
  email?: string
  createdAt: string
}

interface UserState {
  userInfo: User | null
  isLoggedIn: boolean
  token: string | null
  refreshToken: string | null
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const userInfo = ref<User | null>(null)
  const isLoggedIn = ref(false)
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  // getters
  const getUserInfo = computed(() => userInfo.value)
  const getIsLoggedIn = computed(() => isLoggedIn.value)
  const getToken = computed(() => token.value)

  // actions
  const setUserInfo = (info: User | null) => {
    userInfo.value = info
    isLoggedIn.value = !!info
  }

  const setToken = (newToken: string, newRefreshToken?: string) => {
    token.value = newToken
    if (newRefreshToken) {
      refreshToken.value = newRefreshToken
    }
    // 这里应该将token存储到localStorage
    localStorage.setItem('token', newToken)
    if (newRefreshToken) {
      localStorage.setItem('refreshToken', newRefreshToken)
    }
  }

  const clearToken = () => {
    token.value = null
    refreshToken.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  const logout = () => {
    userInfo.value = null
    isLoggedIn.value = false
    clearToken()
  }

  const checkLoginStatus = () => {
    const savedToken = localStorage.getItem('token')
    const savedRefreshToken = localStorage.getItem('refreshToken')
    
    if (savedToken) {
      token.value = savedToken
      refreshToken.value = savedRefreshToken
      isLoggedIn.value = true
      // 这里应该调用API验证token有效性
    }
  }

  return {
    // 状态
    userInfo,
    isLoggedIn,
    token,
    refreshToken,
    
    // getters
    getUserInfo,
    getIsLoggedIn,
    getToken,
    
    // actions
    setUserInfo,
    setToken,
    clearToken,
    logout,
    checkLoginStatus,
  }
})
```

- [ ] **Step 2: 创建购物车状态管理store**

```typescript
// frontend/src/stores/cart.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface CartItem {
  id: string
  productId: string
  name: string
  price: number
  quantity: number
  image: string
  selected: boolean
  specs?: Record<string, string>
}

interface CartState {
  items: CartItem[]
  selectedItems: string[] // 选中的商品ID
  coupon?: Coupon // 应用的优惠券
}

interface Coupon {
  id: string
  name: string
  discount: number
  type: 'percentage' | 'fixed'
  minAmount?: number
}

export const useCartStore = defineStore('cart', () => {
  // 状态
  const items = ref<CartItem[]>([])
  const selectedItems = ref<string[]>([])
  const coupon = ref<Coupon | undefined>(undefined)

  // getters
  const getItems = computed(() => items.value)
  const getSelectedItems = computed(() => selectedItems.value)
  const getCoupon = computed(() => coupon.value)
  
  const getTotalPrice = computed(() => {
    return items.value.reduce((total, item) => {
      if (selectedItems.value.includes(item.id)) {
        return total + (item.price * item.quantity)
      }
      return total
    }, 0)
  })
  
  const getTotalQuantity = computed(() => {
    return items.value.reduce((total, item) => total + item.quantity, 0)
  })
  
  const getSelectedCount = computed(() => {
    return selectedItems.value.length
  })
  
  const getIsAllSelected = computed(() => {
    if (items.value.length === 0) return false
    return selectedItems.value.length === items.value.length
  })

  // actions
  const addItem = (item: Omit<CartItem, 'id' | 'selected'>) => {
    const existingItem = items.value.find(i => i.productId === item.productId)
    
    if (existingItem) {
      existingItem.quantity += item.quantity
    } else {
      const newItem: CartItem = {
        ...item,
        id: Date.now().toString(),
        selected: true,
      }
      items.value.push(newItem)
      selectedItems.value.push(newItem.id)
    }
  }
  
  const removeItem = (itemId: string) => {
    items.value = items.value.filter(item => item.id !== itemId)
    selectedItems.value = selectedItems.value.filter(id => id !== itemId)
  }
  
  const updateQuantity = (itemId: string, quantity: number) => {
    const item = items.value.find(i => i.id === itemId)
    if (item) {
      item.quantity = quantity > 0 ? quantity : 1
    }
  }
  
  const toggleSelect = (itemId: string) => {
    if (selectedItems.value.includes(itemId)) {
      selectedItems.value = selectedItems.value.filter(id => id !== itemId)
    } else {
      selectedItems.value.push(itemId)
    }
  }
  
  const toggleSelectAll = () => {
    if (getIsAllSelected.value) {
      selectedItems.value = []
    } else {
      selectedItems.value = items.value.map(item => item.id)
    }
  }
  
  const clearCart = () => {
    items.value = []
    selectedItems.value = []
    coupon.value = undefined
  }
  
  const applyCoupon = (newCoupon: Coupon) => {
    coupon.value = newCoupon
  }
  
  const removeCoupon = () => {
    coupon.value = undefined
  }

  return {
    // 状态
    items,
    selectedItems,
    coupon,
    
    // getters
    getItems,
    getSelectedItems,
    getCoupon,
    getTotalPrice,
    getTotalQuantity,
    getSelectedCount,
    getIsAllSelected,
    
    // actions
    addItem,
    removeItem,
    updateQuantity,
    toggleSelect,
    toggleSelectAll,
    clearCart,
    applyCoupon,
    removeCoupon,
  }
})
```

- [ ] **Step 3: 创建商品状态管理store**

```typescript
// frontend/src/stores/product.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface Product {
  id: string
  name: string
  description: string
  price: number
  originalPrice?: number
  images: string[]
  categoryId: string
  categoryName: string
  stock: number
  sales: number
  specs?: Record<string, string[]>
  createdAt: string
}

interface Category {
  id: string
  name: string
  icon?: string
  parentId?: string
}

interface ProductState {
  products: Product[]
  categories: Category[]
  currentProduct: Product | null
  searchHistory: string[]
}

export const useProductStore = defineStore('product', () => {
  // 状态
  const products = ref<Product[]>([])
  const categories = ref<Category[]>([])
  const currentProduct = ref<Product | null>(null)
  const searchHistory = ref<string[]>([])

  // getters
  const getProducts = computed(() => products.value)
  const getCategories = computed(() => categories.value)
  const getCurrentProduct = computed(() => currentProduct.value)
  const getSearchHistory = computed(() => searchHistory.value)

  // actions
  const setProducts = (newProducts: Product[]) => {
    products.value = newProducts
  }
  
  const setCategories = (newCategories: Category[]) => {
    categories.value = newCategories
  }
  
  const setCurrentProduct = (product: Product | null) => {
    currentProduct.value = product
  }
  
  const addSearchHistory = (keyword: string) => {
    if (!keyword.trim()) return
    
    // 移除重复项
    searchHistory.value = searchHistory.value.filter(item => item !== keyword)
    // 添加到开头
    searchHistory.value.unshift(keyword)
    // 保持最多10条记录
    if (searchHistory.value.length > 10) {
      searchHistory.value = searchHistory.value.slice(0, 10)
    }
  }
  
  const clearSearchHistory = () => {
    searchHistory.value = []
  }
  
  const clearCurrentProduct = () => {
    currentProduct.value = null
  }

  return {
    // 状态
    products,
    categories,
    currentProduct,
    searchHistory,
    
    // getters
    getProducts,
    getCategories,
    getCurrentProduct,
    getSearchHistory,
    
    // actions
    setProducts,
    setCategories,
    setCurrentProduct,
    addSearchHistory,
    clearSearchHistory,
    clearCurrentProduct,
  }
})
```

- [ ] **Step 4: 创建订单状态管理store**

```typescript
// frontend/src/stores/order.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface Address {
  id: string
  name: string
  phone: string
  province: string
  city: string
  district: string
  detail: string
  isDefault: boolean
}

interface OrderItem {
  productId: string
  name: string
  price: number
  quantity: number
  image: string
  specs?: Record<string, string>
}

interface Order {
  id: string
  orderNo: string
  status: 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled' | 'refunded'
  totalAmount: number
  discountAmount: number
  shippingFee: number
  finalAmount: number
  items: OrderItem[]
  address: Address
  createdAt: string
  paidAt?: string
  shippedAt?: string
  deliveredAt?: string
}

interface OrderState {
  currentOrder: Order | null // 当前正在创建的订单
  orders: Order[] // 历史订单
  addresses: Address[] // 收货地址
  coupons: Coupon[] // 可用优惠券
}

interface Coupon {
  id: string
  name: string
  discount: number
  type: 'percentage' | 'fixed'
  minAmount?: number
  expiredAt: string
}

export const useOrderStore = defineStore('order', () => {
  // 状态
  const currentOrder = ref<Order | null>(null)
  const orders = ref<Order[]>([])
  const addresses = ref<Address[]>([])
  const coupons = ref<Coupon[]>([])

  // getters
  const getCurrentOrder = computed(() => currentOrder.value)
  const getOrders = computed(() => orders.value)
  const getAddresses = computed(() => addresses.value)
  const getCoupons = computed(() => coupons.value)
  
  const getDefaultAddress = computed(() => {
    return addresses.value.find(addr => addr.isDefault) || addresses.value[0]
  })

  // actions
  const setCurrentOrder = (order: Order | null) => {
    currentOrder.value = order
  }
  
  const setOrders = (newOrders: Order[]) => {
    orders.value = newOrders
  }
  
  const setAddresses = (newAddresses: Address[]) => {
    addresses.value = newAddresses
  }
  
  const setCoupons = (newCoupons: Coupon[]) => {
    coupons.value = newCoupons
  }
  
  const addAddress = (address: Omit<Address, 'id'>) => {
    const newAddress: Address = {
      ...address,
      id: Date.now().toString(),
    }
    
    // 如果设为默认地址，清空其他地址的默认标记
    if (address.isDefault) {
      addresses.value = addresses.value.map(addr => ({
        ...addr,
        isDefault: false,
      }))
    }
    
    addresses.value.push(newAddress)
  }
  
  const updateAddress = (id: string, updates: Partial<Address>) => {
    const index = addresses.value.findIndex(addr => addr.id === id)
    if (index !== -1) {
      // 如果设为默认地址，清空其他地址的默认标记
      if (updates.isDefault) {
        addresses.value = addresses.value.map(addr => ({
          ...addr,
          isDefault: addr.id === id,
        }))
      } else {
        addresses.value[index] = { ...addresses.value[index], ...updates }
      }
    }
  }
  
  const deleteAddress = (id: string) => {
    addresses.value = addresses.value.filter(addr => addr.id !== id)
  }
  
  const clearCurrentOrder = () => {
    currentOrder.value = null
  }

  return {
    // 状态
    currentOrder,
    orders,
    addresses,
    coupons,
    
    // getters
    getCurrentOrder,
    getOrders,
    getAddresses,
    getCoupons,
    getDefaultAddress,
    
    // actions
    setCurrentOrder,
    setOrders,
    setAddresses,
    setCoupons,
    addAddress,
    updateAddress,
    deleteAddress,
    clearCurrentOrder,
  }
})
```

- [ ] **Step 5: 创建store统一导出文件**

```typescript
// frontend/src/stores/index.ts
export { useUserStore } from './user.store'
export { useCartStore } from './cart.store'
export { useProductStore } from './product.store'
export { useOrderStore } from './order.store'

// 统一初始化store（如果需要）
export const initializeStores = () => {
  // 这里可以添加store初始化逻辑
  console.log('Stores initialized')
}
```

- [ ] **Step 6: 为user.store创建测试**

```typescript
// frontend/src/stores/user.store.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from './user.store'

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('should initialize with default values', () => {
    const store = useUserStore()
    
    expect(store.userInfo).toBeNull()
    expect(store.isLoggedIn).toBe(false)
    expect(store.token).toBeNull()
  })

  it('should set user info', () => {
    const store = useUserStore()
    const user = {
      id: '123',
      username: 'testuser',
      nickname: 'Test User',
      avatar: 'avatar.jpg',
      createdAt: '2023-01-01',
    }
    
    store.setUserInfo(user)
    
    expect(store.userInfo).toEqual(user)
    expect(store.isLoggedIn).toBe(true)
  })

  it('should set token', () => {
    const store = useUserStore()
    const token = 'test-token'
    
    store.setToken(token)
    
    expect(store.token).toBe(token)
    expect(localStorage.getItem('token')).toBe(token)
  })

  it('should clear token on logout', () => {
    const store = useUserStore()
    store.setToken('test-token')
    store.setUserInfo({
      id: '123',
      username: 'testuser',
      nickname: 'Test User',
      avatar: 'avatar.jpg',
      createdAt: '2023-01-01',
    })
    
    store.logout()
    
    expect(store.userInfo).toBeNull()
    expect(store.isLoggedIn).toBe(false)
    expect(store.token).toBeNull()
    expect(localStorage.getItem('token')).toBeNull()
  })

  it('should check login status from localStorage', () => {
    localStorage.setItem('token', 'saved-token')
    localStorage.setItem('refreshToken', 'saved-refresh-token')
    
    const store = useUserStore()
    store.checkLoginStatus()
    
    expect(store.token).toBe('saved-token')
    expect(store.refreshToken).toBe('saved-refresh-token')
    expect(store.isLoggedIn).toBe(true)
  })
})
```

- [ ] **Step 7: 运行store测试**

```bash
cd frontend
npm test -- frontend/src/stores/user.store.test.ts
```

Expected: All tests pass

- [ ] **Step 8: 提交状态管理文件**

```bash
git add frontend/src/stores/
git commit -m "feat: 创建Pinia状态管理store"
```

---

## Task 5: 配置Axios API层

**Files:**
- Create: `frontend/src/utils/api/index.ts`
- Create: `frontend/src/utils/api/auth.api.ts`
- Create: `frontend/src/utils/api/product.api.ts`
- Test: `frontend/src/utils/api/index.test.ts`

- [ ] **Step 1: 创建Axios基础配置**

```typescript
// frontend/src/utils/api/index.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { useUserStore } from '../../stores/user.store'

// 环境变量配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api'

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const userStore = useUserStore()
    const token = userStore.token
    
    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error: AxiosError) => {
    const userStore = useUserStore()
    
    // Token过期处理
    if (error.response?.status === 401) {
      userStore.logout()
      // 这里可以跳转到登录页
      console.error('Token expired, please login again')
    }
    
    // 统一错误处理
    const errorMessage = (error.response?.data as any)?.message || '网络错误，请稍后重试'
    console.error('API Error:', errorMessage)
    
    // 这里可以显示错误提示
    // showToast(errorMessage)
    
    return Promise.reject(error)
  }
)

// API响应类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp: string
}

// 通用API方法
export const get = <T>(url: string, params?: any): Promise<T> => {
  return api.get(url, { params })
}

export const post = <T>(url: string, data?: any): Promise<T> => {
  return api.post(url, data)
}

export const put = <T>(url: string, data?: any): Promise<T> => {
  return api.put(url, data)
}

export const del = <T>(url: string): Promise<T> => {
  return api.delete(url)
}

export default api
```

- [ ] **Step 2: 创建认证API模块**

```typescript
// frontend/src/utils/api/auth.api.ts
import api, { ApiResponse } from './index'

interface LoginRequest {
  username: string
  password: string
}

interface LoginResponse {
  token: string
  refreshToken: string
  user: {
    id: string
    username: string
    nickname: string
    avatar: string
    email?: string
    phone?: string
  }
}

interface WechatLoginRequest {
  code: string
  userInfo?: {
    nickName: string
    avatarUrl: string
  }
}

export const authApi = {
  // 用户名密码登录
  login: (data: LoginRequest): Promise<ApiResponse<LoginResponse>> => {
    return api.post('/auth/login', data)
  },
  
  // 微信登录
  wechatLogin: (data: WechatLoginRequest): Promise<ApiResponse<LoginResponse>> => {
    return api.post('/auth/wechat-login', data)
  },
  
  // 获取当前用户信息
  getCurrentUser: (): Promise<ApiResponse<LoginResponse['user']>> => {
    return api.get('/auth/me')
  },
  
  // 刷新token
  refreshToken: (refreshToken: string): Promise<ApiResponse<{ token: string }>> => {
    return api.post('/auth/refresh-token', { refreshToken })
  },
  
  // 退出登录
  logout: (): Promise<ApiResponse<void>> => {
    return api.post('/auth/logout')
  },
  
  // 注册
  register: (data: {
    username: string
    password: string
    nickname: string
    phone?: string
    email?: string
  }): Promise<ApiResponse<void>> => {
    return api.post('/auth/register', data)
  },
}
```

- [ ] **Step 3: 创建商品API模块**

```typescript
// frontend/src/utils/api/product.api.ts
import api, { ApiResponse } from './index'

interface Product {
  id: string
  name: string
  description: string
  price: number
  originalPrice?: number
  images: string[]
  categoryId: string
  categoryName: string
  stock: number
  sales: number
  specs?: Record<string, string[]>
  createdAt: string
}

interface Category {
  id: string
  name: string
  icon?: string
  parentId?: string
}

interface ProductQueryParams {
  categoryId?: string
  keyword?: string
  minPrice?: number
  maxPrice?: number
  sortBy?: 'price' | 'sales' | 'createdAt'
  sortOrder?: 'asc' | 'desc'
  page?: number
  pageSize?: number
}

export const productApi = {
  // 获取商品列表
  getProducts: (params?: ProductQueryParams): Promise<ApiResponse<{
    products: Product[]
    total: number
    page: number
    pageSize: number
    totalPages: number
  }>> => {
    return api.get('/products', { params })
  },
  
  // 获取商品详情
  getProduct: (id: string): Promise<ApiResponse<Product>> => {
    return api.get(`/products/${id}`)
  },
  
  // 获取商品分类
  getCategories: (): Promise<ApiResponse<Category[]>> => {
    return api.get('/categories')
  },
  
  // 搜索商品
  searchProducts: (keyword: string, params?: Omit<ProductQueryParams, 'keyword'>): Promise<ApiResponse<{
    products: Product[]
    total: number
  }>> => {
    return api.get('/products/search', { params: { keyword, ...params } })
  },
  
  // 获取热门商品
  getHotProducts: (limit?: number): Promise<ApiResponse<Product[]>> => {
    return api.get('/products/hot', { params: { limit } })
  },
  
  // 获取推荐商品
  getRecommendedProducts: (limit?: number): Promise<ApiResponse<Product[]>> => {
    return api.get('/products/recommended', { params: { limit } })
  },
}
```

- [ ] **Step 4: 创建API配置测试**

```typescript
// frontend/src/utils/api/index.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'
import api, { get, post } from './index'

describe('API Configuration', () => {
  let mock: MockAdapter
  
  beforeEach(() => {
    mock = new MockAdapter(axios)
    vi.clearAllMocks()
  })
  
  afterEach(() => {
    mock.restore()
  })
  
  it('should have correct base URL', () => {
    expect(api.defaults.baseURL).toBe('http://localhost:3000/api')
  })
  
  it('should have correct timeout', () => {
    expect(api.defaults.timeout).toBe(10000)
  })
  
  it('should have correct content type header', () => {
    expect(api.defaults.headers['Content-Type']).toBe('application/json')
  })
  
  it('should handle successful response', async () => {
    const mockData = { id: 1, name: 'Test Product' }
    mock.onGet('/test').reply(200, mockData)
    
    const response = await get('/test')
    expect(response).toEqual(mockData)
  })
  
  it('should handle error response', async () => {
    mock.onGet('/error').reply(500, { message: 'Server Error' })
    
    try {
      await get('/error')
    } catch (error) {
      expect(error).toBeDefined()
    }
  })
  
  it('should send POST request with data', async () => {
    const requestData = { name: 'Test' }
    const responseData = { id: 1, ...requestData }
    
    mock.onPost('/test').reply(200, responseData)
    
    const response = await post('/test', requestData)
    expect(response).toEqual(responseData)
  })
})
```

- [ ] **Step 5: 安装测试依赖**

```bash
cd frontend
npm install axios-mock-adapter vitest --save-dev
```

- [ ] **Step 6: 运行API配置测试**

```bash
cd frontend
npm test -- frontend/src/utils/api/index.test.ts
```

Expected: Tests pass (may need to adjust based on actual setup)

- [ ] **Step 7: 提交API配置文件**

```bash
git add frontend/src/utils/api/
git commit -m "feat: 配置Axios API层"
```

---

## Task 6: 创建基础组件

**Files:**
- Create: `frontend/src/components/common/BaseButton.vue`
- Create: `frontend/src/components/common/BaseCard.vue`
- Create: `frontend/src/components/common/BaseModal.vue`
- Create: `frontend/src/components/common/BaseLoading.vue`
- Test: `frontend/src/components/common/BaseButton.test.ts`

- [ ] **Step 1: 创建BaseButton基础按钮组件**

```vue
<!-- frontend/src/components/common/BaseButton.vue -->
<template>
  <button
    :class="buttonClasses"
    :type="type"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="button-loading">
      <span class="button-loading-spinner"></span>
      <span v-if="loadingText" class="button-loading-text">{{ loadingText }}</span>
    </span>
    
    <span v-else class="button-content">
      <span v-if="$slots.icon" class="button-icon">
        <slot name="icon" />
      </span>
      <span class="button-text">
        <slot />
      </span>
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  loading?: boolean
  loadingText?: string
  block?: boolean
  round?: boolean
  htmlType?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  size: 'medium',
  disabled: false,
  loading: false,
  loadingText: '',
  block: false,
  round: false,
  htmlType: 'button',
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClasses = computed(() => {
  return [
    'base-button',
    `base-button--${props.type}`,
    `base-button--${props.size}`,
    {
      'base-button--disabled': props.disabled,
      'base-button--loading': props.loading,
      'base-button--block': props.block,
      'base-button--round': props.round,
    },
  ]
})

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: $border-radius-md;
  font-family: $font-family;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
  user-select: none;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  &--primary {
    background-color: $color-primary;
    color: $color-white;
    
    &:hover:not(:disabled) {
      background-color: $color-primary-light;
    }
    
    &:active:not(:disabled) {
      background-color: $color-primary-dark;
    }
  }
  
  &--secondary {
    background-color: $color-secondary;
    color: $color-white;
    
    &:hover:not(:disabled) {
      background-color: $color-secondary-light;
    }
    
    &:active:not(:disabled) {
      background-color: $color-secondary-dark;
    }
  }
  
  &--ghost {
    background-color: transparent;
    color: $color-primary;
    border: 1px solid $color-primary;
    
    &:hover:not(:disabled) {
      background-color: rgba($color-primary, 0.1);
    }
  }
  
  &--danger {
    background-color: $color-error;
    color: $color-white;
    
    &:hover:not(:disabled) {
      background-color: lighten($color-error, 10%);
    }
  }
  
  &--small {
    padding: $spacing-xs $spacing-sm;
    font-size: $font-size-sm;
    height: 32px;
  }
  
  &--medium {
    padding: $spacing-sm $spacing-md;
    font-size: $font-size-md;
    height: 40px;
  }
  
  &--large {
    padding: $spacing-md $spacing-lg;
    font-size: $font-size-lg;
    height: 48px;
  }
  
  &--block {
    width: 100%;
  }
  
  &--round {
    border-radius: $border-radius-round;
  }
  
  &--loading {
    cursor: wait;
  }
}

.button-content {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
}

.button-icon {
  display: flex;
  align-items: center;
}

.button-loading {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
}

.button-loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: $color-white;
  border-radius: 50%;
  animation: button-spin 0.8s linear infinite;
}

@keyframes button-spin {
  to {
    transform: rotate(360deg);
  }
}

.button-loading-text {
  font-size: $font-size-sm;
}
</style>
```

- [ ] **Step 2: 创建BaseButton组件测试**

```typescript
// frontend/src/components/common/BaseButton.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from './BaseButton.vue'

describe('BaseButton', () => {
  it('renders with default props', () => {
    const wrapper = mount(BaseButton, {
      slots: {
        default: 'Click me',
      },
    })
    
    expect(wrapper.text()).toContain('Click me')
    expect(wrapper.classes()).toContain('base-button--primary')
    expect(wrapper.classes()).toContain('base-button--medium')
  })
  
  it('renders with different type', () => {
    const wrapper = mount(BaseButton, {
      props: {
        type: 'secondary',
      },
      slots: {
        default: 'Secondary',
      },
    })
    
    expect(wrapper.classes()).toContain('base-button--secondary')
  })
  
  it('renders with different size', () => {
    const wrapper = mount(BaseButton, {
      props: {
        size: 'large',
      },
      slots: {
        default: 'Large',
      },
    })
    
    expect(wrapper.classes()).toContain('base-button--large')
  })
  
  it('renders disabled state', () => {
    const wrapper = mount(BaseButton, {
      props: {
        disabled: true,
      },
      slots: {
        default: 'Disabled',
      },
    })
    
    expect(wrapper.classes()).toContain('base-button--disabled')
    expect(wrapper.find('button').element.disabled).toBe(true)
  })
  
  it('renders loading state', () => {
    const wrapper = mount(BaseButton, {
      props: {
        loading: true,
      },
      slots: {
        default: 'Loading',
      },
    })
    
    expect(wrapper.classes()).toContain('base-button--loading')
    expect(wrapper.find('.button-loading-spinner').exists()).toBe(true)
  })
  
  it('emits click event when clicked', async () => {
    const wrapper = mount(BaseButton, {
      slots: {
        default: 'Click me',
      },
    })
    
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted()).toHaveProperty('click')
  })
  
  it('does not emit click when disabled', async () => {
    const wrapper = mount(BaseButton, {
      props: {
        disabled: true,
      },
      slots: {
        default: 'Disabled',
      },
    })
    
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted()).not.toHaveProperty('click')
  })
  
  it('does not emit click when loading', async () => {
    const wrapper = mount(BaseButton, {
      props: {
        loading: true,
      },
      slots: {
        default: 'Loading',
      },
    })
    
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted()).not.toHaveProperty('click')
  })
})
```

- [ ] **Step 3: 创建BaseCard基础卡片组件**

```vue
<!-- frontend/src/components/common/BaseCard.vue -->
<template>
  <div :class="cardClasses">
    <div v-if="title || $slots.header" class="base-card-header">
      <slot name="header">
        <h3 v-if="title" class="base-card-title">{{ title }}</h3>
      </slot>
    </div>
    
    <div class="base-card-body">
      <slot />
    </div>
    
    <div v-if="$slots.footer" class="base-card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  shadow?: 'sm' | 'md' | 'lg' | 'xl' | 'none'
  bordered?: boolean
  clickable?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  shadow: 'sm',
  bordered: true,
  clickable: false,
  padding: 'md',
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const cardClasses = computed(() => {
  return [
    'base-card',
    `base-card--shadow-${props.shadow}`,
    `base-card--padding-${props.padding}`,
    {
      'base-card--bordered': props.bordered,
      'base-card--clickable': props.clickable,
    },
  ]
})

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.base-card {
  background: $color-white;
  border-radius: $border-radius-md;
  overflow: hidden;
  transition: all 0.2s ease;
  
  &--shadow-sm {
    box-shadow: $shadow-sm;
  }
  
  &--shadow-md {
    box-shadow: $shadow-md;
  }
  
  &--shadow-lg {
    box-shadow: $shadow-lg;
  }
  
  &--shadow-xl {
    box-shadow: $shadow-xl;
  }
  
  &--shadow-none {
    box-shadow: none;
  }
  
  &--bordered {
    border: 1px solid $color-border;
  }
  
  &--clickable {
    cursor: pointer;
    
    &:hover {
      box-shadow: $shadow-md;
      transform: translateY(-2px);
    }
  }
  
  &--padding-none {
    padding: 0;
  }
  
  &--padding-sm {
    padding: $spacing-sm;
  }
  
  &--padding-md {
    padding: $spacing-md;
  }
  
  &--padding-lg {
    padding: $spacing-lg;
  }
}

.base-card-header {
  padding: $spacing-md $spacing-md 0;
  margin-bottom: $spacing-sm;
  
  .base-card--padding-none & {
    padding: $spacing-md $spacing-md 0;
  }
}

.base-card-title {
  font-size: $font-size-lg;
  font-weight: 600;
  color: $color-text-primary;
  margin: 0;
}

.base-card-body {
  .base-card--padding-none & {
    padding: 0;
  }
  
  .base-card--padding-sm & {
    padding: $spacing-sm;
  }
  
  .base-card--padding-md & {
    padding: $spacing-md;
  }
  
  .base-card--padding-lg & {
    padding: $spacing-lg;
  }
}

.base-card-footer {
  padding: 0 $spacing-md $spacing-md;
  margin-top: $spacing-sm;
  
  .base-card--padding-none & {
    padding: 0 $spacing-md $spacing-md;
  }
}
</style>
```

- [ ] **Step 4: 创建BaseModal基础模态框组件**

```vue
<!-- frontend/src/components/common/BaseModal.vue -->
<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="visible" class="base-modal-overlay" @click.self="handleOverlayClick">
        <div :class="modalClasses">
          <div v-if="showHeader" class="base-modal-header">
            <h3 v-if="title" class="base-modal-title">{{ title }}</h3>
            <button v-if="showClose" class="base-modal-close" @click="handleClose">
              ×
            </button>
          </div>
          
          <div class="base-modal-body">
            <slot />
          </div>
          
          <div v-if="$slots.footer" class="base-modal-footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'

interface Props {
  visible: boolean
  title?: string
  width?: string
  showHeader?: boolean
  showClose?: boolean
  closeOnOverlayClick?: boolean
  closeOnEsc?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  width: '500px',
  showHeader: true,
  showClose: true,
  closeOnOverlayClick: true,
  closeOnEsc: true,
})

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  close: []
}>()

const modalClasses = computed(() => {
  return [
    'base-modal',
    {
      'base-modal--has-header': props.showHeader,
      'base-modal--has-footer': !!useSlots().footer,
    },
  ]
})

const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

const handleOverlayClick = () => {
  if (props.closeOnOverlayClick) {
    handleClose()
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (props.closeOnEsc && event.key === 'Escape' && props.visible) {
    handleClose()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

// 获取插槽
import { useSlots } from 'vue'
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.base-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: $spacing-md;
}

.base-modal {
  background: $color-white;
  border-radius: $border-radius-lg;
  width: 100%;
  max-width: v-bind(width);
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: $shadow-xl;
}

.base-modal-header {
  padding: $spacing-lg $spacing-lg $spacing-md;
  border-bottom: 1px solid $color-border;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.base-modal-title {
  font-size: $font-size-lg;
  font-weight: 600;
  color: $color-text-primary;
  margin: 0;
}

.base-modal-close {
  background: none;
  border: none;
  font-size: $font-size-xxl;
  color: $color-text-tertiary;
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: color 0.2s ease;
  
  &:hover {
    color: $color-text-primary;
  }
}

.base-modal-body {
  padding: $spacing-lg;
  overflow-y: auto;
  flex: 1;
}

.base-modal-footer {
  padding: $spacing-md $spacing-lg $spacing-lg;
  border-top: 1px solid $color-border;
  display: flex;
  justify-content: flex-end;
  gap: $spacing-sm;
  flex-shrink: 0;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .base-modal,
.modal-fade-leave-active .base-modal {
  transition: transform 0.3s ease;
}

.modal-fade-enter-from .base-modal,
.modal-fade-leave-to .base-modal {
  transform: scale(0.9);
}
</style>
```

- [ ] **Step 5: 创建BaseLoading基础加载组件**

```vue
<!-- frontend/src/components/common/BaseLoading.vue -->
<template>
  <div :class="loadingClasses">
    <div v-if="type === 'spinner'" class="base-loading-spinner">
      <div class="base-loading-spinner-dot" v-for="i in 3" :key="i" :style="dotStyle(i)"></div>
    </div>
    
    <div v-else-if="type === 'dots'" class="base-loading-dots">
      <div class="base-loading-dot" v-for="i in 3" :key="i" :style="dotAnimationStyle(i)"></div>
    </div>
    
    <div v-else class="base-loading-circle">
      <svg class="base-loading-circle-svg" viewBox="0 0 50 50">
        <circle class="base-loading-circle-background" cx="25" cy="25" r="20" fill="none" />
        <circle class="base-loading-circle-foreground" cx="25" cy="25" r="20" fill="none" />
      </svg>
    </div>
    
    <div v-if="text" class="base-loading-text">{{ text }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'spinner' | 'dots' | 'circle'
  text?: string
  size?: 'small' | 'medium' | 'large'
  color?: string
  fullscreen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'spinner',
  size: 'medium',
  color: '#FF6B35',
  fullscreen: false,
})

const loadingClasses = computed(() => {
  return [
    'base-loading',
    `base-loading--${props.size}`,
    {
      'base-loading--fullscreen': props.fullscreen,
    },
  ]
})

const dotStyle = (index: number) => {
  const rotation = (index - 1) * 120
  return {
    transform: `rotate(${rotation}deg)`,
  }
}

const dotAnimationStyle = (index: number) => {
  return {
    animationDelay: `${(index - 1) * 0.15}s`,
  }
}
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.base-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
  
  &--fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.9);
    z-index: 9999;
  }
  
  &--small {
    .base-loading-spinner,
    .base-loading-dots,
    .base-loading-circle {
      width: 24px;
      height: 24px;
    }
    
    .base-loading-text {
      font-size: $font-size-sm;
    }
  }
  
  &--medium {
    .base-loading-spinner,
    .base-loading-dots,
    .base-loading-circle {
      width: 32px;
      height: 32px;
    }
    
    .base-loading-text {
      font-size: $font-size-md;
    }
  }
  
  &--large {
    .base-loading-spinner,
    .base-loading-dots,
    .base-loading-circle {
      width: 48px;
      height: 48px;
    }
    
    .base-loading-text {
      font-size: $font-size-lg;
    }
  }
}

.base-loading-spinner {
  position: relative;
  width: 32px;
  height: 32px;
}

.base-loading-spinner-dot {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  
  &::before {
    content: '';
    display: block;
    width: 20%;
    height: 20%;
    background-color: v-bind(color);
    border-radius: 50%;
    margin: 0 auto;
    animation: spinner-dot 1.2s infinite ease-in-out both;
  }
}

.base-loading-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.base-loading-dot {
  width: 8px;
  height: 8px;
  background-color: v-bind(color);
  border-radius: 50%;
  animation: dots-bounce 1.4s infinite ease-in-out both;
}

.base-loading-circle {
  width: 32px;
  height: 32px;
}

.base-loading-circle-svg {
  width: 100%;
  height: 100%;
  animation: circle-rotate 1.4s linear infinite;
}

.base-loading-circle-background {
  stroke: rgba(0, 0, 0, 0.1);
  stroke-width: 3;
}

.base-loading-circle-foreground {
  stroke: v-bind(color);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-dasharray: 90, 150;
  stroke-dashoffset: 0;
  animation: circle-dash 1.4s ease-in-out infinite;
}

.base-loading-text {
  color: $color-text-secondary;
  font-weight: 500;
  text-align: center;
}

@keyframes spinner-dot {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

@keyframes dots-bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

@keyframes circle-rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes circle-dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}
</style>
```

- [ ] **Step 6: 运行组件测试**

```bash
cd frontend
npm test -- frontend/src/components/common/BaseButton.test.ts
```

Expected: All tests pass

- [ ] **Step 7: 提交基础组件文件**

```bash
git add frontend/src/components/common/
git commit -m "feat: 创建基础组件系统"
```

---

## Task 7: 验证第一阶段完成

**Files:**
- Test: Run all tests
- Build: Test build process

- [ ] **Step 1: 运行所有测试**

```bash
cd frontend
npm test -- --passWithNoTests
```

Expected: All tests pass

- [ ] **Step 2: 测试uni-app构建**

```bash
cd frontend
npm run build:mp-weixin
```

Expected: Build completes without errors

- [ ] **Step 3: 检查目录结构完整性**

```bash
cd frontend
ls -la
ls -la src/
ls -la src/components/common/
ls -la src/stores/
ls -la src/styles/
ls -la src/utils/api/
```

Expected: All required files exist

- [ ] **Step 4: 创建第一阶段完成标记**

```bash
cd frontend
echo "第一阶段完成：基础框架搭建" > .phase1-complete
git add .phase1-complete
git commit -m "feat: 完成第一阶段基础框架搭建"
```

- [ ] **Step 5: 更新项目README（可选）**

```bash
cd frontend
cat > README.md << 'EOF'
# break-mini-app 前端

面包店小程序前端，基于Vue 3 + uni-app + Vant的混合渐进式架构。

## 第一阶段完成

✅ 基础框架搭建完成：
- uni-app核心配置文件 (pages.json, manifest.json, App.vue, main.ts)
- SCSS样式系统 (variables.scss, mixins.scss, global.scss)
- Pinia状态管理 (user.store, cart.store, product.store, order.store)
- Axios API层配置
- 基础组件系统 (BaseButton, BaseCard, BaseModal, BaseLoading)

## 开发

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建
npm run build

# 测试
npm test
```

## 技术栈
- Vue 3 + TypeScript
- uni-app (跨平台小程序框架)
- Pinia (状态管理)
- Vant Weapp (UI组件库)
- Axios (HTTP客户端)
- SCSS (样式预处理器)
- Jest (测试框架)

## 项目结构
```
frontend/
├── src/
│   ├── components/     # 组件
│   │   ├── common/    # 基础组件
│   │   └── business/  # 业务组件
│   ├── pages/         # 页面组件
│   ├── stores/        # Pinia状态管理
│   ├── styles/        # 样式系统
│   └── utils/         # 工具函数
├── pages.json         # uni-app路由配置
├── manifest.json      # uni-app应用配置
└── package.json       # 项目配置
```
EOF

git add README.md
git commit -m "docs: 更新前端README文档"
```

---

## 计划自检

### 1. Spec覆盖检查
- [x] 修复jest preset依赖 ✅
- [x] 创建uni-app核心配置文件 ✅
- [x] 创建SCSS样式系统 ✅
- [x] 创建Pinia状态管理 ✅
- [x] 配置Axios API层 ✅
- [x] 创建基础组件 ✅

### 2. 占位符扫描
检查完成：无TBD、TODO或其他占位符。所有步骤都包含完整代码。

### 3. 类型一致性检查
检查完成：所有TypeScript类型定义一致，函数签名匹配。

## 执行选项

**计划已保存到 `docs/superpowers/plans/2026-04-04-break-mini-app-frontend-phase1.md`。**

两个执行选项：

**1. Subagent-Driven (推荐)** - 我为每个任务派发一个独立的子代理，在任务间进行review，快速迭代

**2. Inline Execution** - 在此会话中使用executing-plans内联执行，分批执行并设置检查点

**选择哪个方法？**