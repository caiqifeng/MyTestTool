// app.js
App({
  onLaunch: function() {
    var history = wx.getStorageSync('meditation_history')
    if (!history) {
      wx.setStorageSync('meditation_history', [])
    }
    var stats = wx.getStorageSync('meditation_stats')
    if (!stats) {
      wx.setStorageSync('meditation_stats', {
        totalMinutes: 0,
        totalSessions: 0,
        streak: 0,
        lastDate: ''
      })
    }
    this.updateStreak()
  },

  updateStreak: function() {
    var stats = wx.getStorageSync('meditation_stats') || {}
    var now = new Date()
    var today = now.getFullYear() + '/' + (now.getMonth() + 1) + '/' + now.getDate()
    var yesterday = new Date(Date.now() - 86400000)
    var yesterdayStr = yesterday.getFullYear() + '/' + (yesterday.getMonth() + 1) + '/' + yesterday.getDate()

    if (stats.lastDate === yesterdayStr) {
      // 昨天有记录，连续天数保持（今天完成后再更新）
    } else if (stats.lastDate !== today) {
      // 超过一天没冥想，重置连续天数
      stats.streak = 0
      wx.setStorageSync('meditation_stats', stats)
    }
  },

  globalData: {
    userInfo: null
  }
})
