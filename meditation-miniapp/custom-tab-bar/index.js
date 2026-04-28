Component({
  data: {
    selected: 0,
    list: [
      {
        id: 'home',
        pagePath: '/pages/home/home',
        text: '冥想'
      },
      {
        id: 'history',
        pagePath: '/pages/history/history',
        text: '记录'
      },
      {
        id: 'profile',
        pagePath: '/pages/profile/profile',
        text: '我的'
      }
    ]
  },
  methods: {
    switchTab: function(e) {
      var path = e.currentTarget.dataset.path
      var index = e.currentTarget.dataset.index
      wx.switchTab({ url: path })
    }
  }
})
