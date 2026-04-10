import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError, InternalAxiosRequestConfig, AxiosHeaders } from 'axios'
import { useUserStore } from '../../store/user.store'

// 环境变量配置 - 开发环境使用本地后端
const API_BASE_URL = 'http://localhost:3003/api'

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
  (config: InternalAxiosRequestConfig) => {
    const userStore = useUserStore()
    const token = userStore.token

    if (token) {
      if (!config.headers) {
        config.headers = new AxiosHeaders()
      }
      config.headers.set('Authorization', `Bearer ${token}`)
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
      console.error('Token expired, please login again')
    }

    // 统一错误处理
    const errorMessage = (error.response?.data as any)?.message || '网络错误，请稍后重试'
    console.error('API Error:', errorMessage)

    return Promise.reject(error)
  }
)

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean
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