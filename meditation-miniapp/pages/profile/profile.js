// 我的页面
Page({
  data: {
    stats: {},
    reminder: false,
    isLoggedIn: false,
    userInfo: {},
    isVip: false,
    vipExpiryText: ''
  },

  onShow: function() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 2 })
    }
    this.setData({
      stats: wx.getStorageSync('meditation_stats') || { totalMinutes: 0, totalSessions: 0, streak: 0 },
      reminder: wx.getStorageSync('reminder_on') || false
    })
    this.loadUserStatus()
  },

  loadUserStatus: function() {
    var userInfo = wx.getStorageSync('user_info') || {}
    var isLoggedIn = userInfo.isLoggedIn || false
    var isVip = userInfo.isVip || false
    var vipExpiryText = ''

    if (isVip && userInfo.vipExpiry) {
      var now = new Date().getTime()
      if (now > userInfo.vipExpiry) {
        isVip = false
        userInfo.isVip = false
        wx.setStorageSync('user_info', userInfo)
        wx.setStorageSync('vip_status', false)
      } else {
        var d = new Date(userInfo.vipExpiry)
        vipExpiryText = (d.getMonth() + 1) + '月' + d.getDate() + '日'
      }
    }

    this.setData({
      isLoggedIn: isLoggedIn,
      userInfo: userInfo,
      isVip: isVip,
      vipExpiryText: vipExpiryText
    })
  },

  toggleReminder: function(e) {
    var val = e.detail.value
    this.setData({ reminder: val })
    wx.setStorageSync('reminder_on', val)
    wx.showToast({ title: val ? '提醒已开启' : '提醒已关闭', icon: 'none' })
  },

  goLogin: function() {
    wx.navigateTo({ url: '/pages/login/login' })
  },

  goVip: function() {
    if (!this.data.isLoggedIn) {
      wx.navigateTo({ url: '/pages/login/login' })
      return
    }
    wx.navigateTo({ url: '/pages/purchase/purchase' })
  }
})
