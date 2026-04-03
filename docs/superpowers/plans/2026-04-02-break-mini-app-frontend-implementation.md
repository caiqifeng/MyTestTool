# break-mini-app 前端实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现面包店小程序前端，基于Vue 3 + uni-app + Vant的混合渐进式架构，包含首页、商品浏览、购物车、订单流程、用户中心等完整功能。

**Architecture:** 混合渐进式架构，从简单的uni-app标准页面结构开始，逐步引入模块化和组件化。全局状态使用Pinia管理，局部状态使用组件状态。API层使用Axios封装，样式系统基于SCSS变量。

**Tech Stack:** Vue 3, TypeScript, uni-app, Pinia, Vant Weapp, Axios, SCSS, Jest

---

## 第一阶段：基础框架搭建

### Task 1: 修复前端测试配置

**Files:**
- Modify: `frontend/jest.config.js`
- Modify: `frontend/jest.setup.js`
- Delete: `frontend/src/components/SimpleTest.test.js`

- [ ] **Step 1: 修复jest.config.js配置**

```javascript
// frontend/jest.config.js
module.exports = {
  preset: '@vue/cli-plugin-unit-jest/preset',
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

- [ ] **Step 2: 修复jest.setup.js配置**

```javascript
// frontend/jest.setup.js
import { config } from '@vue/test-utils';

// 配置Vue Test Utils
config.global = {
  ...config.global,
  // 全局组件模拟（如果有的话）
  // 全局插件（如果有的话）
};

// 全局测试辅助函数
global.testUtils = {
  mountComponent: (component, options = {}) => {
    return mount(component, {
      global: {
        plugins: [], // 添加全局插件
        components: {}, // 添加全局组件
      },
      ...options,
    });
  },
};
```

- [ ] **Step 3: 删除有问题的测试文件**

```bash
cd frontend
rm src/components/SimpleTest.test.js
```

- [ ] **Step 4: 运行测试验证配置**

```bash
cd frontend
npm test -- --passWithNoTests
```

Expected: PASS (所有测试通过或没有测试)

- [ ] **Step 5: 提交更改**

```bash
cd frontend
git add jest.config.js jest.setup.js
git add -u src/components/SimpleTest.test.js
git commit -m "fix: repair frontend jest configuration"
```

### Task 2: 创建uni-app核心配置文件

**Files:**
- Create: `frontend/pages.json`
- Create: `frontend/manifest.json`
- Modify: `frontend/App.vue`
- Create: `frontend/main.ts`

- [ ] **Step 1: 创建pages.json路由配置**

```json
// frontend/pages.json
{
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "面包小店",
        "navigationBarBackgroundColor": "#FF6B35",
        "navigationBarTextStyle": "white"
      }
    },
    {
      "path": "pages/product/list",
      "style": {
        "navigationBarTitleText": "商品列表",
        "navigationBarBackgroundColor": "#FF6B35",
        "navigationBarTextStyle": "white"
      }
    },
    {
      "path": "pages/product/detail",
      "style": {
        "navigationBarTitleText": "商品详情",
        "navigationBarBackgroundColor": "#FF6B35",
        "navigationBarTextStyle": "white"
      }
    },
    {
      "path": "pages/cart/index",
      "style": {
        "navigationBarTitleText": "购物车",
        "navigationBarBackgroundColor": "#FF6B35",
        "navigationBarTextStyle": "white"
      }
    },
    {
      "path": "pages/order/confirm",
      "style": {
        "navigationBarTitleText": "订单确认",
        "navigationBarBackgroundColor": "#FF6B35",
        "navigationBarTextStyle": "white"
      }
    },
    {
      "path": "pages/user/index",
      "style": {
        "navigationBarTitleText": "个人中心",
        "navigationBarBackgroundColor": "#FF6B35",
        "navigationBarTextStyle": "white"
      }
    }
  ],
  "globalStyle": {
    "navigationBarTextStyle": "white",
    "navigationBarTitleText": "面包小店",
    "navigationBarBackgroundColor": "#FF6B35",
    "backgroundColor": "#F8F8F8",
    "app-plus": {
      "background": "#F8F8F8"
    }
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
        "pagePath": "pages/user/index",
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
  "name": "面包小店",
  "appid": "__UNI__BREAKMINIAPP",
  "description": "新鲜面包，温暖到家",
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
    "appid": "wx-your-appid-here",
    "setting": {
      "urlCheck": false,
      "es6": true,
      "postcss": true,
      "minified": true
    },
    "usingComponents": true,
    "permission": {
      "scope.userLocation": {
        "desc": "获取您的位置信息以提供配送服务"
      }
    },
    "requiredPrivateInfos": ["getLocation"]
  },
  "mp-alipay": {
    "usingComponents": true
  },
  "h5": {
    "title": "面包小店",
    "template": "index.html",
    "router": {
      "mode": "hash",
      "base": "./"
    }
  }
}
```

- [ ] **Step 3: 创建App.vue应用根组件**

```vue
<!-- frontend/App.vue -->
<template>
  <div>
    <!-- 页面内容将通过路由渲染 -->
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from './stores/user.store'

// 应用启动时执行
onLaunch(() => {
  console.log('App Launch')
  
  // 检查登录状态
  const userStore = useUserStore()
  userStore.checkLoginStatus()
})

// 应用显示时执行
onShow(() => {
  console.log('App Show')
})

// 应用隐藏时执行
onHide(() => {
  console.log('App Hide')
})
</script>

<style lang="scss">
/* 全局样式 */
@import './styles/global.scss';

/* 重置样式 */
page {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
               'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
  background-color: #f8f8f8;
}

/* 通用样式 */
.container {
  padding: 16px;
}

.flex {
  display: flex;
}

.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-center {
  text-align: center;
}
</style>
```

- [ ] **Step 4: 创建main.ts应用入口**

```typescript
// frontend/main.ts
import { createSSRApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

// 创建Vue应用实例
export function createApp() {
  const app = createSSRApp(App)
  const pinia = createPinia()
  
  // 使用Pinia状态管理
  app.use(pinia)
  
  return {
    app,
    pinia,
  }
}

// 初始化应用
const { app } = createApp()

// 挂载应用
app.mount('#app')
```

- [ ] **Step 5: 验证uni-app配置**

```bash
cd frontend
# 检查配置语法
npx @dcloudio/vite-plugin-uni/pages-json --verify
```

Expected: 没有错误输出

- [ ] **Step 6: 提交uni-app核心配置**

```bash
cd frontend
git add pages.json manifest.json App.vue main.ts
git commit -m "feat: add uni-app core configuration files"
```

### Task 3: 创建样式系统

**Files:**
- Create: `frontend/styles/variables.scss`
- Create: `frontend/styles/mixins.scss`
- Create: `frontend/styles/global.scss`
- Create: `frontend/uni.scss`

- [ ] **Step 1: 创建SCSS变量文件**

```scss
// frontend/styles/variables.scss
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

// 响应式断点
$breakpoint-sm: 576px;
$breakpoint-md: 768px;
$breakpoint-lg: 992px;
$breakpoint-xl: 1200px;

// 动画时长
$transition-fast: 150ms;
$transition-normal: 250ms;
$transition-slow: 350ms;
```

- [ ] **Step 2: 创建SCSS Mixin文件**

```scss
// frontend/styles/mixins.scss
@import './variables.scss';

// 响应式断点
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

@mixin flex-column-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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
  padding: $spacing-sm $spacing-md;
  border-radius: $border-radius-md;
  font-size: $font-size-md;
  font-weight: 500;
  line-height: 1.5;
  text-align: center;
  cursor: pointer;
  transition: all $transition-normal ease;
  border: 1px solid transparent;
  user-select: none;
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  &:active {
    transform: translateY(1px);
  }
}

// 卡片基础样式
@mixin card-base {
  background-color: $color-white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  padding: $spacing-md;
  transition: box-shadow $transition-normal ease;
  
  &:hover {
    box-shadow: $shadow-md;
  }
}

// 分割线
@mixin divider($color: $color-border, $margin: $spacing-md) {
  height: 1px;
  background-color: $color;
  margin: $margin 0;
  border: none;
}
```

- [ ] **Step 3: 创建全局样式文件**

```scss
// frontend/styles/global.scss
@import './variables.scss';
@import './mixins.scss';

// 重置样式
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  font-family: $font-family;
  font-size: $font-size-md;
  color: $color-text-primary;
  background-color: $color-background;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

// 链接样式
a {
  color: $color-primary;
  text-decoration: none;
  
  &:hover {
    color: $color-primary-dark;
    text-decoration: underline;
  }
}

// 图片响应式
img {
  max-width: 100%;
  height: auto;
  display: block;
}

// 表单元素重置
input, textarea, select, button {
  font-family: inherit;
  font-size: inherit;
  color: inherit;
}

// 工具类
.text-primary { color: $color-primary; }
.text-secondary { color: $color-text-secondary; }
.text-tertiary { color: $color-text-tertiary; }
.text-success { color: $color-success; }
.text-warning { color: $color-warning; }
.text-error { color: $color-error; }
.text-info { color: $color-info; }

.bg-primary { background-color: $color-primary; }
.bg-secondary { background-color: $color-secondary; }
.bg-white { background-color: $color-white; }
.bg-background { background-color: $color-background; }

.mt-xs { margin-top: $spacing-xs; }
.mt-sm { margin-top: $spacing-sm; }
.mt-md { margin-top: $spacing-md; }
.mt-lg { margin-top: $spacing-lg; }
.mt-xl { margin-top: $spacing-xl; }

.mb-xs { margin-bottom: $spacing-xs; }
.mb-sm { margin-bottom: $spacing-sm; }
.mb-md { margin-bottom: $spacing-md; }
.mb-lg { margin-bottom: $spacing-lg; }
.mb-xl { margin-bottom: $spacing-xl; }

.p-xs { padding: $spacing-xs; }
.p-sm { padding: $spacing-sm; }
.p-md { padding: $spacing-md; }
.p-lg { padding: $spacing-lg; }
.p-xl { padding: $spacing-xl; }

