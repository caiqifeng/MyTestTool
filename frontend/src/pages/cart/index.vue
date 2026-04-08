<template>
  <view class="page-container">
    <view class="cart-page">
      <!-- 头部 -->
      <view class="cart-header">
        <text class="cart-title">购物车</text>
        <text v-if="cartStore.getSelectedCount > 0" class="cart-edit" @click="toggleEditMode">
          {{ editMode ? '完成' : '编辑' }}
        </text>
      </view>

      <!-- 购物车为空 -->
      <view v-if="cartStore.getTotalQuantity === 0" class="cart-empty">
        <view class="empty-icon">🛒</view>
        <text class="empty-text">购物车是空的</text>
        <view class="empty-action" @click="handleGoHome">
          <text class="empty-action-text">去逛逛</text>
        </view>
      </view>

      <!-- 购物车商品列表 -->
      <view v-else class="cart-content">
        <view class="cart-items">
          <view
            class="cart-item"
            v-for="item in cartStore.getItems"
            :key="item.id"
          >
            <view class="item-select" @click="cartStore.toggleSelect(item.id)">
              <view
                class="select-checkbox"
                :class="{ 'selected': cartStore.selectedItems.includes(item.id) }"
              >
                <text v-if="cartStore.selectedItems.includes(item.id)">✓</text>
              </view>
            </view>

            <image class="item-image" :src="item.image" mode="aspectFill" />

            <view class="item-info">
              <text class="item-name">{{ item.name }}</text>
              <text v-if="item.specs" class="item-specs">
                {{ Object.values(item.specs).join(' ') }}
              </text>
              <view class="item-bottom">
                <text class="item-price">¥{{ item.price }}</text>

                <view class="item-quantity">
                  <text
                    class="quantity-btn"
                    :class="{ 'disabled': item.quantity <= 1 }"
                    @click="handleDecrease(item.id)"
                  >-</text>
                  <text class="quantity-value">{{ item.quantity }}</text>
                  <text class="quantity-btn" @click="handleIncrease(item.id)">+</text>
                </view>
              </view>
            </view>

            <view v-if="editMode" class="item-delete" @click="cartStore.removeItem(item.id)">
              <text class="delete-icon">×</text>
            </view>
          </view>
        </view>

        <!-- 全选 -->
        <view class="cart-select-all">
          <view class="select-all-checkbox" @click="cartStore.toggleSelectAll()">
            <view
              class="select-checkbox"
              :class="{ 'selected': cartStore.getIsAllSelected }"
            >
              <text v-if="cartStore.getIsAllSelected">✓</text>
            </view>
            <text class="select-all-text">全选</text>
          </view>

          <view v-if="!editMode" class="select-all-delete" @click="handleDeleteSelected">
            <text class="delete-text">删除</text>
          </view>
        </view>
      </view>

      <!-- 底部结算栏 -->
      <view v-if="cartStore.getTotalQuantity > 0" class="cart-footer">
        <view class="footer-left">
          <view class="total-price">
            <text class="total-label">合计：</text>
            <text class="total-value">¥{{ cartStore.getTotalPrice.toFixed(2) }}</text>
          </view>
          <text v-if="cartStore.getCoupon" class="coupon-text">
            已使用优惠券：{{ cartStore.getCoupon.name }}
          </text>
        </view>

        <view class="footer-right">
          <view
            class="settle-btn"
            :class="{ 'disabled': cartStore.getSelectedCount === 0 }"
            @click="handleSettle"
          >
            <text class="settle-text">
              {{ editMode ? '删除' : `结算(${cartStore.getSelectedCount})` }}
            </text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCartStore } from '../../store/cart.store'

const cartStore = useCartStore()
const editMode = ref(false)

onMounted(() => {
  // 初始化购物车数据（模拟）
  if (cartStore.getTotalQuantity === 0) {
    cartStore.addItem({
      productId: '1',
      name: '奶油可颂',
      price: 18,
      quantity: 2,
      image: 'https://source.unsplash.com/featured/200x200/?croissant,bakery',
    })
    cartStore.addItem({
      productId: '2',
      name: '巧克力蛋糕',
      price: 68,
      quantity: 1,
      image: 'https://source.unsplash.com/featured/200x200/?chocolate,cake,dessert',
      specs: { size: '6寸', flavor: '巧克力' },
    })
  }
})

const toggleEditMode = () => {
  editMode.value = !editMode.value
}

const handleDecrease = (itemId: string) => {
  const item = cartStore.getItems.find(i => i.id === itemId)
  if (item && item.quantity > 1) {
    cartStore.updateQuantity(itemId, item.quantity - 1)
  }
}

