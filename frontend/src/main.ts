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