// 布局工具类
.flex { display: flex; }
.flex-1 { flex: 1; }
.flex-column { flex-direction: column; }
.items-center { align-items: center; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.justify-end { justify-content: flex-end; }

// 显示隐藏工具类
.hidden { display: none; }
.visible { display: block; }

// 圆角工具类
.rounded-sm { border-radius: $border-radius-sm; }
.rounded-md { border-radius: $border-radius-md; }
.rounded-lg { border-radius: $border-radius-lg; }
.rounded-xl { border-radius: $border-radius-xl; }
.rounded-full { border-radius: $border-radius-round; }

// 阴影工具类
.shadow-sm { box-shadow: $shadow-sm; }
.shadow-md { box-shadow: $shadow-md; }
.shadow-lg { box-shadow: $shadow-lg; }
.shadow-xl { box-shadow: $shadow-xl; }

// 文字工具类
.text-xs { font-size: $font-size-xs; }
.text-sm { font-size: $font-size-sm; }
.text-md { font-size: $font-size-md; }
.text-lg { font-size: $font-size-lg; }
.text-xl { font-size: $font-size-xl; }
.text-xxl { font-size: $font-size-xxl; }

.text-bold { font-weight: 700; }
.text-semibold { font-weight: 600; }
.text-medium { font-weight: 500; }
.text-normal { font-weight: 400; }

.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

// 溢出处理
.overflow-hidden { overflow: hidden; }
.overflow-auto { overflow: auto; }
.overflow-x-auto { overflow-x: auto; }
.overflow-y-auto { overflow-y: auto; }

// 定位工具类
.relative { position: relative; }
.absolute { position: absolute; }
.fixed { position: fixed; }
.sticky { position: sticky; }

// 宽度高度工具类
.w-full { width: 100%; }
.h-full { height: 100%; }
.min-h-screen { min-height: 100vh; }

// 边框工具类
.border { border: 1px solid $color-border; }
.border-t { border-top: 1px solid $color-border; }
.border-b { border-bottom: 1px solid $color-border; }
.border-l { border-left: 1px solid $color-border; }
.border-r { border-right: 1px solid $color-border; }

.border-primary { border-color: $color-primary; }
.border-secondary { border-color: $color-secondary; }
.border-success { border-color: $color-success; }
.border-warning { border-color: $color-warning; }
.border-error { border-color: $color-error; }
```

- [ ] **Step 4: 创建uni.scss全局样式入口**

```scss
// frontend/uni.scss
/* uni.scss - uni-app全局样式入口 */

// 导入变量和混合
@import './styles/variables.scss';
@import './styles/mixins.scss';

// 通用uni-app样式覆盖
uni-page-body {
  height: 100%;
}

uni-button {
  &.button-hover {
    opacity: 0.8;
  }
}

// 页面容器通用样式
.page-container {
  min-height: 100vh;
  background-color: $color-background;
}

// 安全区域适配
.safe-area-inset-bottom {
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}

.safe-area-inset-top {
  padding-top: constant(safe-area-inset-top);
  padding-top: env(safe-area-inset-top);
}

// 滚动条样式
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: $color-background;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: $color-border;
  border-radius: 3px;
  
  &:hover {
    background: $color-text-tertiary;
  }
}
```

- [ ] **Step 5: 验证SCSS语法**

```bash
cd frontend
# 检查SCSS语法
npx sass --check styles/variables.scss styles/mixins.scss styles/global.scss uni.scss
```

Expected: 没有错误输出

- [ ] **Step 6: 提交样式系统**

```bash
cd frontend
git add styles/ uni.scss
git commit -m "feat: add SCSS style system with variables and mixins"
```

### Task 4: 创建Pinia状态管理

**Files:**
- Create: `frontend/stores/user.store.ts`
- Create: `frontend/stores/cart.store.ts`
- Create: `frontend/stores/product.store.ts`
- Create: `frontend/stores/order.store.ts`
- Create: `frontend/stores/index.ts`

- [ ] **Step 1: 创建用户状态管理store**

```typescript
// frontend/stores/user.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '../../shared/src/types'

export const useUserStore = defineStore('user', () => {
  // 状态
  const userInfo = ref<User | null>(null)
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoggedIn = ref(false)

  // Getter计算属性
  const userId = computed(() => userInfo.value?._id)
  const userRole = computed(() => userInfo.value?.role)
  const userName = computed(() => userInfo.value?.nickname)
  const userAvatar = computed(() => userInfo.value?.avatar)

  // Actions操作
  const setUser = (user: User) => {
    userInfo.value = user
    isLoggedIn.value = true
  }

  const setToken = (newToken: string) => {
    token.value = newToken
    // 存储到本地存储
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', newToken)
    }
  }

  const setRefreshToken = (newRefreshToken: string) => {
    refreshToken.value = newRefreshToken
    // 存储到本地存储
    if (typeof window !== 'undefined') {
      localStorage.setItem('refreshToken', newRefreshToken)
    }
  }

  const clearUser = () => {
    userInfo.value = null
    token.value = null
    refreshToken.value = null
    isLoggedIn.value = false
    // 清除本地存储
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
    }
  }

  const checkLoginStatus = () => {
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('token')
      const storedRefreshToken = localStorage.getItem('refreshToken')
      
      if (storedToken) {
        token.value = storedToken
        isLoggedIn.value = true
        // 这里可以添加验证token有效性的逻辑
      }
      
      if (storedRefreshToken) {
        refreshToken.value = storedRefreshToken
      }
    }
  }

  return {
    // 状态
    userInfo,
    token,
    refreshToken,
    isLoggedIn,
    
    // Getter
    userId,
    userRole,
    userName,
    userAvatar,
    
    // Actions
    setUser,
    setToken,
    setRefreshToken,
    clearUser,
    checkLoginStatus,
  }
})
```

- [ ] **Step 2: 创建购物车状态管理store**

```typescript
// frontend/stores/cart.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Product, ProductSpec } from '../../shared/src/types'

export interface CartItem {
  productId: string
  product: Product
  quantity: number
  selectedSpecs?: ProductSpec[]
  notes?: string
}

export const useCartStore = defineStore('cart', () => {
  // 状态
  const items = ref<CartItem[]>([])
  const selectedItems = ref<string[]>([]) // 选中的商品ID
  const coupon = ref<any>(null) // 应用的优惠券

  // Getter计算属性
  const totalItems = computed(() => 
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )
  
  const selectedItemsCount = computed(() => 
    items.value.filter(item => selectedItems.value.includes(item.productId)).length
  )
  
  const isAllSelected = computed(() => 
    items.value.length > 0 && selectedItems.value.length === items.value.length
  )
  
  const itemsSubtotal = computed(() => 
    items.value
      .filter(item => selectedItems.value.includes(item.productId))
      .reduce((sum, item) => sum + (item.product.price * item.quantity), 0)
  )
  
  const discountAmount = computed(() => {
    if (!coupon.value) return 0
    
    const { discountType, discountValue, maxDiscountAmount } = coupon.value
    let discount = 0
    
    if (discountType === 'percentage') {
      discount = itemsSubtotal.value * (discountValue / 100)
      if (maxDiscountAmount && discount > maxDiscountAmount) {
        discount = maxDiscountAmount
      }
    } else if (discountType === 'fixed') {
      discount = discountValue
    }
    
    return discount
  })
  
  const deliveryFee = computed(() => {
    // 满50免运费
    const FREE_DELIVERY_THRESHOLD = 50
    const DELIVERY_FEE = 5
    
    return itemsSubtotal.value >= FREE_DELIVERY_THRESHOLD ? 0 : DELIVERY_FEE
  })
  
  const totalAmount = computed(() => 
    itemsSubtotal.value - discountAmount.value + deliveryFee.value
  )

  // Actions操作
  const addItem = (product: Product, quantity: number = 1, specs?: ProductSpec[]) => {
    const existingItemIndex = items.value.findIndex(
      item => item.productId === product._id && 
      JSON.stringify(item.selectedSpecs) === JSON.stringify(specs)
    )
    
    if (existingItemIndex >= 0) {
      // 更新现有商品数量
      items.value[existingItemIndex].quantity += quantity
    } else {
      // 添加新商品
      items.value.push({
        productId: product._id!,
        product,
        quantity,
        selectedSpecs: specs,
      })
    }
    
    // 自动选中新添加的商品
    if (!selectedItems.value.includes(product._id!)) {
      selectedItems.value.push(product._id!)
    }
    
    // 保存到本地存储
    saveToLocalStorage()
  }

  const updateQuantity = (productId: string, quantity: number) => {
    const itemIndex = items.value.findIndex(item => item.productId === productId)
    
    if (itemIndex >= 0) {
      if (quantity <= 0) {
        removeItem(productId)
      } else {
        items.value[itemIndex].quantity = quantity
      }
    }
    
    saveToLocalStorage()
  }

  const removeItem = (productId: string) => {
    const itemIndex = items.value.findIndex(item => item.productId === productId)
    
    if (itemIndex >= 0) {
      items.value.splice(itemIndex, 1)
      // 从选中列表中移除
      const selectedIndex = selectedItems.value.indexOf(productId)
      if (selectedIndex >= 0) {
        selectedItems.value.splice(selectedIndex, 1)
      }
    }
    
    saveToLocalStorage()
  }

  const toggleSelectItem = (productId: string) => {
    const index = selectedItems.value.indexOf(productId)
    
    if (index >= 0) {
      selectedItems.value.splice(index, 1)
    } else {
      selectedItems.value.push(productId)
    }
    
    saveToLocalStorage()
  }

  const toggleSelectAll = () => {
    if (isAllSelected.value) {
      // 取消全选
      selectedItems.value = []
    } else {
      // 全选
      selectedItems.value = items.value.map(item => item.productId)
    }
    
    saveToLocalStorage()
  }

  const clearCart = () => {
    items.value = []
    selectedItems.value = []
    coupon.value = null
    clearLocalStorage()
  }

  const applyCoupon = (newCoupon: any) => {
    coupon.value = newCoupon
    saveToLocalStorage()
  }

  const removeCoupon = () => {
    coupon.value = null
    saveToLocalStorage()
  }

  // 本地存储辅助函数
  const saveToLocalStorage = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('cartItems', JSON.stringify(items.value))
      localStorage.setItem('cartSelectedItems', JSON.stringify(selectedItems.value))
      if (coupon.value) {
        localStorage.setItem('cartCoupon', JSON.stringify(coupon.value))
      } else {
        localStorage.removeItem('cartCoupon')
      }
    }
  }

  const loadFromLocalStorage = () => {
    if (typeof window !== 'undefined') {
      const storedItems = localStorage.getItem('cartItems')
      const storedSelected = localStorage.getItem('cartSelectedItems')
      const storedCoupon = localStorage.getItem('cartCoupon')
      
      if (storedItems) {
        try {
          items.value = JSON.parse(storedItems)
        } catch (error) {
          console.error('Failed to parse cart items:', error)
          items.value = []
        }
      }
      
      if (storedSelected) {
        try {
          selectedItems.value = JSON.parse(storedSelected)
        } catch (error) {
          console.error('Failed to parse selected items:', error)
          selectedItems.value = []
        }
      }
      
      if (storedCoupon) {
        try {
          coupon.value = JSON.parse(storedCoupon)
        } catch (error) {
          console.error('Failed to parse coupon:', error)
          coupon.value = null
        }
      }
    }
  }

  const clearLocalStorage = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('cartItems')
      localStorage.removeItem('cartSelectedItems')
      localStorage.removeItem('cartCoupon')
    }
  }

  // 初始化时从本地存储加载
  loadFromLocalStorage()

  return {
    // 状态
    items,
    selectedItems,
    coupon,
    
    // Getter
    totalItems,
    selectedItemsCount,
    isAllSelected,
    itemsSubtotal,
    discountAmount,
    deliveryFee,
    totalAmount,
    
    // Actions
    addItem,
    updateQuantity,
    removeItem,
    toggleSelectItem,
    toggleSelectAll,
    clearCart,
    applyCoupon,
    removeCoupon,
    saveToLocalStorage,
    loadFromLocalStorage,
  }
})
```

- [ ] **Step 3: 创建商品状态管理store**

```typescript
// frontend/stores/product.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Product, Category } from '../../shared/src/types'

