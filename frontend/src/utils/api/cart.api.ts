import api, { ApiResponse } from './index'

interface CartItem {
  productId: string
  name: string
  price: number
  quantity: number
  image: string
  specs?: Record<string, string>
}

interface Cart {
  _id: string
  userId: string
  items: CartItem[]
  updatedAt: string
}

export const cartApi = {
  // 获取购物车
  getCart: (): Promise<ApiResponse<{ cart: Cart }>> => {
    return api.get('/cart')
  },

  // 添加商品到购物车
  addToCart: (productId: string, quantity: number, specs?: Record<string, string>): Promise<ApiResponse<{ cart: Cart }>> => {
    return api.post('/cart/items', { productId, quantity, specs })
  },

  // 更新购物车商品数量
  updateCartItem: (productId: string, quantity: number): Promise<ApiResponse<{ cart: Cart }>> => {
    return api.put(`/cart/items/${productId}`, { quantity })
  },

  // 删除购物车商品
  removeCartItem: (productId: string): Promise<ApiResponse<{ cart: Cart }>> => {
    return api.delete(`/cart/items/${productId}`)
  },

  // 清空购物车
  clearCart: (): Promise<ApiResponse<{ cart: Cart }>> => {
    return api.delete('/cart')
  },

  // 获取购物车商品数量
  getCartCount: (): Promise<ApiResponse<{ count: number }>> => {
    return api.get('/cart/count')
  }
}