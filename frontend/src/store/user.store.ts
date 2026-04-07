// frontend/src/store/user.store.ts
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