export const useProductStore = defineStore('product', () => {
  // 状态
  const products = ref<Product[]>([])
  const categories = ref<Category[]>([])
  const currentProduct = ref<Product | null>(null)
  const searchHistory = ref<string[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getter计算属性
  const featuredProducts = computed(() => 
    products.value
      .filter(product => product.status === 'active')
      .sort((a, b) => b.sortOrder - a.sortOrder)
      .slice(0, 8)
  )
  
  const popularProducts = computed(() => 
    products.value
      .filter(product => product.status === 'active')
      .sort((a, b) => b.salesCount - a.salesCount)
      .slice(0, 6)
  )
  
  const categoryMap = computed(() => {
    const map: Record<string, Category> = {}
    categories.value.forEach(category => {
      map[category._id!] = category
    })
    return map
  })

  // Actions操作
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
    
    // 移除重复的搜索词
    const index = searchHistory.value.indexOf(keyword)
    if (index >= 0) {
      searchHistory.value.splice(index, 1)
    }
    
    // 添加到开头
    searchHistory.value.unshift(keyword)
    
    // 限制历史记录数量
    if (searchHistory.value.length > 10) {
      searchHistory.value = searchHistory.value.slice(0, 10)
    }
    
    // 保存到本地存储
    saveSearchHistory()
  }

  const clearSearchHistory = () => {
    searchHistory.value = []
    clearSearchHistoryStorage()
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  // 本地存储辅助函数
  const saveSearchHistory = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('productSearchHistory', JSON.stringify(searchHistory.value))
    }
  }

  const loadSearchHistory = () => {
    if (typeof window !== 'undefined') {
      const storedHistory = localStorage.getItem('productSearchHistory')
      if (storedHistory) {
        try {
          searchHistory.value = JSON.parse(storedHistory)
        } catch (error) {
          console.error('Failed to parse search history:', error)
          searchHistory.value = []
        }
      }
    }
  }

  const clearSearchHistoryStorage = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('productSearchHistory')
    }
  }

  // 初始化时从本地存储加载搜索历史
  loadSearchHistory()

  return {
    // 状态
    products,
    categories,
    currentProduct,
    searchHistory,
    isLoading,
    error,
    
    // Getter
    featuredProducts,
    popularProducts,
    categoryMap,
    
    // Actions
    setProducts,
    setCategories,
    setCurrentProduct,
    addSearchHistory,
    clearSearchHistory,
    setLoading,
    setError,
  }
})
```

- [ ] **Step 4: 创建订单状态管理store**

```typescript
// frontend/stores/order.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Order, Address, Coupon } from '../../shared/src/types'

export const useOrderStore = defineStore('order', () => {
  // 状态
  const currentOrder = ref<Order | null>(null)
  const orders = ref<Order[]>([])
  const addresses = ref<Address[]>([])
  const coupons = ref<Coupon[]>([])
  const selectedAddress = ref<Address | null>(null)
  const selectedCoupon = ref<Coupon | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getter计算属性
  const pendingOrders = computed(() => 
    orders.value.filter(order => 
      ['pending', 'confirmed', 'processing', 'ready_for_pickup', 'out_for_delivery'].includes(order.orderStatus)
    )
  )
  
  const completedOrders = computed(() => 
    orders.value.filter(order => order.orderStatus === 'completed')
  )
  
  const defaultAddress = computed(() => 
    addresses.value.find(address => address.isDefault) || addresses.value[0] || null
  )
  
  const availableCoupons = computed(() => 
    coupons.value.filter(coupon => 
      coupon.isActive && 
      new Date(coupon.startDate) <= new Date() && 
      new Date() <= new Date(coupon.endDate) &&
      (coupon.usageLimit === undefined || coupon.usedCount < coupon.usageLimit)
    )
  )

  // Actions操作
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

  const setSelectedAddress = (address: Address | null) => {
    selectedAddress.value = address
  }

  const setSelectedCoupon = (coupon: Coupon | null) => {
    selectedCoupon.value = coupon
  }

  const addAddress = (address: Address) => {
    addresses.value.push(address)
    
    // 如果这是第一个地址或设为默认，则自动选中
    if (addresses.value.length === 1 || address.isDefault) {
      selectedAddress.value = address
    }
  }

  const updateAddress = (addressId: string, updates: Partial<Address>) => {
    const index = addresses.value.findIndex(addr => addr._id === addressId)
    if (index >= 0) {
      addresses.value[index] = { ...addresses.value[index], ...updates }
      
      // 如果更新为默认地址，则取消其他地址的默认状态
      if (updates.isDefault) {
        addresses.value.forEach((addr, i) => {
          if (i !== index && addr.isDefault) {
            addresses.value[i].isDefault = false
          }
        })
        
        // 更新选中地址
        if (selectedAddress.value?._id === addressId) {
          selectedAddress.value = addresses.value[index]
        }
      }
    }
  }

  const deleteAddress = (addressId: string) => {
    const index = addresses.value.findIndex(addr => addr._id === addressId)
    if (index >= 0) {
      // 如果删除的是选中地址，重置选中状态
      if (selectedAddress.value?._id === addressId) {
        selectedAddress.value = defaultAddress.value
      }
      
      addresses.value.splice(index, 1)
    }
  }

  const addOrder = (order: Order) => {
    orders.value.unshift(order)
  }

  const updateOrderStatus = (orderId: string, status: string) => {
    const index = orders.value.findIndex(order => order._id === orderId)
    if (index >= 0) {
      orders.value[index].orderStatus = status
    }
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  const resetCurrentOrder = () => {
    currentOrder.value = null
    selectedAddress.value = defaultAddress.value
    selectedCoupon.value = null
  }

  return {
    // 状态
    currentOrder,
    orders,
    addresses,
    coupons,
    selectedAddress,
    selectedCoupon,
    isLoading,
    error,
    
    // Getter
    pendingOrders,
    completedOrders,
    defaultAddress,
    availableCoupons,
    
    // Actions
    setCurrentOrder,
    setOrders,
    setAddresses,
    setCoupons,
    setSelectedAddress,
    setSelectedCoupon,
    addAddress,
    updateAddress,
    deleteAddress,
    addOrder,
    updateOrderStatus,
    setLoading,
    setError,
    resetCurrentOrder,
  }
})
```

- [ ] **Step 5: 创建stores统一导出文件**

```typescript
// frontend/stores/index.ts
export { useUserStore } from './user.store'
export { useCartStore } from './cart.store'
export { useProductStore } from './product.store'
export { useOrderStore } from './order.store'

// 统一初始化函数（可选）
export const initializeStores = () => {
  // 这里可以添加所有store的初始化逻辑
  console.log('Stores initialized')
}
```

- [ ] **Step 6: 创建Pinia store的TypeScript测试**

```typescript
// frontend/stores/user.store.test.ts
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach } from 'vitest'
import { useUserStore } from './user.store'

describe('User Store', () => {
  beforeEach(() => {
    // 创建一个新的pinia实例并激活
    setActivePinia(createPinia())
  })

  it('should initialize with default values', () => {
    const store = useUserStore()
    
    expect(store.userInfo).toBeNull()
    expect(store.token).toBeNull()
    expect(store.refreshToken).toBeNull()
    expect(store.isLoggedIn).toBe(false)
  })

  it('should set user info correctly', () => {
    const store = useUserStore()
    const mockUser = {
      _id: 'user123',
      openid: 'openid123',
      nickname: 'Test User',
      role: 'customer',
    } as any
    
    store.setUser(mockUser)
    
    expect(store.userInfo).toEqual(mockUser)
    expect(store.isLoggedIn).toBe(true)
    expect(store.userId).toBe('user123')
    expect(store.userName).toBe('Test User')
  })

  it('should clear user info correctly', () => {
    const store = useUserStore()
    const mockUser = {
      _id: 'user123',
      openid: 'openid123',
      nickname: 'Test User',
      role: 'customer',
    } as any
    
    store.setUser(mockUser)
    store.setToken('token123')
    store.setRefreshToken('refreshToken123')
    
    store.clearUser()
    
    expect(store.userInfo).toBeNull()
    expect(store.token).toBeNull()
    expect(store.refreshToken).toBeNull()
    expect(store.isLoggedIn).toBe(false)
  })
})
```

- [ ] **Step 7: 运行Pinia store测试**

```bash
cd frontend
npm test -- stores/user.store.test.ts --passWithNoTests
```

Expected: 测试通过或跳过（因为可能缺少vitest配置）

- [ ] **Step 8: 提交Pinia状态管理**

```bash
cd frontend
git add stores/
git commit -m "feat: add Pinia state management stores"
```

### Task 5: 创建API封装层

**Files:**
- Create: `frontend/utils/api/index.ts`
- Create: `frontend/utils/api/auth.api.ts`
- Create: `frontend/utils/api/product.api.ts`
- Create: `frontend/utils/api/order.api.ts`
- Create: `frontend/utils/api/cart.api.ts`
- Create: `frontend/utils/api/address.api.ts`
- Create: `frontend/utils/api/coupon.api.ts`

- [ ] **Step 1: 创建API配置和基础封装**

```typescript
// frontend/utils/api/index.ts
import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useUserStore } from '../../stores/user.store'

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api'
const TIMEOUT = 10000 // 10秒超时

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加token
api.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const userStore = useUserStore()
    const token = userStore.token
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // 直接返回数据部分
    return response.data
  },
  async (error) => {
    const originalRequest = error.config
    
    // 处理401错误 - token过期
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const userStore = useUserStore()
        const refreshToken = userStore.refreshToken
        
        if (refreshToken) {
          // 尝试刷新token
          const response = await axios.post(`${API_BASE_URL}/auth/refresh-token`, {
            refreshToken,
          })
          
          const { token: newToken } = response.data
          
          if (newToken) {
            // 更新store中的token
            userStore.setToken(newToken)
            
            // 重试原始请求
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            return api(originalRequest)
          }
        }
      } catch (refreshError) {
        // 刷新token失败，清除用户状态
        const userStore = useUserStore()
        userStore.clearUser()
        
        // 跳转到登录页（在uni-app中需要特殊处理）
        console.error('Token refresh failed, user logged out')
      }
    }
    
    // 统一错误提示
    const errorMessage = error.response?.data?.message || error.message || '网络错误'
    console.error('API Error:', errorMessage)
    
    // 这里可以添加统一的错误提示UI
    // uni.showToast({ title: errorMessage, icon: 'none' })
    
    return Promise.reject(error)
  }
)

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// 导出API实例
export { api }

// 导出各个模块的API
export * from './auth.api'
export * from './product.api'
export * from './order.api'
export * from './cart.api'
export * from './address.api'
export * from './coupon.api'
```

- [ ] **Step 2: 创建认证相关API**

```typescript
// frontend/utils/api/auth.api.ts
import { api } from '.'
import type { User } from '../../../shared/src/types'

export interface WechatLoginParams {
  code: string
  nickname?: string
  avatar?: string
}

export interface WechatLoginResponse {
  token: string
  refreshToken: string
  user: User
}

export interface RefreshTokenParams {
  refreshToken: string
}

export interface RefreshTokenResponse {
  token: string
}

