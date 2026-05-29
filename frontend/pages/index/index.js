Page({
  data: {
    searchKeyword: '',
    banners: [
      { id: 1, image: '/static/banners/banner-bakery-interior.jpg' },
      { id: 2, image: '/static/banners/banner-cake-dessert.jpg' },
      { id: 3, image: '/static/banners/banner-coffee-breakfast.jpg' },
    ],
    categories: [
      { id: '1', name: '全部', icon: '🍞' },
      { id: '2', name: '面包', icon: '🥖' },
      { id: '3', name: '蛋糕', icon: '🍰' },
      { id: '4', name: '甜点', icon: '🍮' },
      { id: '5', name: '饮品', icon: '☕' },
      { id: '6', name: '礼盒', icon: '🎁' },
    ],
    recommendedProducts: [
      {
        id: '1',
        name: '奶油可颂',
        price: 18,
        originalPrice: 22,
        images: ['data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='],
      },
      {
        id: '2',
        name: '巧克力蛋糕',
        price: 68,
        originalPrice: 88,
        images: ['data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='],
      },
      {
        id: '3',
        name: '草莓慕斯',
        price: 48,
        images: ['data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='],
      },
    ],
    hotProducts: [
      {
        id: '4',
        name: '全麦面包',
        description: '健康全麦，低脂低糖',
        price: 28,
        sales: 152,
        images: ['data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='],
      },
      {
        id: '5',
        name: '芝士蛋糕',
        description: '浓郁芝士，入口即化',
        price: 58,
        sales: 98,
        images: ['data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='],
      },
      {
        id: '6',
        name: '拿铁咖啡',
        description: '现磨咖啡，香浓顺滑',
        price: 25,
        sales: 203,
        images: ['data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='],
      },
    ],
  },

  onLoad: function() {
    console.log('首页加载')
  },

  handleSearch: function(e) {
    const keyword = e.detail.value || this.data.searchKeyword
    if (keyword.trim()) {
      console.log('搜索:', keyword)
      wx.showToast({
        title: '搜索: ' + keyword,
        icon: 'none',
      })
    }
  },

  handleCategoryClick: function(e) {
    const categoryId = e.currentTarget.dataset.id
    console.log('选择分类:', categoryId)
    wx.showToast({
      title: '分类: ' + categoryId,
      icon: 'none',
    })
  },

  handleProductClick: function(e) {
    const productId = e.currentTarget.dataset.id
    console.log('查看商品:', productId)
    wx.navigateTo({
      url: '/pages/product-detail/index?id=' + productId,
    })
  },

  handleViewAll: function() {
    console.log('查看全部推荐')
    wx.showToast({
      title: '查看全部',
      icon: 'none',
    })
  },
})