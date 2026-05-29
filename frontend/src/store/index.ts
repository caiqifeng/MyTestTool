// frontend/src/store/index.ts
export { useUserStore } from './user.store'
export { useCartStore } from './cart.store'
export { useProductStore } from './product.store'
export { useOrderStore } from './order.store'

// 统一初始化store
export const initializeStores = () => {
  console.log('Stores initialized')
}