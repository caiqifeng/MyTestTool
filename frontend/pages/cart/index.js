Page({
  data: {
    editMode: false,
    selectedItems: [],
    items: [
      {
        id: '1',
        productId: '1',
        name: '奶油可颂',
        price: 18,
        quantity: 2,
        image: '/static/products/large/cart-croissant.jpg',
        specs: null,
      },
      {
        id: '2',
        productId: '2',
        name: '巧克力蛋糕',
        price: 68,
        quantity: 1,
        image: '/static/products/large/cart-chocolate-cake.jpg',
        specs: { size: '6寸', flavor: '巧克力' },
      },
    ],
    coupon: null,
    selectedCount: 0,
    totalQuantity: 0,
    totalPrice: 0,
    isAllSelected: false,
  },

  onLoad: function() {
    console.log('购物车页面加载')
    this.calculateTotals()
  },

  calculateTotals: function() {
    const items = this.data.items
    const selectedItems = this.data.selectedItems

    const totalQuantity = items.reduce((sum, item) => sum + item.quantity, 0)
    const totalPrice = items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    const selectedCount = selectedItems.length
    const isAllSelected = selectedCount > 0 && selectedCount === items.length

    this.setData({
      totalQuantity: totalQuantity,
      totalPrice: totalPrice,
      selectedCount: selectedCount,
      isAllSelected: isAllSelected,
    })
  },

  toggleEditMode: function() {
    const newEditMode = !this.data.editMode
    this.setData({
      editMode: newEditMode,
    })
  },

  toggleSelect: function(e) {
    const itemId = e.currentTarget.dataset.id
    const selectedItems = this.data.selectedItems
    const index = selectedItems.indexOf(itemId)

    if (index === -1) {
      selectedItems.push(itemId)
    } else {
      selectedItems.splice(index, 1)
    }

    this.setData({
      selectedItems: selectedItems,
    })
    this.calculateTotals()
  },

  toggleSelectAll: function() {
    const items = this.data.items
    const selectedItems = this.data.selectedItems
    const isAllSelected = this.data.isAllSelected

    if (isAllSelected) {
      // 取消全选
      this.setData({
        selectedItems: [],
      })
    } else {
      // 全选
      const allItemIds = items.map(item => item.id)
      this.setData({
        selectedItems: allItemIds,
      })
    }
    this.calculateTotals()
  },

  decreaseQuantity: function(e) {
    const itemId = e.currentTarget.dataset.id
    const items = this.data.items
    const itemIndex = items.findIndex(item => item.id === itemId)

    if (itemIndex !== -1 && items[itemIndex].quantity > 1) {
      items[itemIndex].quantity -= 1
      this.setData({
        items: items,
      })
      this.calculateTotals()
    }
  },

  increaseQuantity: function(e) {
    const itemId = e.currentTarget.dataset.id
    const items = this.data.items
    const itemIndex = items.findIndex(item => item.id === itemId)

    if (itemIndex !== -1) {
      items[itemIndex].quantity += 1
      this.setData({
        items: items,
      })
      this.calculateTotals()
    }
  },

  removeItem: function(e) {
    const itemId = e.currentTarget.dataset.id
    const items = this.data.items.filter(item => item.id !== itemId)

    this.setData({
      items: items,
    })
    this.calculateTotals()

    wx.showToast({
      title: '已删除',
      icon: 'success',
    })
  },

  deleteSelected: function() {
    const selectedItems = this.data.selectedItems
    const items = this.data.items.filter(item => !selectedItems.includes(item.id))

    this.setData({
      items: items,
      selectedItems: [],
    })
    this.calculateTotals()

    wx.showToast({
      title: '已删除选中商品',
      icon: 'success',
    })
  },

  handleSettle: function() {
    if (this.data.editMode) {
      this.deleteSelected()
    } else if (this.data.selectedCount > 0) {
      console.log('去结算')
      wx.navigateTo({
        url: '/pages/order-confirm/index',
      })
    }
  },

  handleGoHome: function() {
    wx.switchTab({
      url: '/pages/index/index',
    })
  },
})