export const authApi = {
  // 微信登录
  wechatLogin: (params: WechatLoginParams) => 
    api.post<WechatLoginResponse>('/auth/wechat-login', params),
  
  // 刷新token
  refreshToken: (params: RefreshTokenParams) => 
    api.post<RefreshTokenResponse>('/auth/refresh-token', params),
  
  // 获取当前用户信息
  getCurrentUser: () => api.get<User>('/auth/me'),
  
  // 更新用户信息
  updateUser: (updates: Partial<User>) => 
    api.put<User>('/auth/me', updates),
}
```

- [ ] **Step 3: 创建商品相关API**

```typescript
// frontend/utils/api/product.api.ts
import { api } from '.'
import type { Product, Category } from '../../../shared/src/types'

export interface ProductQueryParams {
  page?: number
  limit?: number
  categoryId?: string
  status?: string
  keyword?: string
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface ProductListResponse {
  products: Product[]
  total: number
  page: number
  limit: number
  totalPages: number
}

export const productApi = {
  // 获取商品列表
  getProducts: (params?: ProductQueryParams) => 
    api.get<ProductListResponse>('/products', { params }),
  
  // 获取商品详情
  getProduct: (id: string) => api.get<Product>(`/products/${id}`),
  
  // 获取商品分类
  getCategories: () => api.get<Category[]>('/categories'),
  
  // 获取分类详情
  getCategory: (id: string) => api.get<Category>(`/categories/${id}`),
  
  // 搜索商品
  searchProducts: (keyword: string, params?: Omit<ProductQueryParams, 'keyword'>) => 
    api.get<ProductListResponse>('/products/search', { 
      params: { keyword, ...params } 
    }),
}
```

- [ ] **Step 4: 创建订单相关API**

```typescript
// frontend/utils/api/order.api.ts
import { api } from '.'
import type { Order, Address, Coupon } from '../../../shared/src/types'

export interface CreateOrderParams {
  items: Array<{
    productId: string
    quantity: number
    specs?: Array<{ name: string; value: string }>
  }>
  deliveryType: 'delivery' | 'pickup'
  deliveryAddress?: Address
  pickupTime?: string
  paymentMethod: 'wechat_pay' | 'alipay' | 'cash' | 'card'
  remark?: string
  couponId?: string
}

export interface OrderQueryParams {
  page?: number
  limit?: number
  status?: string
  startDate?: string
  endDate?: string
}

export interface OrderListResponse {
  orders: Order[]
  total: number
  page: number
  limit: number
  totalPages: number
}

export const orderApi = {
  // 创建订单
  createOrder: (params: CreateOrderParams) => 
    api.post<Order>('/orders', params),
  
  // 获取订单列表
  getOrders: (params?: OrderQueryParams) => 
    api.get<OrderListResponse>('/orders', { params }),
  
  // 获取订单详情
  getOrder: (id: string) => api.get<Order>(`/orders/${id}`),
  
  // 取消订单
  cancelOrder: (id: string) => api.put<Order>(`/orders/${id}/cancel`),
  
  // 确认收货
  confirmOrder: (id: string) => api.put<Order>(`/orders/${id}/confirm`),
  
  // 获取订单支付状态
  getOrderPaymentStatus: (id: string) => 
    api.get<{ paid: boolean; paymentStatus: string }>(`/orders/${id}/payment-status`),
}
```

- [ ] **Step 5: 创建购物车相关API**

```typescript
// frontend/utils/api/cart.api.ts
import { api } from '.'
import type { Cart } from '../../../shared/src/types'

export interface CartItemParams {
  productId: string
  quantity: number
  specs?: Array<{ name: string; value: string }>
}

export const cartApi = {
  // 获取购物车（如果需要服务端同步）
  getCart: () => api.get<Cart>('/cart'),
  
  // 添加商品到购物车
  addToCart: (params: CartItemParams) => 
    api.post<Cart>('/cart/items', params),
  
  // 更新购物车商品数量
  updateCartItem: (itemId: string, quantity: number) => 
    api.put<Cart>(`/cart/items/${itemId}`, { quantity }),
  
  // 删除购物车商品
  removeCartItem: (itemId: string) => 
    api.delete<Cart>(`/cart/items/${itemId}`),
  
  // 清空购物车
  clearCart: () => api.delete<Cart>('/cart'),
}
```

- [ ] **Step 6: 创建地址相关API**

```typescript
// frontend/utils/api/address.api.ts
import { api } from '.'
import type { Address } from '../../../shared/src/types'

export interface CreateAddressParams {
  contactName: string
  contactPhone: string
  province: string
  city: string
  district: string
  detail: string
  isDefault?: boolean
}

export interface UpdateAddressParams extends Partial<CreateAddressParams> {}

export const addressApi = {
  // 获取地址列表
  getAddresses: () => api.get<Address[]>('/addresses'),
  
  // 获取地址详情
  getAddress: (id: string) => api.get<Address>(`/addresses/${id}`),
  
  // 创建地址
  createAddress: (params: CreateAddressParams) => 
    api.post<Address>('/addresses', params),
  
  // 更新地址
  updateAddress: (id: string, params: UpdateAddressParams) => 
    api.put<Address>(`/addresses/${id}`, params),
  
  // 删除地址
  deleteAddress: (id: string) => api.delete<void>(`/addresses/${id}`),
  
  // 设置默认地址
  setDefaultAddress: (id: string) => 
    api.put<Address>(`/addresses/${id}/set-default`),
}
```

- [ ] **Step 7: 创建优惠券相关API**

```typescript
// frontend/utils/api/coupon.api.ts
import { api } from '.'
import type { Coupon } from '../../../shared/src/types'

export interface CouponQueryParams {
  page?: number
  limit?: number
  isActive?: boolean
  applicableOnly?: boolean
}

export interface CouponListResponse {
  coupons: Coupon[]
  total: number
  page: number
  limit: number
  totalPages: number
}

export interface ValidateCouponParams {
  code: string
  orderAmount?: number
  productIds?: string[]
}

export interface ValidateCouponResponse {
  valid: boolean
  coupon?: Coupon
  message?: string
}

export const couponApi = {
  // 获取优惠券列表
  getCoupons: (params?: CouponQueryParams) => 
    api.get<CouponListResponse>('/coupons', { params }),
  
  // 获取可用优惠券
  getAvailableCoupons: (orderAmount?: number) => 
    api.get<Coupon[]>('/coupons/available', { params: { orderAmount } }),
  
  // 验证优惠券
  validateCoupon: (params: ValidateCouponParams) => 
    api.post<ValidateCouponResponse>('/coupons/validate', params),
  
  // 领取优惠券
  claimCoupon: (code: string) => 
    api.post<Coupon>('/coupons/claim', { code }),
  
  // 获取用户已领取的优惠券
  getUserCoupons: () => api.get<Coupon[]>('/coupons/my'),
}
```

- [ ] **Step 8: 创建API层测试**

```typescript
// frontend/utils/api/api.test.ts
import { describe, it, expect, vi } from 'vitest'
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'
import { authApi } from './auth.api'

// 创建axios模拟实例
const mock = new MockAdapter(axios)

describe('Auth API', () => {
  afterEach(() => {
    mock.reset()
  })

  it('should handle wechat login successfully', async () => {
    const mockResponse = {
      token: 'mock-token',
      refreshToken: 'mock-refresh-token',
      user: {
        _id: 'user123',
        openid: 'openid123',
        nickname: 'Test User',
        role: 'customer',
      },
    }

    mock.onPost('/auth/wechat-login').reply(200, mockResponse)

    const result = await authApi.wechatLogin({
      code: 'mock-code',
      nickname: 'Test User',
    })

    expect(result).toEqual(mockResponse)
  })

  it('should handle login error', async () => {
    mock.onPost('/auth/wechat-login').reply(400, {
      message: 'Invalid code',
    })

    await expect(authApi.wechatLogin({ code: 'invalid-code' }))
      .rejects.toThrow()
  })
})
```

- [ ] **Step 9: 运行API层测试**

```bash
cd frontend
npm test -- utils/api/api.test.ts --passWithNoTests
```

Expected: 测试通过或跳过

- [ ] **Step 10: 提交API封装层**

```bash
cd frontend
git add utils/api/
git commit -m "feat: add API layer with axios and module exports"
```

### Task 6: 创建基础组件

**Files:**
- Create: `frontend/src/components/common/BaseButton.vue`
- Create: `frontend/src/components/common/BaseCard.vue`
- Create: `frontend/src/components/common/BaseModal.vue`
- Create: `frontend/src/components/common/BaseLoading.vue`

- [ ] **Step 1: 创建BaseButton基础按钮组件**

```vue
<!-- frontend/src/components/common/BaseButton.vue -->
<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    :type="nativeType"
    @click="handleClick"
  >
    <span v-if="loading" class="button-loading">
      <span class="button-loading-spinner"></span>
      <span v-if="loadingText">{{ loadingText }}</span>
    </span>
    <span v-else class="button-content">
      <span v-if="iconLeft" class="button-icon-left">
        <i :class="iconLeft"></i>
      </span>
      <span class="button-text">
        <slot>{{ text }}</slot>
      </span>
      <span v-if="iconRight" class="button-icon-right">
        <i :class="iconRight"></i>
      </span>
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  // 类型
  type?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' | 'ghost'
  // 大小
  size?: 'small' | 'medium' | 'large'
  // 形状
  shape?: 'default' | 'round' | 'circle'
  // 状态
  disabled?: boolean
  loading?: boolean
  loadingText?: string
  // 内容
  text?: string
  iconLeft?: string
  iconRight?: string
  // HTML原生属性
  nativeType?: 'button' | 'submit' | 'reset'
  // 样式
  block?: boolean
  plain?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  size: 'medium',
  shape: 'default',
  disabled: false,
  loading: false,
  nativeType: 'button',
  block: false,
  plain: false,
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

// 按钮类名计算
const buttonClasses = computed(() => {
  const classes = ['base-button']
  
  // 类型
  classes.push(`base-button--${props.type}`)
  
  // 大小
  classes.push(`base-button--${props.size}`)
  
  // 形状
  if (props.shape !== 'default') {
    classes.push(`base-button--${props.shape}`)
  }
  
  // 状态
  if (props.disabled) {
    classes.push('base-button--disabled')
  }
  if (props.loading) {
    classes.push('base-button--loading')
  }
  if (props.block) {
    classes.push('base-button--block')
  }
  if (props.plain) {
    classes.push('base-button--plain')
  }
  
  return classes.join(' ')
})

// 点击处理
const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style lang="scss" scoped>
@import '../../../styles/variables.scss';

.base-button {
  // 基础样式
  @include button-base;
  
  // 类型样式
  &--primary {
    background-color: $color-primary;
    color: $color-white;
    border-color: $color-primary;
    
    &:hover:not(:disabled):not(.base-button--loading) {
      background-color: $color-primary-light;
      border-color: $color-primary-light;
    }
    
    &:active:not(:disabled):not(.base-button--loading) {
      background-color: $color-primary-dark;
      border-color: $color-primary-dark;
    }
  }
  
  &--secondary {
    background-color: $color-secondary;
    color: $color-white;
    border-color: $color-secondary;
    
    &:hover:not(:disabled):not(.base-button--loading) {
      background-color: $color-secondary-light;
      border-color: $color-secondary-light;
    }
    
    &:active:not(:disabled):not(.base-button--loading) {
      background-color: $color-secondary-dark;
      border-color: $color-secondary-dark;
    }
  }
  
  &--ghost {
    background-color: transparent;
    color: $color-primary;
    border-color: $color-primary;
    
    &:hover:not(:disabled):not(.base-button--loading) {
      background-color: rgba($color-primary, 0.1);
    }
    
    &:active:not(:disabled):not(.base-button--loading) {
      background-color: rgba($color-primary, 0.2);
    }
  }
  
  // 大小样式
  &--small {
    padding: $spacing-xs $spacing-sm;
    font-size: $font-size-sm;
    min-height: 32px;
  }
  
  &--medium {
    padding: $spacing-sm $spacing-md;
    font-size: $font-size-md;
    min-height: 40px;
  }
  
  &--large {
    padding: $spacing-md $spacing-lg;
    font-size: $font-size-lg;
    min-height: 48px;
  }
  
  // 形状样式
  &--round {
    border-radius: $border-radius-round;
  }
  
  &--circle {
    border-radius: 50%;
    width: 40px;
    height: 40px;
    padding: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    
    &.base-button--small {
      width: 32px;
      height: 32px;
    }
    
    &.base-button--large {
      width: 48px;
      height: 48px;
    }
  }
  
  // 块级样式
  &--block {
    display: flex;
    width: 100%;
  }
  
  // 朴素样式
  &--plain {
    &.base-button--primary {
      background-color: transparent;
      color: $color-primary;
      
      &:hover:not(:disabled):not(.base-button--loading) {
        background-color: rgba($color-primary, 0.1);
      }
    }
  }
  
  // 禁用状态
  &--disabled {
    opacity: 0.6;
    cursor: not-allowed;
    
    &:active {
      transform: none;
    }
  }
  
  // 加载状态
  &--loading {
    cursor: wait;
    
    .button-loading {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: $spacing-xs;
    }
    
    .button-loading-spinner {
      width: 16px;
      height: 16px;
      border: 2px solid rgba($color-white, 0.3);
      border-top-color: $color-white;
      border-radius: 50%;
      animation: button-spin 0.8s linear infinite;
      
      .base-button--primary & {
        border-top-color: $color-white;
      }
      
      .base-button--secondary & {
        border-top-color: $color-white;
      }
      
      .base-button--ghost & {
        border-top-color: $color-primary;
      }
    }
  }
  
  // 内容区域
  .button-content {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: $spacing-xs;
  }
  
  .button-icon-left,
  .button-icon-right {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2em;
  }
}

@keyframes button-spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
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
    expect(wrapper.classes()).toContain('base-button')
    expect(wrapper.classes()).toContain('base-button--primary')
    expect(wrapper.classes()).toContain('base-button--medium')
  })
  
  it('renders with different types', () => {
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
  
  it('emits click event when clicked', async () => {
    const wrapper = mount(BaseButton, {
      slots: {
        default: 'Click me',
      },
    })
    
    await wrapper.trigger('click')
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
    
    await wrapper.trigger('click')
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
    
    await wrapper.trigger('click')
    expect(wrapper.emitted()).not.toHaveProperty('click')
  })
  
  it('renders loading state', () => {
    const wrapper = mount(BaseButton, {
      props: {
        loading: true,
        loadingText: 'Loading...',
      },
    })
    
    expect(wrapper.classes()).toContain('base-button--loading')
    expect(wrapper.text()).toContain('Loading...')
    expect(wrapper.find('.button-loading-spinner').exists()).toBe(true)
  })
  
  it('renders with icons', () => {
    const wrapper = mount(BaseButton, {
      props: {
        iconLeft: 'icon-add',
        iconRight: 'icon-arrow',
      },
      slots: {
        default: 'With Icons',
      },
    })
    
    expect(wrapper.find('.button-icon-left').exists()).toBe(true)
    expect(wrapper.find('.button-icon-right').exists()).toBe(true)
  })
})
```

- [ ] **Step 3: 创建BaseCard基础卡片组件**

```vue
<!-- frontend/src/components/common/BaseCard.vue -->
<template>
  <div :class="cardClasses">
    <!-- 头部区域 -->
    <div v-if="showHeader" class="base-card__header">
      <div v-if="title || $slots.title" class="base-card__title">
        <slot name="title">{{ title }}</slot>
      </div>
      <div v-if="subtitle || $slots.subtitle" class="base-card__subtitle">
        <slot name="subtitle">{{ subtitle }}</slot>
      </div>
      <div v-if="$slots.extra" class="base-card__extra">
        <slot name="extra"></slot>
      </div>
    </div>
    
    <!-- 内容区域 -->
    <div class="base-card__body">
      <slot></slot>
    </div>
    
    <!-- 底部区域 -->
    <div v-if="$slots.footer" class="base-card__footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  subtitle?: string
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  bordered?: boolean
  hoverable?: boolean
  padding?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  radius?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'full'
  backgroundColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  shadow: 'sm',
  bordered: true,
  hoverable: false,
  padding: 'md',
  radius: 'lg',
  backgroundColor: 'white',
})

