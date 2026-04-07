// frontend/src/store/order.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface Address {
  id: string
  name: string
  phone: string
  province: string
  city: string
  district: string
  detail: string
  isDefault: boolean
}

interface OrderItem {
  productId: string
  name: string
  price: number
  quantity: number
  image: string
  specs?: Record<string, string>
}

interface Order {
  id: string
  orderNo: string
  status: 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled' | 'refunded'
  totalAmount: number
  discountAmount: number
  shippingFee: number
  finalAmount: number
  items: OrderItem[]
  address: Address
  createdAt: string
  paidAt?: string
  shippedAt?: string
  deliveredAt?: string
}

interface OrderState {
  currentOrder: Order | null
  orders: Order[]
  addresses: Address[]
  coupons: Coupon[]
}

interface Coupon {
  id: string
  name: string
  discount: number
  type: 'percentage' | 'fixed'
  minAmount?: number
  expiredAt: string
}

export const useOrderStore = defineStore('order', () => {
  // 状态
  const currentOrder = ref<Order | null>(null)
  const orders = ref<Order[]>([])
  const addresses = ref<Address[]>([])
  const coupons = ref<Coupon[]>([])

  // getters
  const getCurrentOrder = computed(() => currentOrder.value)
  const getOrders = computed(() => orders.value)
  const getAddresses = computed(() => addresses.value)
  const getCoupons = computed(() => coupons.value)

  const getDefaultAddress = computed(() => {
    return addresses.value.find(addr => addr.isDefault) || addresses.value[0]
  })

  // actions
  const setCurrentOrder = (order: Order | null) => {
    currentOrder.value = order
  }

  const setOrders = (newOrders: Order[]) => {
    orders.value = newOrders
  }

  const setAddresses = (newAddresses: Address[]) => {
    addresses.value = newAddresses
  }

  const setCoupons = (newCoupons: Coupon[]) => {
    coupons.value = newCoupons
  }

  const addAddress = (address: Omit<Address, 'id'>) => {
    const newAddress: Address = {
      ...address,
      id: Date.now().toString(),
    }

    if (address.isDefault) {
      addresses.value = addresses.value.map(addr => ({
        ...addr,
        isDefault: false,
      }))
    }

    addresses.value.push(newAddress)
  }

  const updateAddress = (id: string, updates: Partial<Address>) => {
    const index = addresses.value.findIndex(addr => addr.id === id)
    if (index !== -1) {
      if (updates.isDefault) {
        addresses.value = addresses.value.map(addr => ({
          ...addr,
          isDefault: addr.id === id,
        }))
      } else {
        addresses.value[index] = { ...addresses.value[index], ...updates }
      }
    }
  }

  const deleteAddress = (id: string) => {
    addresses.value = addresses.value.filter(addr => addr.id !== id)
  }

  const clearCurrentOrder = () => {
    currentOrder.value = null
  }

  return {
    // 状态
    currentOrder,
    orders,
    addresses,
    coupons,

    // getters
    getCurrentOrder,
    getOrders,
    getAddresses,
    getCoupons,
    getDefaultAddress,

    // actions
    setCurrentOrder,
    setOrders,
    setAddresses,
    setCoupons,
    addAddress,
    updateAddress,
    deleteAddress,
    clearCurrentOrder,
  }
})