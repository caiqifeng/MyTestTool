// frontend/src/store/cart.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { cartApi } from '../utils/api/cart.api'

interface CartItem {
  id: string
  productId: string
  name: string
  price: number
  quantity: number
  image: string
  selected: boolean
  specs?: Record<string, string>
}

interface Coupon {
  id: string
  name: string
  discount: number
  type: 'percentage' | 'fixed'
  minAmount?: number
}

export const useCartStore = defineStore('cart', () => {
  // 状态
  const items = ref<CartItem[]>([])
  const selectedItems = ref<string[]>([])
  const coupon = ref<Coupon | undefined>(undefined)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // getters
  const getItems = computed(() => items.value)
  const getSelectedItems = computed(() => selectedItems.value)
  const getCoupon = computed(() => coupon.value)
  const getIsLoading = computed(() => isLoading.value)
  const getError = computed(() => error.value)

  const getTotalPrice = computed(() => {
    return items.value.reduce((total, item) => {
      if (selectedItems.value.includes(item.id)) {
        return total + (item.quantity * item.price)
      }
      return total
    }, 0)
  })

  const getTotalQuantity = computed(() => {
    return items.value.reduce((total, item) => total + item.quantity, 0)
  })

  const getSelectedCount = computed(() => {
    return selectedItems.value.length
  })

  const getIsAllSelected = computed(() => {
    if (items.value.length === 0) return false
    return selectedItems.value.length === items.value.length
  })

  // 工具函数：将后端购物车数据转换为前端格式
  const transformBackendCart = (backendCart: any): CartItem[] => {
    return backendCart.items.map((item: any) => ({
      id: item.productId || `cart_${Date.now()}_${item.productId}`, // 使用productId作为id或生成复合id
      productId: item.productId,
      name: item.name,
      price: item.price,
      quantity: item.quantity,
      image: item.image,
      selected: true, // 默认选中
      specs: item.specs || {}
    }))
  }

  // 工具函数：更新本地购物车状态
  const updateLocalCart = (backendCart: any) => {
    const transformedItems = transformBackendCart(backendCart)
    items.value = transformedItems
    selectedItems.value = transformedItems.map(item => item.id)
  }

  // actions
  const fetchCart = async () => {
    try {
      isLoading.value = true
      error.value = null
      const response = await cartApi.getCart()
      if (response.success && response.data.cart) {
        updateLocalCart(response.data.cart)
      } else {
        error.value = response.message || '获取购物车失败'
      }
    } catch (err: any) {
      error.value = err.message || '请求购物车失败'
      console.error('获取购物车失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  const addItem = async (item: Omit<CartItem, 'id' | 'selected'>) => {
    try {
      isLoading.value = true
      error.value = null
      const response = await cartApi.addToCart(item.productId, item.quantity, item.specs)
      if (response.success && response.data.cart) {
        updateLocalCart(response.data.cart)
      } else {
        error.value = response.message || '添加商品到购物车失败'
      }
    } catch (err: any) {
      error.value = err.message || '添加商品到购物车请求失败'
      console.error('添加商品到购物车失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  const removeItem = async (itemId: string) => {
    try {
      isLoading.value = true
      error.value = null
      // 从前端数据中查找对应的productId
      const item = items.value.find(i => i.id === itemId)
      if (item) {
        const response = await cartApi.removeCartItem(item.productId)
        if (response.success && response.data.cart) {
          updateLocalCart(response.data.cart)
        } else {
          error.value = response.message || '删除购物车商品失败'
        }
      } else {
        error.value = '未找到要删除的商品'
      }
    } catch (err: any) {
      error.value = err.message || '删除购物车商品请求失败'
      console.error('删除购物车商品失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  const updateQuantity = async (itemId: string, quantity: number) => {
    try {
      isLoading.value = true
      error.value = null
      // 从前端数据中查找对应的productId
      const item = items.value.find(i => i.id === itemId)
      if (item) {
        const response = await cartApi.updateCartItem(item.productId, quantity)
        if (response.success && response.data.cart) {
          updateLocalCart(response.data.cart)
        } else {
          error.value = response.message || '更新购物车商品数量失败'
        }
      } else {
        error.value = '未找到要更新的商品'
      }
    } catch (err: any) {
      error.value = err.message || '更新购物车商品数量请求失败'
      console.error('更新购物车商品数量失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  const toggleSelect = (itemId: string) => {
    if (selectedItems.value.includes(itemId)) {
      selectedItems.value = selectedItems.value.filter(id => id !== itemId)
    } else {
      selectedItems.value.push(itemId)
    }
  }

  const toggleSelectAll = () => {
    if (getIsAllSelected.value) {
      selectedItems.value = []
    } else {
      selectedItems.value = items.value.map(item => item.id)
    }
  }

  const clearCart = async () => {
    try {
      isLoading.value = true
      error.value = null
      const response = await cartApi.clearCart()
      if (response.success && response.data.cart) {
        updateLocalCart(response.data.cart)
        coupon.value = undefined
      } else {
        error.value = response.message || '清空购物车失败'
      }
    } catch (err: any) {
      error.value = err.message || '清空购物车请求失败'
      console.error('清空购物车失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  const applyCoupon = (newCoupon: Coupon) => {
    coupon.value = newCoupon
  }

  const removeCoupon = () => {
    coupon.value = undefined
  }

  return {
    // 状态
    items,
    selectedItems,
    coupon,
    isLoading,
    error,

    // getters
    getItems,
    getSelectedItems,
    getCoupon,
    getTotalPrice,
    getTotalQuantity,
    getSelectedCount,
    getIsAllSelected,
    getIsLoading,
    getError,

    // actions
    fetchCart,
    addItem,
    removeItem,
    updateQuantity,
    toggleSelect,
    toggleSelectAll,
    clearCart,
    applyCoupon,
    removeCoupon,
  }
})