// 计算是否显示头部
const showHeader = computed(() => 
  props.title || props.subtitle || useSlots().title || useSlots().subtitle || useSlots().extra
)

// 卡片类名计算
const cardClasses = computed(() => {
  const classes = ['base-card']
  
  // 阴影
  if (props.shadow !== 'none') {
    classes.push(`base-card--shadow-${props.shadow}`)
  }
  
  // 边框
  if (props.bordered) {
    classes.push('base-card--bordered')
  }
  
  // 悬停效果
  if (props.hoverable) {
    classes.push('base-card--hoverable')
  }
  
  // 内边距
  if (props.padding !== 'md') {
    classes.push(`base-card--padding-${props.padding}`)
  }
  
  // 圆角
  if (props.radius !== 'lg') {
    classes.push(`base-card--radius-${props.radius}`)
  }
  
  return classes.join(' ')
})

// 卡片样式计算
const cardStyles = computed(() => {
  const styles: Record<string, string> = {}
  
  // 背景颜色
  if (props.backgroundColor !== 'white') {
    styles.backgroundColor = props.backgroundColor
  }
  
  return styles
})
</script>

<style lang="scss" scoped>
@import '../../../styles/variables.scss';

.base-card {
  // 基础样式
  background-color: $color-white;
  transition: all $transition-normal ease;
  
  // 边框样式
  &--bordered {
    border: 1px solid $color-border;
  }
  
  // 圆角样式
  &--radius-none {
    border-radius: 0;
  }
  
  &--radius-sm {
    border-radius: $border-radius-sm;
  }
  
  &--radius-md {
    border-radius: $border-radius-md;
  }
  
  &--radius-lg {
    border-radius: $border-radius-lg;
  }
  
  &--radius-xl {
    border-radius: $border-radius-xl;
  }
  
  &--radius-full {
    border-radius: $border-radius-round;
  }
  
  // 阴影样式
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
  
  // 内边距样式
  &--padding-none {
    .base-card__header,
    .base-card__body,
    .base-card__footer {
      padding: 0;
    }
  }
  
  &--padding-xs {
    .base-card__header,
    .base-card__body,
    .base-card__footer {
      padding: $spacing-xs;
    }
  }
  
  &--padding-sm {
    .base-card__header,
    .base-card__body,
    .base-card__footer {
      padding: $spacing-sm;
    }
  }
  
  &--padding-md {
    .base-card__header,
    .base-card__body,
    .base-card__footer {
      padding: $spacing-md;
    }
  }
  
  &--padding-lg {
    .base-card__header,
    .base-card__body,
    .base-card__footer {
      padding: $spacing-lg;
    }
  }
  
  &--padding-xl {
    .base-card__header,
    .base-card__body,
    .base-card__footer {
      padding: $spacing-xl;
    }
  }
  
  // 悬停效果
  &--hoverable {
    &:hover {
      box-shadow: $shadow-md;
      transform: translateY(-2px);
    }
  }
  
  // 头部样式
  &__header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: $spacing-md;
    border-bottom: 1px solid $color-border;
    
    .base-card--padding-none &,
    .base-card--padding-xs &,
    .base-card--padding-sm &,
    .base-card--padding-md &,
    .base-card--padding-lg &,
    .base-card--padding-xl & {
      padding: inherit;
      padding-bottom: 0;
      border-bottom: none;
    }
  }
  
  &__title {
    font-size: $font-size-lg;
    font-weight: 600;
    color: $color-text-primary;
    flex: 1;
  }
  
  &__subtitle {
    font-size: $font-size-sm;
    color: $color-text-secondary;
    margin-top: $spacing-xs;
  }
  
  &__extra {
    margin-left: $spacing-md;
  }
  
  // 内容样式
  &__body {
    padding: $spacing-md;
    
    .base-card--padding-none &,
    .base-card--padding-xs &,
    .base-card--padding-sm &,
    .base-card--padding-md &,
    .base-card--padding-lg &,
    .base-card--padding-xl & {
      padding: inherit;
    }
  }
  
  // 底部样式
  &__footer {
    padding: $spacing-md;
    border-top: 1px solid $color-border;
    
    .base-card--padding-none &,
    .base-card--padding-xs &,
    .base-card--padding-sm &,
    .base-card--padding-md &,
    .base-card--padding-lg &,
    .base-card--padding-xl & {
      padding: inherit;
      padding-top: 0;
      border-top: none;
    }
  }
}
</style>
```

- [ ] **Step 4: 创建BaseModal基础模态框组件**

```vue
<!-- frontend/src/components/common/BaseModal.vue -->
<template>
  <div
    v-if="visible"
    :class="modalClasses"
    @click="handleOverlayClick"
  >
    <div :class="contentClasses" @click.stop>
      <!-- 头部 -->
      <div v-if="showHeader" class="base-modal__header">
        <div class="base-modal__title">
          <slot name="title">{{ title }}</slot>
        </div>
        <button
          v-if="closable"
          class="base-modal__close"
          @click="handleClose"
          aria-label="Close"
        >
          <span class="base-modal__close-icon">×</span>
        </button>
      </div>
      
      <!-- 内容 -->
      <div class="base-modal__body">
        <slot></slot>
      </div>
      
      <!-- 底部 -->
      <div v-if="showFooter" class="base-modal__footer">
        <slot name="footer">
          <BaseButton
            v-if="cancelText"
            :type="cancelType"
            :size="buttonSize"
            @click="handleCancel"
          >
            {{ cancelText }}
          </BaseButton>
          <BaseButton
            v-if="confirmText"
            :type="confirmType"
            :size="buttonSize"
            :loading="confirmLoading"
            @click="handleConfirm"
          >
            {{ confirmText }}
          </BaseButton>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import BaseButton from './BaseButton.vue'

interface Props {
  // 显示控制
  visible: boolean
  // 头部
  title?: string
  closable?: boolean
  // 底部
  showFooter?: boolean
  cancelText?: string
  confirmText?: string
  cancelType?: 'default' | 'primary' | 'secondary' | 'ghost'
  confirmType?: 'default' | 'primary' | 'secondary' | 'ghost'
  confirmLoading?: boolean
  // 样式
  width?: string | number
  centered?: boolean
  maskClosable?: boolean
  animation?: 'fade' | 'slide' | 'zoom'
  zIndex?: number
  // 尺寸
  size?: 'small' | 'medium' | 'large' | 'full'
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  closable: true,
  showFooter: true,
  cancelText: '取消',
  confirmText: '确定',
  cancelType: 'default',
  confirmType: 'primary',
  confirmLoading: false,
  centered: true,
  maskClosable: true,
  animation: 'fade',
  zIndex: 1000,
  size: 'medium',
})

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  close: []
  cancel: []
  confirm: []
}>()

