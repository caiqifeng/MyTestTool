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