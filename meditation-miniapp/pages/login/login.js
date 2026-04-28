// 登录页面
Page({
  data: {},

  onLoad: function() {
    // 如果已登录，直接返回
    var userInfo = wx.getStorageSync('user_info')
    if (userInfo && userInfo.isLoggedIn) {
      wx.navigateBack()
    }
  },

  // 微信登录
  onWechatLogin: function(e) {
    var self = this
    if (e.detail.userInfo) {
      self.doLogin({
        nickName: e.detail.userInfo.nickName,
        avatarUrl: e.detail.userInfo.avatarUrl,
        loginType: 'wechat'
      })
    } else {
      wx.showToast({ title: '需要授权才能登录', icon: 'none' })
    }
  },

  // 执行登录
  doLogin: function(info) {
    // TODO: 后端登录，获取用户数据（VIP状态、已购买场景等）
    // 模拟登录成功
    var userInfo = {
      isLoggedIn: true,
      nickName: info.nickName || '冥想者',
      avatarUrl: info.avatarUrl || '',
      loginType: info.loginType || 'guest',
      phone: info.phone || '',
      loginTime: new Date().toISOString(),
      isVip: false,
      vipExpiry: '',
      purchasedScenes: {}
    }

    wx.setStorageSync('user_info', userInfo)
    wx.showToast({ title: '登录成功', icon: 'success' })

    // 延迟返回，让用户看到提示
    setTimeout(function() {
      var pages = getCurrentPages()
      if (pages.length > 1) {
        wx.navigateBack()
      } else {
        wx.switchTab({ url: '/pages/home/home' })
      }
    }, 1000)
  },

  // 游客体验
  guestLogin: function() {
    var userInfo = {
      isLoggedIn: false,
      nickName: '游客',
      avatarUrl: '',
      loginType: 'guest',
      loginTime: new Date().toISOString(),
      isVip: false,
      vipExpiry: '',
      purchasedScenes: {}
    }
    wx.setStorageSync('user_info', userInfo)

    var pages = getCurrentPages()
    if (pages.length > 1) {
      wx.navigateBack()
    } else {
      wx.switchTab({ url: '/pages/home/home' })
    }
  }
})
