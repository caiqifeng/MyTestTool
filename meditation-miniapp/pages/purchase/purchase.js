// 购买页面
var scenesData = require('../../data/scenes')
var MEDITATION_SCENES = scenesData.MEDITATION_SCENES

Page({
  data: {
    userInfo: {},
    isVip: false,
    vipExpiryText: '',
    scene: null,
    selectedPlan: 'yearly'
  },

  onLoad: function(options) {
    // 加载用户信息
    var userInfo = wx.getStorageSync('user_info') || {}
    var isVip = userInfo.isVip || false
    var vipExpiryText = ''

    if (isVip && userInfo.vipExpiry) {
      var now = new Date().getTime()
      if (now > userInfo.vipExpiry) {
        isVip = false
        userInfo.isVip = false
        wx.setStorageSync('user_info', userInfo)
      } else {
        var d = new Date(userInfo.vipExpiry)
        vipExpiryText = (d.getMonth() + 1) + '月' + d.getDate() + '日'
      }
    }

    // 加载指定场景
    var scene = null
    if (options.sceneId) {
      scene = MEDITATION_SCENES.find(function(s) { return s.id === options.sceneId })
    }

    this.setData({
      userInfo: userInfo,
      isVip: isVip,
      vipExpiryText: vipExpiryText,
      scene: scene
    })
  },

  selectPlan: function(e) {
    var plan = e.currentTarget.dataset.plan
    this.setData({ selectedPlan: plan })
  },

  // 购买单个场景
  buyScene: function() {
    var scene = this.data.scene
    if (!scene) return

    var self = this
    wx.showModal({
      title: '购买场景',
      content: '确定花费 ¥' + (scene.price / 100).toFixed(0) + ' 购买「' + scene.name + '」？',
      confirmText: '购买',
      confirmColor: '#6B9B7D',
      success: function(res) {
        if (res.confirm) {
          // TODO: 接入微信支付
          // 模拟购买成功
          var userInfo = wx.getStorageSync('user_info') || {}
          if (!userInfo.purchasedScenes) userInfo.purchasedScenes = {}
          userInfo.purchasedScenes[scene.id] = {
            price: scene.price,
            time: new Date().toISOString()
          }
          wx.setStorageSync('user_info', userInfo)
          wx.setStorageSync('purchased_scenes', userInfo.purchasedScenes)

          wx.showToast({ title: '购买成功', icon: 'success' })

          setTimeout(function() {
            // 返回首页并自动进入播放
            wx.redirectTo({
              url: '/pages/session/session?sceneId=' + scene.id + '&duration=' + (scene.defaultDuration || 10)
            })
          }, 1200)
        }
      }
    })
  },

  // 开通VIP
  buyVip: function() {
    var plan = this.data.selectedPlan
    var planName = plan === 'monthly' ? '月度会员' : '年度会员'
    var planPrice = plan === 'monthly' ? '¥18' : '¥128'

    var self = this
    wx.showModal({
      title: planName,
      content: '确定花费 ' + planPrice + ' 开通' + planName + '？',
      confirmText: '开通',
      confirmColor: '#6B9B7D',
      success: function(res) {
        if (res.confirm) {
          // TODO: 接入微信支付
          // 模拟开通成功
          var expiry = new Date().getTime()
          if (plan === 'monthly') {
            expiry += 30 * 24 * 60 * 60 * 1000
          } else {
            expiry += 365 * 24 * 60 * 60 * 1000
          }

          var userInfo = wx.getStorageSync('user_info') || {}
          userInfo.isVip = true
          userInfo.vipExpiry = expiry
          wx.setStorageSync('user_info', userInfo)
          wx.setStorageSync('vip_status', true)
          wx.setStorageSync('vip_expiry', expiry)

          wx.showToast({ title: '开通成功 🎉', icon: 'success' })

          // 刷新页面数据
          var d = new Date(expiry)
          var vipExpiryText = (d.getMonth() + 1) + '月' + d.getDate() + '日'
          self.setData({
            isVip: true,
            vipExpiryText: vipExpiryText,
            userInfo: userInfo
          })

          // 如果是从场景点击进来的，1.5秒后自动跳转播放
          if (self.data.scene) {
            setTimeout(function() {
              wx.redirectTo({
                url: '/pages/session/session?sceneId=' + self.data.scene.id + '&duration=' + (self.data.scene.defaultDuration || 10)
              })
            }, 1500)
          }
        }
      }
    })
  }
})
