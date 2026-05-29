<template>
  <view class="page-container">
    <view class="address-list-page">
      <!-- 头部 -->
      <view class="address-header">
        <text class="address-title">收货地址</text>
      </view>

      <!-- 地址列表 -->
      <view class="addresses-section">
        <view v-if="isLoading" class="loading-section">
          <text class="loading-text">加载中...</text>
        </view>

        <view v-else-if="error" class="error-section">
          <text class="error-text">{{ error }}</text>
          <view class="retry-btn" @click="fetchAddresses">
            <text class="retry-text">重试</text>
          </view>
        </view>

        <view v-else-if="addresses.length === 0" class="empty-section">
          <view class="empty-icon">📍</view>
          <text class="empty-text">暂无收货地址</text>
          <text class="empty-subtext">添加收货地址，方便购物</text>
        </view>

        <view v-else class="addresses-list">
          <view
            v-for="address in addresses"
            :key="address._id"
            class="address-card"
            :class="{ 'default': address.isDefault }"
          >
            <!-- 地址信息 -->
            <view class="address-info">
              <view class="address-main">
                <text class="address-name">{{ address.name }}</text>
                <text class="address-phone">{{ address.phone }}</text>
                <text v-if="address.isDefault" class="default-badge">默认</text>
              </view>
              <text class="address-detail">
                {{ address.province }}{{ address.city }}{{ address.district }}{{ address.detail }}
              </text>
            </view>

            <!-- 操作按钮 -->
            <view class="address-actions">
              <view class="action-left">
                <view class="action-item" @click="handleEditAddress(address)">
                  <text class="action-text">编辑</text>
                </view>
                <view class="action-item" @click="handleDeleteAddress(address._id)">
                  <text class="action-text">删除</text>
                </view>
              </view>
              <view class="action-right">
                <view
                  v-if="!address.isDefault"
                  class="action-item set-default"
                  @click="handleSetDefault(address._id)"
                >
                  <text class="action-text">设为默认</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 添加地址按钮 -->
      <view class="add-address-section">
        <view class="add-address-btn" @click="handleAddAddress">
          <text class="add-icon">+</text>
          <text class="add-text">添加新地址</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { addressApi } from '../../utils/api/address.api'

interface Address {
  _id: string
  userId: string
  name: string
  phone: string
  province: string
  city: string
  district: string
  detail: string
  postalCode?: string
  isDefault: boolean
  createdAt: string
  updatedAt: string
}

const addresses = ref<Address[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)

const fetchAddresses = async () => {
  isLoading.value = true
  error.value = null

  try {
    const response = await addressApi.getAddresses()
    if (response.success && response.data.addresses) {
      addresses.value = response.data.addresses
    } else {
      throw new Error(response.message || '获取地址列表失败')
    }
  } catch (err: any) {
    error.value = err.message || '获取地址列表失败'
    console.error('获取地址列表失败:', err)
  } finally {
    isLoading.value = false
  }
}

const handleAddAddress = () => {
  uni.navigateTo({
    url: '/pages/address-edit/index'
  })
}

const handleEditAddress = (address: Address) => {
  uni.navigateTo({
    url: `/pages/address-edit/index?id=${address._id}`
  })
}

const handleDeleteAddress = (addressId: string) => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这个地址吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await addressApi.deleteAddress(addressId)
          uni.showToast({
            title: '删除成功',
            icon: 'success'
          })
          // 重新加载地址列表
          fetchAddresses()
        } catch (err: any) {
          uni.showToast({
            title: err.message || '删除失败',
            icon: 'none'
          })
        }
      }
    }
  })
}

const handleSetDefault = async (addressId: string) => {
  try {
    await addressApi.setDefaultAddress(addressId)
    uni.showToast({
      title: '已设为默认地址',
      icon: 'success'
    })
    // 重新加载地址列表
    fetchAddresses()
  } catch (err: any) {
    uni.showToast({
      title: err.message || '设置失败',
      icon: 'none'
    })
  }
}

onMounted(() => {
  fetchAddresses()
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.address-list-page {
  padding-bottom: 120rpx; /* 为添加按钮留空间 */
}

.address-header {
  padding: $spacing-lg $spacing-md;
  background-color: $color-white;
  border-bottom: 1px solid $color-border;

  .address-title {
    font-size: $font-size-xl;
    font-weight: 500;
    color: $color-text-primary;
  }
}

.addresses-section {
  padding: $spacing-md;

  .loading-section,
  .error-section,
  .empty-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: $spacing-xl 0;
    background-color: $color-white;
    border-radius: $border-radius-lg;
  }

  .loading-text,
  .error-text,
  .empty-text {
    font-size: $font-size-md;
    font-weight: 400;
    color: $color-text-secondary;
    margin-bottom: $spacing-md;
  }

  .retry-btn {
    background-color: $color-primary;
    border-radius: $border-radius-lg;
    padding: $spacing-sm $spacing-lg;

    .retry-text {
      color: $color-white;
      font-weight: 500;
      font-size: $font-size-md;
    }
  }

  .empty-icon {
    font-size: 80rpx;
    margin-bottom: $spacing-md;
  }

  .empty-subtext {
    font-size: $font-size-xs;
    font-weight: 300;
    color: $color-text-secondary;
  }
}

.addresses-list {
  .address-card {
    background-color: $color-white;
    border-radius: $border-radius-lg;
    margin-bottom: $spacing-md;
    overflow: hidden;

    &:last-child {
      margin-bottom: 0;
    }

    &.default {
      border: 1px solid $color-primary;
      background-color: rgba($color-primary, 0.05);
    }
  }

  .address-info {
    padding: $spacing-md;

    .address-main {
      display: flex;
      align-items: center;
      margin-bottom: $spacing-xs;
      gap: $spacing-sm;

      .address-name {
        font-size: $font-size-md;
        font-weight: 500;
        color: $color-text-primary;
      }

      .address-phone {
        font-size: $font-size-sm;
        font-weight: 300;
        color: $color-text-secondary;
      }

      .default-badge {
        font-size: $font-size-xs;
        font-weight: 400;
        color: $color-primary;
        background-color: rgba($color-primary, 0.1);
        padding: 2rpx 8rpx;
        border-radius: $border-radius-sm;
      }
    }

    .address-detail {
      display: block;
      font-size: $font-size-sm;
      font-weight: 300;
      color: $color-text-secondary;
      line-height: 1.4;
    }
  }

  .address-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $spacing-md;
    border-top: 1px solid $color-border;
    background-color: $color-background;

    .action-left,
    .action-right {
      display: flex;
      gap: $spacing-lg;
    }

    .action-item {
      font-size: $font-size-sm;
      color: $color-text-secondary;

      &.set-default {
        color: $color-primary;
      }
    }
  }
}

.add-address-section {
  position: fixed;
  bottom: env(safe-area-inset-bottom);
  left: 0;
  right: 0;
  background-color: $color-white;
  border-top: 1px solid $color-border;
  padding: $spacing-md;

  .add-address-btn {
    background-color: $color-accent;
    border-radius: $border-radius-lg;
    padding: $spacing-md;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: $spacing-sm;

    .add-icon {
      font-size: $font-size-lg;
      color: $color-white;
    }

    .add-text {
      color: $color-white;
      font-weight: 500;
      font-size: $font-size-md;
    }
  }
}
</style>