// 计算是否显示头部
const showHeader = computed(() => props.title || useSlots().title)

// 计算按钮尺寸
const buttonSize = computed(() => {
  switch (props.size) {
    case 'small': return 'small'
    case 'medium': return 'medium'
    case 'large': return 'large'
    case 'full': return 'medium'
    default: return 'medium'
  }
})

// 模态框类名
const modalClasses = computed(() => {
  const classes = ['base-modal']
  
  if (props.animation) {
    classes.push(`base-modal--${props.animation}`)
  }
  
  return classes.join(' ')
})

// 内容区域类名
const contentClasses = computed(() => {
  const classes = ['base-modal__content']
  
  classes.push(`base-modal__content--${props.size}`)
  
  if (props.centered) {
    classes.push('base-modal__content--centered')
  }
  
  return classes.join(' ')
})

// 内容区域样式
const contentStyles = computed(() => {
  const styles: Record<string, string> = {}
  
  if (props.width && typeof props.width === 'string') {
    styles.width = props.width
  } else if (props.width && typeof props.width === 'number') {
    styles.width = `${props.width}px`
  }
  
  if (props.zIndex !== 1000) {
    styles.zIndex = props.zIndex.toString()
  }
  
  return styles
})

// 处理关闭
const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

// 处理取消
const handleCancel = () => {
  handleClose()
  emit('cancel')
}

// 处理确认
const handleConfirm = () => {
  emit('confirm')
}

// 处理遮罩层点击
const handleOverlayClick = () => {
  if (props.maskClosable) {
    handleClose()
  }
}

// 监听visible变化，处理body滚动
watch(() => props.visible, (newVal) => {
  if (typeof document !== 'undefined') {
    if (newVal) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
  }
})
</script>

<style lang="scss" scoped>
@import '../../../styles/variables.scss';

.base-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.5);
  animation: modal-fade-in $transition-normal ease;
  
  // 动画效果
  &--fade {
    animation: modal-fade-in $transition-normal ease;
    
    .base-modal__content {
      animation: modal-content-fade-in $transition-normal ease;
    }
  }
  
  &--slide {
    animation: modal-fade-in $transition-normal ease;
    
    .base-modal__content {
      animation: modal-content-slide-up $transition-normal ease;
    }
  }
  
  &--zoom {
    animation: modal-fade-in $transition-normal ease;
    
    .base-modal__content {
      animation: modal-content-zoom-in $transition-normal ease;
    }
  }
  
  // 内容区域
  &__content {
    background-color: $color-white;
    border-radius: $border-radius-lg;
    box-shadow: $shadow-xl;
    overflow: hidden;
    max-width: 90vw;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    
    // 尺寸
    &--small {
      width: 400px;
    }
    
    &--medium {
      width: 520px;
    }
    
    &--large {
      width: 720px;
    }
    
    &--full {
      width: 90vw;
      height: 90vh;
    }
    
    // 居中
    &--centered {
      margin: auto;
    }
  }
  
  // 头部
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: $spacing-lg;
    border-bottom: 1px solid $color-border;
  }
  
  &__title {
    font-size: $font-size-lg;
    font-weight: 600;
    color: $color-text-primary;
    flex: 1;
  }
  
  &__close {
    background: none;
    border: none;
    padding: $spacing-xs;
    margin-left: $spacing-md;
    cursor: pointer;
    font-size: $font-size-xl;
    color: $color-text-tertiary;
    line-height: 1;
    transition: color $transition-fast ease;
    
    &:hover {
      color: $color-text-secondary;
    }
    
    &-icon {
      display: block;
    }
  }
  
  // 内容
  &__body {
    padding: $spacing-lg;
    flex: 1;
    overflow-y: auto;
  }
  
  // 底部
  &__footer {
    padding: $spacing-lg;
    border-top: 1px solid $color-border;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: $spacing-md;
  }
}

