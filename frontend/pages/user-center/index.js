Page({
  data: {
    isLoggedIn: false,
    nickname: '',
    avatar: '/static/avatars/default-avatar.png',
  },

  onLoad: function() {
    console.log('用户中心页面加载')
    // 检查本地存储的登录状态
    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      this.setData({
        isLoggedIn: true,
        nickname: userInfo.nickname || '用户',
        avatar: userInfo.avatar || 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
      })
    }
  },

  handleLogin: function() {
    if (!this.data.isLoggedIn) {
      console.log('跳转到登录页')
      // 模拟登录
      const mockUserInfo = {
        id: '123',
        username: 'testuser',
        nickname: '测试用户',
        avatar: '/static/avatars/default-avatar.png',
        createdAt: '2023-01-01',
      }

      this.setData({
        isLoggedIn: true,
        nickname: mockUserInfo.nickname,
        avatar: mockUserInfo.avatar,
      })

      // 保存到本地存储
      wx.setStorageSync('userInfo', mockUserInfo)

      wx.showToast({
        title: '登录成功',
        icon: 'success',
      })
    }
  },

  handleLogout: function() {
    const that = this
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: function(res) {
        if (res.confirm) {
          // 清除本地存储
          wx.removeStorageSync('userInfo')

          that.setData({
            isLoggedIn: false,
            nickname: '',
            avatar: '/static/avatars/default-avatar.png',
          })

          wx.showToast({
            title: '已退出登录',
            icon: 'success',
          })
        }
      }
    })
  },

  handleNavigate: function(e) {
    const type = e.currentTarget.dataset.type
    const subtype = e.currentTarget.dataset.subtype

    if (!this.data.isLoggedIn) {
      wx.showToast({
        title: '请先登录',
        icon: 'none',
      })
      return
    }

    console.log('跳转到:', type, subtype)

    switch (type) {
      case 'order':
        console.log('跳转到订单页面，子类型:', subtype)
        break
      case 'address':
        console.log('跳转到地址页面')
        break
      case 'coupon':
        console.log('跳转到优惠券页面')
        break
      default:
        console.log('跳转到:', type)
    }
  },
})