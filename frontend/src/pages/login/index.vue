<template>
  <view class="page-container">
    <view class="login-page">
      <!-- 头部 -->
      <view class="login-header">
        <text class="login-title">登录</text>
        <text class="login-subtitle">欢迎来到面包店</text>
      </view>

      <!-- 表单 -->
      <view class="login-form">
        <view class="form-item">
          <text class="form-label">用户名</text>
          <input
            class="form-input"
            type="text"
            placeholder="请输入用户名"
            v-model="form.username"
          />
        </view>

        <view class="form-item">
          <text class="form-label">密码</text>
          <input
            class="form-input"
            type="password"
            placeholder="请输入密码"
            v-model="form.password"
            @confirm="handleLogin"
          />
        </view>

        <view class="form-actions">
          <view class="login-btn" @click="handleLogin">
            <text class="login-btn-text">登录</text>
          </view>

          <view class="register-link" @click="handleRegister">
            <text class="register-text">还没有账号？立即注册</text>
          </view>
        </view>

        <!-- 第三方登录 -->
        <view class="social-login">
          <text class="social-title">其他登录方式</text>
          <view class="social-buttons">
            <view class="social-btn wechat" @click="handleWechatLogin">
              <text class="social-icon">💬</text>
              <text class="social-text">微信登录</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '../../store/user.store'
import { authApi } from '../../utils/api/auth.api'

const userStore = useUserStore()

const form = ref({
  username: '',
  password: '',
})

const loading = ref(false)

const handleLogin = async () => {
  if (!form.value.username.trim() || !form.value.password.trim()) {
    uni.showToast({
      title: '请输入用户名和密码',
      icon: 'none',
    })
    return
  }

  loading.value = true

  try {
    console.log('登录请求:', form.value)

    // 实际API调用
    const response = await authApi.login({
      username: form.value.username.trim(),
      password: form.value.password.trim()
    })

    userStore.setUserInfo(response.data.user)
    userStore.setToken(response.data.token, response.data.refreshToken)

    uni.showToast({
      title: '登录成功',
      icon: 'success',
    })

    // 跳转回上一页或首页
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)

  } catch (error) {
    console.error('登录失败:', error)
    uni.showToast({
      title: '登录失败，请重试',
      icon: 'none',
    })
  } finally {
    loading.value = false
  }
}

const handleRegister = () => {
  uni.navigateTo({
    url: '/pages/register/index',
  })
}

const handleWechatLogin = () => {
  uni.showToast({
    title: '微信登录功能开发中',
    icon: 'none',
  })
}
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.login-page {
  padding: $spacing-xl $spacing-lg;
}

.login-header {
  text-align: center;
  margin-bottom: $spacing-xl;

  .login-title {
    display: block;
    font-size: $font-size-xxl;
    font-weight: 500;
    color: $color-text-primary;
    margin-bottom: $spacing-sm;
  }

  .login-subtitle {
    display: block;
    font-size: $font-size-md;
    font-weight: 300;
    color: $color-text-secondary;
  }
}

.login-form {
  .form-item {
    margin-bottom: $spacing-lg;

    .form-label {
      display: block;
      font-size: $font-size-md;
      color: $color-text-primary;
      margin-bottom: $spacing-sm;
      font-weight: 400;
    }

    .form-input {
      border: 1px solid $color-border;
      border-radius: $border-radius-lg;
      padding: $spacing-md;
      font-size: $font-size-md;
      color: $color-text-primary;
      background-color: $color-white;
      width: 100%;

      &::placeholder {
        color: $color-text-secondary;
      }
    }
  }

  .form-actions {
    margin-top: $spacing-xl;

    .login-btn {
      background-color: $color-accent;
      border-radius: $border-radius-lg;
      padding: $spacing-md;
      text-align: center;
      margin-bottom: $spacing-lg;

      .login-btn-text {
        color: $color-white;
        font-weight: 500;
        font-size: $font-size-md;
      }
    }

    .register-link {
      text-align: center;

      .register-text {
        color: $color-primary;
        font-size: $font-size-sm;
        font-weight: 300;
      }
    }
  }
}

.social-login {
  margin-top: $spacing-xl;
  padding-top: $spacing-xl;
  border-top: 1px solid $color-border;

  .social-title {
    display: block;
    text-align: center;
    font-size: $font-size-sm;
    font-weight: 300;
    color: $color-text-secondary;
    margin-bottom: $spacing-lg;
  }

  .social-buttons {
    display: flex;
    justify-content: center;

    .social-btn {
      border: 1px solid $color-border;
      border-radius: $border-radius-round;
      padding: $spacing-sm $spacing-lg;
      display: flex;
      align-items: center;
      gap: $spacing-sm;

      &.wechat {
        border-color: #07C160;
        color: #07C160;
      }

      .social-icon {
        font-size: $font-size-lg;
      }

      .social-text {
        font-size: $font-size-md;
      }
    }
  }
}
</style>