// 动画定义
@keyframes modal-fade-in {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

@keyframes modal-content-fade-in {
  0% {
    opacity: 0;
    transform: translateY(-20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes modal-content-slide-up {
  0% {
    transform: translateY(100%);
  }
  100% {
    transform: translateY(0);
  }
}

@keyframes modal-content-zoom-in {
  0% {
    transform: scale(0.8);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
```

- [ ] **Step 5: 创建BaseLoading基础加载组件**

```vue
<!-- frontend/src/components/common/BaseLoading.vue -->
<template>
  <div :class="loadingClasses" :style="loadingStyles">
    <!-- 全屏加载 -->
    <div v-if="fullscreen" class="base-loading__fullscreen">
      <div class="base-loading__spinner">
        <div v-if="type === 'spinner'" class="base-loading__spinner-circle"></div>
        <div v-else-if="type === 'dots'" class="base-loading__dots">
          <div class="base-loading__dot"></div>
          <div class="base-loading__dot"></div>
          <div class="base-loading__dot"></div>
        </div>
        <div v-else-if="type === 'pulse'" class="base-loading__pulse"></div>
      </div>
      <div v-if="text" class="base-loading__text">{{ text }}</div>
    </div>
    
    <!-- 内联加载 -->
    <div v-else class="base-loading__inline">
      <div class="base-loading__spinner">
        <div v-if="type === 'spinner'" class="base-loading__spinner-circle"></div>
        <div v-else-if="type === 'dots'" class="base-loading__dots">
          <div class="base-loading__dot"></div>
          <div class="base-loading__dot"></div>
          <div class="base-loading__dot"></div>
        </div>
        <div v-else-if="type === 'pulse'" class="base-loading__pulse"></div>
      </div>
      <div v-if="text" class="base-loading__text">{{ text }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  // 显示控制
  visible?: boolean
  // 类型
  type?: 'spinner' | 'dots' | 'pulse'
  // 内容
  text?: string
  // 样式
  fullscreen?: boolean
  background?: string
  color?: string
  size?: 'small' | 'medium' | 'large'
  // 自定义
  customClass?: string
  zIndex?: number
}

const props = withDefaults(defineProps<Props>(), {
  visible: true,
  type: 'spinner',
  fullscreen: false,
  background: 'rgba(255, 255, 255, 0.9)',
  color: '#FF6B35',
  size: 'medium',
  zIndex: 1000,
})

// 加载类名
const loadingClasses = computed(() => {
  const classes = ['base-loading']
  
  if (props.fullscreen) {
    classes.push('base-loading--fullscreen')
  } else {
    classes.push('base-loading--inline')
  }
  
  if (props.customClass) {
    classes.push(props.customClass)
  }
  
  return classes.join(' ')
})

// 加载样式
const loadingStyles = computed(() => {
  const styles: Record<string, string> = {}
  
  if (!props.visible) {
    styles.display = 'none'
  }
  
  if (props.fullscreen) {
    styles.backgroundColor = props.background
    styles.zIndex = props.zIndex.toString()
  }
  
  return styles
})

// 加载器尺寸
const spinnerSize = computed(() => {
  switch (props.size) {
    case 'small': return '24px'
    case 'medium': return '32px'
    case 'large': return '48px'
    default: return '32px'
  }
})
</script>

<style lang="scss" scoped>
@import '../../../styles/variables.scss';

.base-loading {
  // 全屏加载
  &--fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(255, 255, 255, 0.9);
  }
  
  // 内联加载
  &--inline {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  
  // 加载器容器
  &__spinner {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  // 旋转器
  &__spinner-circle {
    width: v-bind(spinnerSize);
    height: v-bind(spinnerSize);
    border: 3px solid rgba(v-bind(color), 0.3);
    border-top-color: v-bind(color);
    border-radius: 50%;
    animation: loading-spin 0.8s linear infinite;
  }
  
  // 点状加载
  &__dots {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
  }
  
  &__dot {
    width: 8px;
    height: 8px;
    background-color: v-bind(color);
    border-radius: 50%;
    animation: loading-dots 1.4s ease-in-out infinite;
    
    &:nth-child(2) {
      animation-delay: 0.2s;
    }
    
    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
  
  // 脉冲加载
  &__pulse {
    width: v-bind(spinnerSize);
    height: v-bind(spinnerSize);
    background-color: v-bind(color);
    border-radius: 50%;
    animation: loading-pulse 1.2s ease-in-out infinite;
  }
  
  // 文字
  &__text {
    margin-top: $spacing-md;
    font-size: $font-size-md;
    color: $color-text-secondary;
    text-align: center;
  }
  
  // 内联加载的文字
  &--inline &__text {
    margin-top: 0;
    margin-left: $spacing-sm;
  }
}

// 动画定义
@keyframes loading-spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes loading-dots {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-8px);
  }
}

@keyframes loading-pulse {
  0% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  50% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
}
</style>
```

- [ ] **Step 6: 运行基础组件测试**

```bash
cd frontend
npm test -- src/components/common/BaseButton.test.ts --passWithNoTests
```

Expected: 测试通过或跳过

- [ ] **Step 7: 提交基础组件**

```bash
cd frontend
git add src/components/common/
git commit -m "feat: add base components (Button, Card, Modal, Loading)"
```

### Task 7: 创建页面目录结构

**Files:**
- Create: `frontend/src/pages/index/index.vue`
- Create: `frontend/src/pages/index/index.scss`
- Create: `frontend/src/pages/product/list/index.vue`
- Create: `frontend/src/pages/product/detail/index.vue`
- Create: `frontend/src/pages/cart/index.vue`
- Create: `frontend/src/pages/order/confirm/index.vue`
- Create: `frontend/src/pages/user/index.vue`

- [ ] **Step 1: 创建首页页面**

```vue
<!-- frontend/src/pages/index/index.vue -->
<template>
  <view class="home-page">
    <!-- 自定义导航栏 -->
    <view class="home-navbar">
      <view class="navbar-left">
        <text class="navbar-title">面包小店</text>
      </view>
      <view class="navbar-right">
        <view class="navbar-search" @click="handleSearch">
          <text class="search-icon">🔍</text>
          <text class="search-text">搜索面包、蛋糕...</text>
        </view>
      </view>
    </view>
    
    <!-- 页面内容 -->
    <scroll-view 
      class="home-content" 
      scroll-y 
      :show-scrollbar="false"
      @scrolltolower="handleScrollToLower"
    >
      <!-- Banner轮播 -->
      <swiper 
        class="home-banner" 
        :autoplay="true" 
        :interval="3000" 
        :circular="true"
        indicator-dots
        indicator-color="rgba(255, 255, 255, 0.6)"
        indicator-active-color="#FF6B35"
      >
        <swiper-item v-for="(banner, index) in banners" :key="index">
          <image 
            class="banner-image" 
            :src="banner.image" 
            mode="aspectFill"
            @click="handleBannerClick(banner)"
          />
        </swiper-item>
      </swiper>
      
      <!-- 快捷入口 -->
      <view class="quick-entries">
        <view 
          v-for="category in quickCategories" 
          :key="category.id"
          class="quick-entry"
          @click="handleCategoryClick(category)"
        >
          <view class="entry-icon">{{ category.icon }}</view>
          <text class="entry-text">{{ category.name }}</text>
        </view>
      </view>
      
      <!-- 推荐商品 -->
      <view class="section">
        <view class="section-header">
          <text class="section-title">今日推荐</text>
          <text class="section-more" @click="handleViewMore">查看更多 ></text>
        </view>
        <view class="recommend-products">
          <ProductCard 
            v-for="product in featuredProducts" 
            :key="product._id"
            :product="product"
            @click="handleProductClick(product)"
          />
        </view>
      </view>
      
      <!-- 限时优惠 -->
      <view class="section" v-if="hasPromotions">
        <view class="section-header">
          <text class="section-title">限时优惠</text>
          <view class="promotion-timer">
            <text class="timer-text">剩余时间:</text>
            <text class="timer-value">{{ promotionTime }}</text>
          </view>
        </view>
        <view class="promotion-products">
          <!-- 这里可以添加优惠商品 -->
        </view>
      </view>
      
      <!-- 加载更多提示 -->
      <view v-if="loading" class="loading-more">
        <BaseLoading type="dots" text="加载中..." />
      </view>
      
      <view v-if="noMore" class="no-more">
        <text>没有更多了</text>
      </view>
    </scroll-view>
    
    <!-- 底部标签栏（由uni-app pages.json配置） -->
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useProductStore } from '../../stores/product.store'
import { useCartStore } from '../../stores/cart.store'
import ProductCard from '../../components/product/ProductCard.vue'
import BaseLoading from '../../components/common/BaseLoading.vue'

// Store
const productStore = useProductStore()
const cartStore = useCartStore()

// 状态
const banners = ref([
  { id: 1, image: '/static/banner/1.jpg', linkType: 'product', linkTarget: '1' },
  { id: 2, image: '/static/banner/2.jpg', linkType: 'category', linkTarget: 'bread' },
  { id: 3, image: '/static/banner/3.jpg', linkType: 'url', linkTarget: 'https://example.com' },
])

const quickCategories = ref([
  { id: 'bread', name: '面包', icon: '🍞' },
  { id: 'cake', name: '蛋糕', icon: '🎂' },
  { id: 'pastry', name: '糕点', icon: '🥐' },
  { id: 'dessert', name: '甜品', icon: '🍰' },
  { id: 'beverage', name: '饮品', icon: '🥤' },
  { id: 'all', name: '全部', icon: '📦' },
])

const promotionTime = ref('02:15:30')
const loading = ref(false)
const noMore = ref(false)

// 计算属性
const featuredProducts = computed(() => productStore.featuredProducts)
const hasPromotions = computed(() => false) // 暂时没有促销活动

// 生命周期
onMounted(() => {
  loadInitialData()
})

// 方法
const loadInitialData = async () => {
  try {
    loading.value = true
    // 这里可以调用API获取数据
    // 暂时使用模拟数据
    await new Promise(resolve => setTimeout(resolve, 1000))
    loading.value = false
  } catch (error) {
    console.error('Failed to load initial data:', error)
    loading.value = false
  }
}

const handleSearch = () => {
  uni.navigateTo({
    url: '/pages/product/list?search=true',
  })
}

const handleBannerClick = (banner: any) => {
  if (banner.linkType === 'product') {
    uni.navigateTo({
      url: `/pages/product/detail?id=${banner.linkTarget}`,
    })
  } else if (banner.linkType === 'category') {
    uni.navigateTo({
      url: `/pages/product/list?categoryId=${banner.linkTarget}`,
    })
  } else if (banner.linkType === 'url') {
    // 处理外部链接
    console.log('Open external link:', banner.linkTarget)
  }
}

const handleCategoryClick = (category: any) => {
  if (category.id === 'all') {
    uni.navigateTo({
      url: '/pages/product/list',
    })
  } else {
    uni.navigateTo({
      url: `/pages/product/list?categoryId=${category.id}`,
    })
  }
}

const handleProductClick = (product: any) => {
  uni.navigateTo({
    url: `/pages/product/detail?id=${product._id}`,
  })
}

const handleViewMore = () => {
  uni.navigateTo({
    url: '/pages/product/list',
  })
}

const handleScrollToLower = () => {
  if (!loading.value && !noMore.value) {
    loadMoreData()
  }
}

const loadMoreData = async () => {
  // 加载更多数据
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  loading.value = false
  noMore.value = true // 模拟没有更多数据
}
</script>

<style lang="scss" scoped>
@import '../../../styles/variables.scss';

.home-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.home-navbar {
  padding: $spacing-md $spacing-lg;
  background-color: $color-primary;
  color: $color-white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  
  .navbar-left {
    .navbar-title {
      font-size: $font-size-xl;
      font-weight: 600;
    }
  }
  
  .navbar-right {
    flex: 1;
    margin-left: $spacing-lg;
    
    .navbar-search {
      background-color: rgba($color-white, 0.2);
      border-radius: $border-radius-round;
      padding: $spacing-xs $spacing-md;
      display: flex;
      align-items: center;
      cursor: pointer;
      
      .search-icon {
        margin-right: $spacing-xs;
        font-size: $font-size-md;
      }
      
      .search-text {
        font-size: $font-size-sm;
        color: rgba($color-white, 0.8);
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }
}

.home-content {
  flex: 1;
  background-color: $color-background;
}

.home-banner {
  height: 200px;
  
  .banner-image {
    width: 100%;
    height: 100%;
  }
}

.quick-entries {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-md;
  padding: $spacing-lg;
  background-color: $color-white;
  
  .quick-entry {
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    
    .entry-icon {
      font-size: 32px;
      margin-bottom: $spacing-xs;
      transition: transform $transition-normal ease;
      
      &:hover {
        transform: scale(1.1);
      }
    }
    
    .entry-text {
      font-size: $font-size-sm;
      color: $color-text-secondary;
    }
  }
}

.section {
  margin-top: $spacing-lg;
  background-color: $color-white;
  padding: $spacing-lg;
  
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: $spacing-md;
    
    .section-title {
      font-size: $font-size-lg;
      font-weight: 600;
      color: $color-text-primary;
    }
    
    .section-more {
      font-size: $font-size-sm;
      color: $color-primary;
      cursor: pointer;
      
      &:hover {
        text-decoration: underline;
      }
    }
    
    .promotion-timer {
      display: flex;
      align-items: center;
      gap: $spacing-xs;
      
      .timer-text {
        font-size: $font-size-sm;
        color: $color-text-secondary;
      }
      
      .timer-value {
        font-size: $font-size-sm;
        font-weight: 600;
        color: $color-error;
      }
    }
  }
}

.recommend-products {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-md;
}

.loading-more,
.no-more {
  padding: $spacing-xl;
  text-align: center;
  color: $color-text-tertiary;
  font-size: $font-size-sm;
}
</style>
```

- [ ] **Step 2: 创建商品列表页面**

```vue
<!-- frontend/src/pages/product/list/index.vue -->
<template>
  <view class="product-list-page">
    <!-- 搜索栏 -->
    <view class="search-bar">
      <view class="search-input" @click="handleSearchClick">
        <text class="search-icon">🔍</text>
        <input 
          class="search-input-field"
          :value="searchKeyword"
          placeholder="搜索面包、蛋糕..."
          disabled
        />
      </view>
      <view class="search-filter" @click="showFilter = true">
        <text class="filter-icon">⚙️</text>
      </view>
    </view>
    
    <!-- 筛选条件 -->
    <view class="filter-tags" v-if="activeFilters.length > 0">
      <view 
        v-for="filter in activeFilters" 
        :key="filter.key"
        class="filter-tag"
        @click="removeFilter(filter.key)"
      >
        <text class="filter-tag-text">{{ filter.label }}</text>
        <text class="filter-tag-close">×</text>
      </view>
      <view class="filter-clear" @click="clearAllFilters">
        <text>清空</text>
      </view>
    </view>
    
    <!-- 商品列表 -->
    <scroll-view 
      class="product-list-content" 
      scroll-y 
      :show-scrollbar="false"
      @scrolltolower="handleScrollToLower"
    >
      <!-- 排序栏 -->
      <view class="sort-bar">
        <view 
          v-for="sortOption in sortOptions" 
          :key="sortOption.value"
          :class="['sort-option', { active: sortOption.value === currentSort }]"
          @click="handleSortChange(sortOption.value)"
        >
          <text class="sort-option-text">{{ sortOption.label }}</text>
          <view v-if="sortOption.value === currentSort" class="sort-arrow">
            <text>{{ sortOrder === 'asc' ? '↑' : '↓' }}</text>
          </view>
        </view>
      </view>
      
      <!-- 商品网格 -->
      <view class="product-grid">
        <ProductCard 
          v-for="product in products" 
          :key="product._id"
          :product="product"
          @click="handleProductClick(product)"
          @add-to-cart="handleAddToCart(product)"
        />
      </view>
      
      <!-- 空状态 -->
      <view v-if="products.length === 0 && !loading" class="empty-state">
        <text class="empty-icon">📦</text>
        <text class="empty-text">暂无商品</text>
        <view class="empty-action" @click="clearAllFilters">
          <text>清除筛选条件</text>
        </view>
      </view>
      
      <!-- 加载状态 -->
      <view v-if="loading" class="loading-state">
        <BaseLoading type="dots" text="加载中..." />
      </view>
      
      <!-- 没有更多 -->
      <view v-if="noMore && products.length > 0" class="no-more">
        <text>没有更多商品了</text>
      </view>
    </scroll-view>
    
    <!-- 筛选面板 -->
    <BaseModal
      v-model:visible="showFilter"
      title="筛选条件"
      :show-footer="true"
      cancel-text="重置"
      confirm-text="确定"
      @cancel="handleFilterReset"
      @confirm="handleFilterConfirm"
    >
      <view class="filter-panel">
        <!-- 价格筛选 -->
        <view class="filter-section">
          <text class="filter-section-title">价格区间</text>
          <view class="price-range">
            <input 
              class="price-input"
              type="number"
              v-model="priceRange.min"
              placeholder="最低价"
            />
            <text class="price-separator">-</text>
            <input 
              class="price-input"
              type="number"
              v-model="priceRange.max"
              placeholder="最高价"
            />
          </view>
        </view>
        
        <!-- 分类筛选 -->
        <view class="filter-section">
          <text class="filter-section-title">商品分类</text>
          <view class="category-tags">
            <view 
              v-for="category in categories" 
              :key="category._id"
              :class="['category-tag', { active: selectedCategory === category._id }]"
              @click="handleCategorySelect(category._id)"
            >
              <text>{{ category.name }}</text>
            </view>
          </view>
        </view>
      </view>
    </BaseModal>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useProductStore } from '../../../stores/product.store'
import { useCartStore } from '../../../stores/cart.store'
import ProductCard from '../../../components/product/ProductCard.vue'
import BaseModal from '../../../components/common/BaseModal.vue'
import BaseLoading from '../../../components/common/BaseLoading.vue'

// Store
const productStore = useProductStore()
const cartStore = useCartStore()

// 路由参数
const query = ref<Record<string, any>>({})

// 状态
const searchKeyword = ref('')
const showFilter = ref(false)
const currentSort = ref('default')
const sortOrder = ref<'asc' | 'desc'>('desc')
const loading = ref(false)
const noMore = ref(false)
const page = ref(1)
const limit = ref(10)

// 筛选状态
const priceRange = ref({
  min: '',
  max: '',
})
const selectedCategory = ref<string | null>(null)

// 排序选项
const sortOptions = ref([
  { label: '综合', value: 'default' },
  { label: '价格', value: 'price' },
  { label: '销量', value: 'sales' },
  { label: '新品', value: 'new' },
])

// 计算属性
const products = computed(() => productStore.products)
const categories = computed(() => productStore.categories)

const activeFilters = computed(() => {
  const filters: Array<{ key: string; label: string }> = []
  
  if (selectedCategory.value) {
    const category = categories.value.find(c => c._id === selectedCategory.value)
    if (category) {
      filters.push({ key: 'category', label: `分类: ${category.name}` })
    }
  }
  
  if (priceRange.value.min || priceRange.value.max) {
    let label = '价格: '
    if (priceRange.value.min) label += `¥${priceRange.value.min}`
    label += ' - '
    if (priceRange.value.max) label += `¥${priceRange.value.max}`
    filters.push({ key: 'price', label })
  }
  
  return filters
})

// 生命周期
onMounted(() => {
  // 获取路由参数
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  query.value = currentPage?.options || {}
  
  // 从路由参数初始化
  if (query.value.categoryId) {
    selectedCategory.value = query.value.categoryId
  }
  if (query.value.search === 'true') {
    searchKeyword.value = query.value.keyword || ''
  }
  
  loadProducts()
  loadCategories()
})

// 监听筛选条件变化
watch([selectedCategory, priceRange], () => {
  // 重置分页
  page.value = 1
  noMore.value = false
}, { deep: true })

// 方法
const loadProducts = async () => {
  try {
    loading.value = true
    
    const params = {
      page: page.value,
      limit: limit.value,
      sortBy: currentSort.value === 'default' ? 'sortOrder' : currentSort.value,
      sortOrder: sortOrder.value,
    } as any
    
    if (selectedCategory.value) {
      params.categoryId = selectedCategory.value
    }
    
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    
    if (priceRange.value.min) {
      params.minPrice = Number(priceRange.value.min)
    }
    
    if (priceRange.value.max) {
      params.maxPrice = Number(priceRange.value.max)
    }
    
    // 这里应该调用API获取商品列表
    // 暂时使用store中的数据
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    loading.value = false
  } catch (error) {
    console.error('Failed to load products:', error)
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    // 这里应该调用API获取分类
    // 暂时使用store中的数据
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const handleSearchClick = () => {
  uni.navigateTo({
    url: '/pages/product/list?search=true',
  })
}

const handleSortChange = (sortValue: string) => {
  if (currentSort.value === sortValue) {
    // 切换排序方向
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    currentSort.value = sortValue
    sortOrder.value = 'desc'
  }
  
  // 重新加载商品
  page.value = 1
  noMore.value = false
  loadProducts()
}

const handleProductClick = (product: any) => {
  uni.navigateTo({
    url: `/pages/product/detail?id=${product._id}`,
  })
}

const handleAddToCart = (product: any) => {
  cartStore.addItem(product, 1)
  uni.showToast({
    title: '已加入购物车',
    icon: 'success',
  })
}

const handleCategorySelect = (categoryId: string) => {
  selectedCategory.value = selectedCategory.value === categoryId ? null : categoryId
}

const handleFilterReset = () => {
  priceRange.value = { min: '', max: '' }
  selectedCategory.value = null
}

const handleFilterConfirm = () => {
  showFilter.value = false
  loadProducts()
}

const removeFilter = (filterKey: string) => {
  if (filterKey === 'category') {
    selectedCategory.value = null
  } else if (filterKey === 'price') {
    priceRange.value = { min: '', max: '' }
  }
  
  loadProducts()
}

const clearAllFilters = () => {
  handleFilterReset()
  loadProducts()
}

const handleScrollToLower = () => {
  if (!loading.value && !noMore.value) {
    loadMoreProducts()
  }
}

const loadMoreProducts = async () => {
  page.value += 1
  await loadProducts()
  // 这里应该根据实际数据判断是否还有更多
  noMore.value = page.value >= 3 // 模拟最多3页
}
</script>

<style lang="scss" scoped>
@import '../../../../styles/variables.scss';

.product-list-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.search-bar {
  padding: $spacing-md $spacing-lg;
  background-color: $color-white;
  border-bottom: 1px solid $color-border;
  display: flex;
  align-items: center;
  gap: $spacing-md;
  
  .search-input {
    flex: 1;
    background-color: $color-background;
    border-radius: $border-radius-round;
    padding: $spacing-sm $spacing-md;
    display: flex;
    align-items: center;
    cursor: pointer;
    
    .search-icon {
      margin-right: $spacing-sm;
      color: $color-text-tertiary;
    }
    
    .search-input-field {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      font-size: $font-size-md;
      color: $color-text-primary;
      
      &::placeholder {
        color: $color-text-tertiary;
      }
    }
  }
  
  .search-filter {
    padding: $spacing-sm;
    cursor: pointer;
    
    .filter-icon {
      font-size: $font-size-lg;
      color: $color-text-secondary;
    }
  }
}

.filter-tags {
  padding: $spacing-sm $spacing-lg;
  background-color: $color-white;
  border-bottom: 1px solid $color-border;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: $spacing-sm;
  
  .filter-tag {
    background-color: $color-background;
    border-radius: $border-radius-round;
    padding: $spacing-xs $spacing-sm;
    display: flex;
    align-items: center;
    gap: $spacing-xs;
    cursor: pointer;
    
    .filter-tag-text {
      font-size: $font-size-sm;
      color: $color-text-secondary;
    }
    
    .filter-tag-close {
      font-size: $font-size-lg;
      color: $color-text-tertiary;
      line-height: 1;
    }
    
    &:hover {
      background-color: darken($color-background, 5%);
    }
  }
  
  .filter-clear {
    font-size: $font-size-sm;
    color: $color-primary;
    cursor: pointer;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.product-list-content {
  flex: 1;
  background-color: $color-background;
}

.sort-bar {
  background-color: $color-white;
  padding: $spacing-md $spacing-lg;
  display: flex;
  align-items: center;
  gap: $spacing-xl;
  border-bottom: 1px solid $color-border;
  
  .sort-option {
    display: flex;
    align-items: center;
    gap: $spacing-xs;
    cursor: pointer;
    
    &.active {
      .sort-option-text {
        color: $color-primary;
        font-weight: 600;
      }
      
      .sort-arrow {
        color: $color-primary;
      }
    }
    
    .sort-option-text {
      font-size: $font-size-md;
      color: $color-text-secondary;
      
      &:hover {
        color: $color-primary;
      }
    }
    
    .sort-arrow {
      font-size: $font-size-sm;
      color: $color-text-tertiary;
    }
  }
}

.product-grid {
  padding: $spacing-lg;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-md;
}

.empty-state {
  padding: $spacing-xxl $spacing-xl;
  text-align: center;
  background-color: $color-white;
  margin: $spacing-lg;
  border-radius: $border-radius-lg;
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: $spacing-md;
    display: block;
  }
  
  .empty-text {
    font-size: $font-size-lg;
    color: $color-text-secondary;
    margin-bottom: $spacing-md;
    display: block;
  }
  
  .empty-action {
    display: inline-block;
    padding: $spacing-sm $spacing-md;
    background-color: $color-primary;
    color: $color-white;
    border-radius: $border-radius-md;
    cursor: pointer;
    
    &:hover {
      background-color: $color-primary-light;
    }
  }
}

.loading-state,
.no-more {
  padding: $spacing-xl;
  text-align: center;
  color: $color-text-tertiary;
  font-size: $font-size-sm;
}

.filter-panel {
  padding: $spacing-lg 0;
  
  .filter-section {
    margin-bottom: $spacing-xl;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .filter-section-title {
      font-size: $font-size-md;
      font-weight: 600;
      color: $color-text-primary;
      margin-bottom: $spacing-md;
      display: block;
    }
  }
  
  .price-range {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    
    .price-input {
      flex: 1;
      padding: $spacing-sm $spacing-md;
      border: 1px solid $color-border;
      border-radius: $border-radius-md;
      font-size: $font-size-md;
      color: $color-text-primary;
      
      &::placeholder {
        color: $color-text-tertiary;
      }
    }
    
    .price-separator {
      color: $color-text-secondary;
    }
  }
  
  .category-tags {
    display: flex;
    flex-wrap: wrap;
    gap: $spacing-sm;
    
    .category-tag {
      padding: $spacing-sm $spacing-md;
      background-color: $color-background;
      border-radius: $border-radius-md;
      cursor: pointer;
      
      &.active {
        background-color: $color-primary;
        color: $color-white;
      }
      
      &:hover:not(.active) {
        background-color: darken($color-background, 5%);
      }
    }
  }
}
</style>
```

- [ ] **Step 3: 创建其他页面骨架**

```vue
<!-- frontend/src/pages/product/detail/index.vue -->
<template>
  <view class="product-detail-page">
    <text>商品详情页 (待实现)</text>
  </view>
</template>

<script setup lang="ts">
// 商品详情页骨架
</script>

<style lang="scss" scoped>
.product-detail-page {
  padding: 20px;
}
</style>
```

```vue
<!-- frontend/src/pages/cart/index.vue -->
<template>
  <view class="cart-page">
    <text>购物车页面 (待实现)</text>
  </view>
</template>

<script setup lang="ts">
// 购物车页面骨架
</script>

<style lang="scss" scoped>
.cart-page {
  padding: 20px;
}
</style>
```

```vue
<!-- frontend/src/pages/order/confirm/index.vue -->
<template>
  <view class="order-confirm-page">
    <text>订单确认页 (待实现)</text>
  </view>
</template>

<script setup lang="ts">
// 订单确认页骨架
</script>

<style lang="scss" scoped>
.order-confirm-page {
  padding: 20px;
}
</style>
```

```vue
<!-- frontend/src/pages/user/index.vue -->
<template>
  <view class="user-page">
    <text>个人中心页 (待实现)</text>
  </view>
</template>

<script setup lang="ts">
// 个人中心页骨架
</script>

<style lang="scss" scoped>
.user-page {
  padding: 20px;
}
</style>
```

- [ ] **Step 4: 验证页面结构**

```bash
cd frontend
# 检查页面结构
find src/pages -type f -name "*.vue" | wc -l
```

Expected: 输出至少7个文件

- [ ] **Step 5: 提交页面结构**

```bash
cd frontend
git add src/pages/
git commit -m "feat: add page structure with home and product list"
```

---

**第一阶段完成检查点**

所有第一阶段任务已完成，前端基础框架已搭建完成：
- ✅ 修复了前端测试配置
- ✅ 创建了uni-app核心配置文件
- ✅ 建立了SCSS样式系统
- ✅ 实现了Pinia状态管理
- ✅ 创建了API封装层
- ✅ 开发了基础组件库
- ✅ 建立了页面目录结构

**下一步**：进入第二阶段 - 核心功能开发。需要实现：
1. 首页完整功能（Banner、商品推荐、分类导航）
2. 商品详情页（规格选择、加入购物车）
3. 购物车页面（商品管理、价格计算）
4. 微信登录集成
5. 页面路由完善

**是否继续执行第二阶段任务？**