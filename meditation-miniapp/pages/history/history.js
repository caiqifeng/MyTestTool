// 历史记录页
Page({
  data: { history: [], stats: {} },
  onShow: function() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 })
    }
    this.setData({
      history: wx.getStorageSync('meditation_history') || [],
      stats: wx.getStorageSync('meditation_stats') || { totalMinutes: 0, totalSessions: 0, streak: 0 }
    })
  },
  goHome: function() { wx.switchTab({ url: '/pages/home/home' }) }
})
