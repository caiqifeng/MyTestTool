// frontend/src/store/user.store.test.ts
import { describe, it, expect, beforeEach } from '@jest/globals'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from './user.store'

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    // 清除localStorage
    if (typeof window !== 'undefined') {
      window.localStorage.clear()
    }
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
    if (typeof window !== 'undefined') {
      expect(window.localStorage.getItem('token')).toBe(token)
    }
  })

  it('should set token with refresh token', () => {
    const store = useUserStore()
    const token = 'test-token'
    const refreshToken = 'refresh-token'

    store.setToken(token, refreshToken)

    expect(store.token).toBe(token)
    expect(store.refreshToken).toBe(refreshToken)
    if (typeof window !== 'undefined') {
      expect(window.localStorage.getItem('token')).toBe(token)
      expect(window.localStorage.getItem('refreshToken')).toBe(refreshToken)
    }
  })

  it('should clear token on logout', () => {
    const store = useUserStore()
    // 先设置token和用户信息
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
    if (typeof window !== 'undefined') {
      expect(window.localStorage.getItem('token')).toBeNull()
      expect(window.localStorage.getItem('refreshToken')).toBeNull()
    }
  })

  it('should check login status from localStorage', () => {
    if (typeof window === 'undefined') {
      // 跳过Node环境测试
      return
    }

    // 模拟localStorage有token
    window.localStorage.setItem('token', 'saved-token')
    window.localStorage.setItem('refreshToken', 'saved-refresh-token')

    const store = useUserStore()
    store.checkLoginStatus()

    expect(store.token).toBe('saved-token')
    expect(store.refreshToken).toBe('saved-refresh-token')
    expect(store.isLoggedIn).toBe(true)
  })

  it('should not be logged in when no token in localStorage', () => {
    if (typeof window === 'undefined') {
      // 跳过Node环境测试
      return
    }

    // 确保localStorage没有token
    window.localStorage.removeItem('token')
    window.localStorage.removeItem('refreshToken')

    const store = useUserStore()
    store.checkLoginStatus()

    expect(store.token).toBeNull()
    expect(store.isLoggedIn).toBe(false)
  })
})