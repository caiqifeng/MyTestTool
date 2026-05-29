// frontend/src/store/order.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { orderApi } from '../utils/api/order.api'

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
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // getters
  const getCurrentOrder = computed(() => currentOrder.value)
  const getOrders = computed(() => orders.value)
  const getAddresses = computed(() => addresses.value)
  const getCoupons = computed(() => coupons.value)
  const getIsLoading = computed(() => isLoading.value)
  const getError = computed(() => error.value)

  const getDefaultAddress = computed(() => {
    return addresses.value.find(addr => addr.isDefault) || addresses.value[0]
  })

  // 工具函数：转换后端数据为前端格式
  const transformBackendOrder = (backendOrder: any): Order => ({
    id: backendOrder._id,
    orderNo: backendOrder.orderNumber,
    status: backendOrder.orderStatus,
    totalAmount: backendOrder.subtotal,
    discountAmount: backendOrder.discount,
    shippingFee: backendOrder.deliveryFee,
    finalAmount: backendOrder.total,
    items: backendOrder.items.map((item: any) => ({
      productId: item.productId,
      name: item.name,
      price: item.price,
      quantity: item.quantity,
      image: item.image,
      specs: item.specs || {}
    })),
    address: {
      id: backendOrder.deliveryAddressId || '',
      name: '默认地址', // 需要从地址API获取详细信息
      phone: '',
      province: '',
      city: '',
      district: '',
      detail: '',
      isDefault: true
    },
    createdAt: backendOrder.createdAt,
    paidAt: backendOrder.paidAt,
    shippedAt: backendOrder.shippedAt,
    deliveredAt: backendOrder.deliveredAt
  })

  // actions
  const fetchOrders = async (params?: any) => {
    try {
      isLoading.value = true
      error.value = null
      const response = await orderApi.getOrders(params)
      if (response.success && response.data.orders) {
        orders.value = response.data.orders.map(transformBackendOrder)
      } else {
        error.value = response.message || '获取订单列表失败'
      }
    } catch (err: any) {
      error.value = err.message || '请求订单列表失败'
      console.error('获取订单列表失败:', err)
    } finally {
      isLoading.value = false

    }
  }

  const fetchOrderById = async (id: string) => {
    try {
      isLoading.value = true
      error.value = null
      const response = await orderApi.getOrder(id)
      if (response.success && response.data.order) {
        currentOrder.value = transformBackendOrder(response.data.order)
      } else {
        error.value = response.message || '获取订单详情失败'
      }
    } catch (err: any) {
      error.value = err.message || '请求订单详情失败'
      console.error('获取订单详情失败:', err)
    } finally {
      isLoading.value = false

    }
  }

  const createNewOrder = async (orderData: any) => {
    try {
      isLoading.value = true
      error.value = null
      const response = await orderApi.createOrder(orderData)
      if (response.success && response.data.order) {
        currentOrder.value = transformBackendOrder(response.data.order)
        orders.value.unshift(transformBackendOrder(response.data.order))
      } else {
        error.value = response.message || '创建订单失败'
      }
    } catch (err: any) {
      error.value = err.message || '创建订单请求失败'
      console.error('创建订单失败:', err)

    } finally {
      isLoading.value = false
    }
  }

  const cancelOrder = async (id: string) => {
    try {
      isLoading.value = true
      error.value = null
      const response = await orderApi.cancelOrder(id)
      if (response.success && response.data.order) {
        const updatedOrder = transformBackendOrder(response.data.order)
        orders.value = orders.value.map(order => order.id === id ? updatedOrder : order)
        if (currentOrder.value && currentOrder.value.id === id) {
          currentOrder.value = updatedOrder
        }
      } else {
        error.value = response.message || '取消订单失败'
      }
    } catch (err: any) {
      error.value = err.message || '取消订单请求失败'
      console.error('取消订单失败:', err)

    } finally {
      isLoading.value = false
    }
  }

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

  const addAddress = async (addressData: Omit<Address, 'id'>) => {
    // 需要先创建address.api.ts
    // 暂用本地模拟
    const newAddress: Address = {
      ...addressData,
      id: Date.now().toString()
    }
    addresses.value.push(newAddress)
  }

  const updateAddress = async (id: string, updates: Partial<Address>) => {
    const index = addresses.value.findIndex(addr => addr.id === id)
    if (index !== -1) {
      if (updates.isDefault) {
        addresses.value = addresses.value.map(addr => ({
          ...addr,
          isDefault: addr.id === id
        }))
      } else {
        addresses.value[index] = { ...addresses.value[index], ...updates }
      }
    }
  }

  const deleteAddress = async (id: string) => {
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
    isLoading,
    error,

    // getters
    getCurrentOrder,
    getOrders,
    getAddresses,
    getCoupons,
    getIsLoading,
    getError,
    getDefaultAddress,

    // actions
    fetchOrders,
    fetchOrderById,
    createNewOrder,
    cancelOrder,
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