// frontend/src/store/cart.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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

interface CartState {
  items: CartItem[]
  selectedItems: string[]
  coupon?: Coupon
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

  // getters
  const getItems = computed(() => items.value)
  const getSelectedItems = computed(() => selectedItems.value)
  const getCoupon = computed(() => coupon.value)

  const getTotalPrice = computed(() => {
    return items.value.reduce((total, item) => {
      if (selectedItems.value.includes(item.id)) {
        return total + (item.price * item.quantity)
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

  // actions
  const addItem = (item: Omit<CartItem, 'id' | 'selected'>) => {
    const existingItem = items.value.find(i => i.productId === item.productId)

    if (existingItem) {
      existingItem.quantity += item.quantity
    } else {
      const newItem: CartItem = {
        ...item,
        id: Date.now().toString(),
        selected: true,
      }
      items.value.push(newItem)
      selectedItems.value.push(newItem.id)
    }
  }

  const removeItem = (itemId: string) => {
    items.value = items.value.filter(item => item.id !== itemId)
    selectedItems.value = selectedItems.value.filter(id => id !== itemId)
  }

  const updateQuantity = (itemId: string, quantity: number) => {
    const item = items.value.find(i => i.id === itemId)
    if (item) {
      item.quantity = quantity > 0 ? quantity : 1
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

  const clearCart = () => {
    items.value = []
    selectedItems.value = []
    coupon.value = undefined
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

    // getters
    getItems,
    getSelectedItems,
    getCoupon,
    getTotalPrice,
    getTotalQuantity,
    getSelectedCount,
    getIsAllSelected,

    // actions
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