const handleIncrease = (itemId: string) => {
  const item = cartStore.getItems.find(i => i.id === itemId)
  if (item) {
    cartStore.updateQuantity(itemId, item.quantity + 1)
  }
}

const handleDeleteSelected = () => {
  cartStore.selectedItems.forEach(itemId => {
    cartStore.removeItem(itemId)
  })
}

const handleSettle = () => {
  if (editMode.value) {
    handleDeleteSelected()
  } else if (cartStore.getSelectedCount > 0) {
    console.log('去结算')
    uni.navigateTo({
      url: '/pages/order-confirm/index',
    })
  }
}

const handleGoHome = () => {
  uni.switchTab({
    url: '/pages/index/index',
  })
}
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.cart-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.cart-header {
  padding: $spacing-md;
  background-color: $color-white;
  border-bottom: 1px solid $color-border;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cart-title {
  font-size: $font-size-xl;
  font-weight: 600;
  color: $color-text-primary;
}

.cart-edit {
  font-size: $font-size-md;
  color: $color-primary;
}

.cart-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $spacing-xl;

  .empty-icon {
    font-size: 80rpx;
    margin-bottom: $spacing-md;
  }

  .empty-text {
    font-size: $font-size-md;
    color: $color-text-secondary;
    margin-bottom: $spacing-lg;
  }

  .empty-action {
    background-color: $color-primary;
    border-radius: $border-radius-round;
    padding: $spacing-sm $spacing-xl;

    .empty-action-text {
      color: $color-white;
      font-weight: 500;
    }
  }
}

.cart-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 120rpx; /* 为底部结算栏留空间 */
}

.cart-items {
  .cart-item {
    display: flex;
    align-items: center;
    padding: $spacing-md;
    background-color: $color-white;
    margin-bottom: 1px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .item-select {
    margin-right: $spacing-md;
  }

  .select-checkbox {
    width: 40rpx;
    height: 40rpx;
    border: 2px solid $color-border;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;

    &.selected {
      border-color: $color-primary;
      background-color: $color-primary;
      color: $color-white;
    }
  }

  .item-image {
    width: 160rpx;
    height: 160rpx;
    border-radius: $border-radius-sm;
    margin-right: $spacing-md;
  }

  .item-info {
    flex: 1;

    .item-name {
      display: block;
      font-size: $font-size-md;
      color: $color-text-primary;
      margin-bottom: $spacing-xs;
      @include text-ellipsis(1);
    }

    .item-specs {
      display: block;
      font-size: $font-size-sm;
      color: $color-text-tertiary;
      margin-bottom: $spacing-md;
    }

    .item-bottom {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .item-price {
      font-size: $font-size-lg;
      font-weight: 600;
      color: $color-error;
    }

    .item-quantity {
      display: flex;
      align-items: center;
      border: 1px solid $color-border;
      border-radius: $border-radius-round;
      overflow: hidden;

      .quantity-btn {
        width: 60rpx;
        height: 60rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: $font-size-lg;
        color: $color-text-primary;

        &.disabled {
          color: $color-text-tertiary;
        }
      }

      .quantity-value {
        width: 80rpx;
        text-align: center;
        font-size: $font-size-md;
        color: $color-text-primary;
      }
    }
  }

  .item-delete {
    width: 80rpx;
    height: 80rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: $spacing-md;

    .delete-icon {
      font-size: $font-size-xxl;
      color: $color-error;
    }
  }
}

.cart-select-all {
  padding: $spacing-md;
  background-color: $color-white;
  border-top: 1px solid $color-border;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .select-all-checkbox {
    display: flex;
    align-items: center;
  }

  .select-all-text {
    margin-left: $spacing-sm;
    font-size: $font-size-md;
    color: $color-text-primary;
  }

  .select-all-delete {
    .delete-text {
      font-size: $font-size-md;
      color: $color-text-tertiary;
    }
  }
}

.cart-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: $color-white;
  border-top: 1px solid $color-border;
  padding: $spacing-md;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;

  .footer-left {
    .total-price {
      display: flex;
      align-items: baseline;
      margin-bottom: $spacing-xs;
    }

    .total-label {
      font-size: $font-size-sm;
      color: $color-text-secondary;
    }

    .total-value {
      font-size: $font-size-xl;
      font-weight: 600;
      color: $color-error;
    }

    .coupon-text {
      font-size: $font-size-xs;
      color: $color-primary;
    }
  }

  .footer-right {
    .settle-btn {
      background-color: $color-primary;
      border-radius: $border-radius-round;
      padding: $spacing-sm $spacing-xl;

      &.disabled {
        background-color: $color-text-tertiary;
        opacity: 0.5;
      }

      .settle-text {
        color: $color-white;
        font-weight: 500;
        font-size: $font-size-md;
      }
    }
  }
}
</style>