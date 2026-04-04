import { createSSRApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import * as Pinia from 'pinia'
import vant from 'vant'
import 'vant/lib/index.css'

// 创建应用实例
export function createApp() {
  const app = createSSRApp(App)

  // 初始化Pinia状态管理
  const pinia = createPinia()
  app.use(pinia)

  // 注册Vant组件库
  app.use(vant)

  // 全局属性
  app.config.globalProperties.$pinia = pinia

  return {
    app,
    Pinia // 兼容旧版uni-app的Pinia导出
  }
}

// 导出createPinia方法供页面使用
export { createPinia }

// 导出uni-app类型
declare module '@dcloudio/uni-app' {
  interface Uni {
    $pinia?: typeof Pinia
  }
}

// 全局类型声明
declare global {
  interface Window {
    __PINIA__?: any
  }
}

// 开发环境调试
if (process.env.NODE_ENV === 'development') {
  // 添加调试工具
  const win = window as any
  win.__VUE_DEVTOOLS_GLOBAL_HOOK__ = win.__VUE_DEVTOOLS_GLOBAL_HOOK__ || {}

  // 打印环境信息
  console.log('🚀 Break面包店小程序启动')
  console.log('📱 运行环境:', process.env.VUE_APP_PLATFORM)
  console.log('🔧 构建模式:', process.env.NODE_ENV)
  console.log('📦 版本:', process.env.VUE_APP_VERSION)
}