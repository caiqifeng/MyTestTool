// 首页逻辑
var scenesData = require('../../data/scenes')
var MEDITATION_SCENES = scenesData.MEDITATION_SCENES

Page({
  data: {
    greeting: '',
    scenes: MEDITATION_SCENES,
    selectedScene: 'mindfulness',
    selectedDuration: 10,
    currentScene: MEDITATION_SCENES.find(function(s) { return s.id === 'mindfulness' }) || MEDITATION_SCENES[0],
    featured: MEDITATION_SCENES[0],
    showDurationSheet: false,
    stats: { totalMinutes: 0, totalSessions: 0, streak: 0 },
    isVip: false,
    isLoggedIn: false,
    purchasedScenes: {}
  },

  onLoad: function() {
    this.setGreeting()
    this.loadStats()
    this.loadUserStatus()
    this.setFeatured()
  },

  onShow: function() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 })
    }
    this.loadStats()
    this.loadUserStatus()
  },

  // 加载用户状态（登录/VIP/已购买）
  loadUserStatus: function() {
    var userInfo = wx.getStorageSync('user_info') || {}
    var isLoggedIn = userInfo.isLoggedIn || false
    var isVip = userInfo.isVip || false
    var purchasedScenes = userInfo.purchasedScenes || {}

    // 检查VIP是否过期
    if (isVip && userInfo.vipExpiry) {
      var now = new Date().getTime()
      if (now > userInfo.vipExpiry) {
        isVip = false
        userInfo.isVip = false
        wx.setStorageSync('user_info', userInfo)
        wx.setStorageSync('vip_status', false)
        wx.setStorageSync('vip_expiry', '')
      }
    }

    this.setData({
      isLoggedIn: isLoggedIn,
      isVip: isVip,
      purchasedScenes: purchasedScenes
    })
  },

  // 判断场景是否可用（免费/VIP/已购买）
  isSceneAvailable: function(scene) {
    if (!scene.isVip) return true
    if (this.data.isVip) return true
    if (this.data.purchasedScenes[scene.id]) return true
    return false
  },

  // 处理场景点击：登录判断 → 购买判断 → 播放
  handleSceneTap: function(scene) {
    if (!scene) return

    // 免费场景或已拥有：直接进入播放
    if (this.isSceneAvailable(scene)) {
      wx.navigateTo({
        url: '/pages/session/session?sceneId=' + scene.id + '&duration=' + (scene.defaultDuration || 10)
      })
      return
    }

    // 收费场景：检查登录状态
    if (!this.data.isLoggedIn) {
      wx.navigateTo({ url: '/pages/login/login' })
      return
    }

    // 已登录但未购买/VIP：跳转购买页
    wx.navigateTo({
      url: '/pages/purchase/purchase?sceneId=' + scene.id
    })
  },

  setGreeting: function() {
    var h = new Date().getHours()
    var greeting = '晚上好'
    if (h >= 5 && h < 12) greeting = '早上好'
    else if (h >= 12 && h < 18) greeting = '下午好'
    this.setData({ greeting: greeting })
  },

  loadStats: function() {
    var stats = wx.getStorageSync('meditation_stats') || {
      totalMinutes: 0, totalSessions: 0, streak: 0
    }
    this.setData({ stats: stats })
  },

  setFeatured: function() {
    var h = new Date().getHours()
    var featuredId = 'mindfulness'
    if (h >= 5 && h < 10) featuredId = 'dawn_light'
    else if (h >= 10 && h < 18) featuredId = 'forest_rain'
    else if (h >= 18 && h < 22) featuredId = 'ocean_wave'
    else featuredId = 'starry_sky'

    var featured = MEDITATION_SCENES.find(function(s) { return s.id === featuredId }) || MEDITATION_SCENES[0]
    this.setData({ featured: featured })
  },

  // 选择场景
  selectScene: function(e) {
    var id = e.currentTarget.dataset.id
    var scene = MEDITATION_SCENES.find(function(s) { return s.id === id })
    if (!scene) return

    this.handleSceneTap(scene)
  },

  selectDuration: function(e) {
    var val = parseInt(e.currentTarget.dataset.val) || 10
    this.setData({ selectedDuration: val })
  },

  // 开始冥想按钮
  openDurationSheet: function() {
    var scene = this.data.currentScene
    if (!scene) return

    this.handleSceneTap(scene)
  },

  // 时长面板操作（免费场景选中后才到这里）
  showDurationSheetForScene: function() {
    this.setData({ showDurationSheet: true })
  },

  closeDurationSheet: function() {
    this.setData({ showDurationSheet: false })
  },

  startFeatured: function() {
    var featured = this.data.featured
    if (!featured) return
    this.handleSceneTap(featured)
  },

  startMeditation: function() {
    var selectedScene = this.data.selectedScene
    var selectedDuration = this.data.selectedDuration
    if (!selectedScene) return
    this.setData({ showDurationSheet: false })
    wx.navigateTo({
      url: '/pages/session/session?sceneId=' + selectedScene + '&duration=' + selectedDuration
    })
  },

  // 跳转VIP购买页
  goVip: function() {
    if (!this.data.isLoggedIn) {
      wx.navigateTo({ url: '/pages/login/login' })
      return
    }
    wx.navigateTo({ url: '/pages/purchase/purchase' })
  },

  goHistory: function() {
    wx.switchTab({ url: '/pages/history/history' })
  }
})
