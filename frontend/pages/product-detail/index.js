Page({
  data: {
    productId: '',
    product: {},
    selectedSpecs: {},
    isFavorited: false,
    quantity: 1,
    cartTotalQuantity: 0
  },
  onLoad: function(options) {
    console.log('product-detail页面加载，参数:', options)
    if (options && options.id) {
      const productData = this.getProductData(options.id)
      // 计算折扣百分比
      if (productData.originalPrice && productData.originalPrice > 0) {
        productData.discountPercent = Math.round((1 - productData.price / productData.originalPrice) * 100)
      } else {
        productData.discountPercent = 0
      }
      // 计算是否有规格
      productData.hasSpecs = productData.specs && Object.keys(productData.specs).length > 0
      this.setData({
        productId: options.id,
        product: productData
      })
      console.log('加载商品数据:', options.id)

      // 初始化默认规格选择
      const selectedSpecs = {}
      if (productData.specs) {
        Object.keys(productData.specs).forEach(specName => {
          if (productData.specs[specName].length > 0) {
            selectedSpecs[specName] = productData.specs[specName][0]
          }
        })
      }
      this.setData({ selectedSpecs: selectedSpecs })
    }
  },

  getProductData: function(productId) {
    const mockProducts = {
      '1': {
        id: '1',
        name: '奶油可颂',
        description: '新鲜烘焙的奶油可颂，外酥内软，奶香浓郁，早餐下午茶的不二选择。',
        price: 18,
        originalPrice: 22,
        images: [
          '/static/product-detail/carousel-croissant.jpg',
          '/static/product-detail/carousel-bread.jpg',
          '/static/product-detail/carousel-pastries.jpg'
        ],
        categoryId: '1',
        categoryName: '面包',
        stock: 100,
        sales: 152,
        specs: {
          '尺寸': ['小份', '中份', '大份'],
          '口味': ['原味', '巧克力', '抹茶']
        }
      },
      '2': {
        id: '2',
        name: '巧克力蛋糕',
        description: '浓郁的巧克力蛋糕，口感丝滑，巧克力味十足。',
        price: 68,
        originalPrice: 88,
        images: [
          '/static/product-detail/carousel-croissant.jpg',
          '/static/product-detail/carousel-bread.jpg',
          '/static/product-detail/carousel-pastries.jpg'
        ],
        categoryId: '3',
        categoryName: '蛋糕',
        stock: 50,
        sales: 89,
        specs: {
          '尺寸': ['6寸', '8寸', '10寸'],
          '口味': ['巧克力', '抹茶', '草莓']
        }
      }
    };

    return mockProducts[productId] || mockProducts['1'];
  },

  // 选择规格
  selectSpec: function(e) {
    const { specName, value } = e.currentTarget.dataset
    const selectedSpecs = this.data.selectedSpecs
    selectedSpecs[specName] = value
    this.setData({ selectedSpecs: selectedSpecs })
  },

  // 增加数量
  increaseQuantity: function() {
    const quantity = this.data.quantity + 1
    this.setData({ quantity: quantity })
  },

  // 减少数量
  decreaseQuantity: function() {
    const quantity = this.data.quantity
    if (quantity > 1) {
      this.setData({ quantity: quantity - 1 })
    }
  },

  // 加入购物车
  handleAddToCart: function() {
    const { product, selectedSpecs, quantity } = this.data
    const cartItem = {
      productId: product.id,
      name: product.name,
      price: product.price,
      quantity: quantity,
      image: product.images[0],
      specs: selectedSpecs
    }

    // 模拟添加到购物车
    console.log('加入购物车:', cartItem)

    // 更新购物车数量
    const cartTotalQuantity = this.data.cartTotalQuantity + quantity
    this.setData({ cartTotalQuantity: cartTotalQuantity })

    wx.showToast({
      title: '已加入购物车',
      icon: 'success'
    })
  },

  // 立即购买
  handleBuyNow: function() {
    const { product, selectedSpecs, quantity } = this.data
    const cartItem = {
      productId: product.id,
      name: product.name,
      price: product.price,
      quantity: quantity,
      image: product.images[0],
      specs: selectedSpecs
    }

    // 模拟添加到购物车
    console.log('立即购买:', cartItem)

    wx.showToast({
      title: '跳转到订单确认',
      icon: 'none'
    })

    // 实际应用中这里会跳转到订单确认页面
    // wx.navigateTo({
    //   url: '/pages/order-confirm/index'
    // })
  },

  // 导航到其他页面
  handleNavigate: function(e) {
    const type = e.currentTarget.dataset.type

    switch (type) {
      case 'home':
        wx.switchTab({
          url: '/pages/index/index'
        })
        break
      case 'cart':
        wx.switchTab({
          url: '/pages/cart/index'
        })
        break
    }
  },

  // 收藏/取消收藏
  handleFavorite: function() {
    const isFavorited = !this.data.isFavorited
    this.setData({ isFavorited: isFavorited })

    wx.showToast({
      title: isFavorited ? '已收藏' : '已取消收藏',
      icon: 'none'
    })
  },

  onReady: function() {
    console.log('product-detail页面准备完成')
  }
})