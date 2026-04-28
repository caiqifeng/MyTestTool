// 冥想播放页逻辑
var scenesData = require('../../data/scenes')
var MEDITATION_SCENES = scenesData.MEDITATION_SCENES
var timerData = require('../../utils/timer')
var MeditationTimer = timerData.MeditationTimer

// ============================================================
// 音频资源配置
// 优先使用在线 URL（CDN），填写后自动走在线模式，不需要分包加载
// 如果在线 URL 留空('')，自动降级到本地分包路径
//
// 推荐 CDN 方案：腾讯云 COS / 阿里云 OSS / GitHub + jsDelivr
// 上传音频到 COS Bucket 后，将对应的 https:// 链接填入 AUDIO_CDN
// ============================================================

// 在线 CDN 地址（填写后自动生效，留空则用本地分包）
var AUDIO_CDN = {
  rain_forest:   '',   // 例: 'https://your-bucket.cos.ap-guangzhou.myqcloud.com/audio/rain_forest.mp3'
  ocean_waves:   '',
  morning_birds: '',
  deep_rumble:   '',
  night_ambient: '',
  singing_bowl:  ''
}

// 本地分包路径（CDN 不可用时的降级方案）
var AUDIO_LOCAL = {
  rain_forest:   'audioPackage/audio/rain_forest.mp3',
  ocean_waves:   'audioPackage/audio/ocean_waves.mp3',
  morning_birds: 'audioPackage/audio/morning_birds.mp3',
  deep_rumble:   'audioPackage/audio/deep_rumble.mp3',
  night_ambient: 'audioPackage2/audio/night_ambient.mp3',
  singing_bowl:  'audioPackage2/audio/singing_bowl.mp3'
}

// 获取音频路径（优先 CDN）
function getAudioSrc(audioType) {
  var cdn = AUDIO_CDN[audioType]
  if (cdn && cdn.length > 0) return cdn
  return AUDIO_LOCAL[audioType] || ''
}

Page({
  data: {
    scene: null,
    duration: 10,
    isPlaying: false,
    timerMinutes: 10,
    timerSeconds: 0,
    progress: 0,
    breathPhase: 'inhale',
    breathLabel: '吸气',
    breathHint: '4 秒',
    currentGuide: '',
    showGuide: true,
    soundOn: true,
    showComplete: false,
    longPressing: false,
    longPressSec: 0,
    actualMeditated: 0,
    showEndToast: false,
    totalToday: 0,
    newStreak: 0
  },

  timer: null,
  guideIndex: 0,
  guideTimer: null,
  bgAudio: null,
  longPressTimer: null,
  longPressCount: 0,
  touchStartTime: 0,

  onLoad: function(options) {
    var sceneId = options.sceneId || ''
    var duration = parseInt(options.duration) || 10
    var scene = MEDITATION_SCENES.find(function(s) { return s.id === sceneId }) || MEDITATION_SCENES[0]

    this.setData({
      scene: scene,
      duration: duration,
      timerMinutes: duration,
      timerSeconds: 0,
      currentGuide: (scene && scene.guideScript) ? scene.guideScript[0] : ''
    })

    wx.setNavigationBarTitle({ title: scene.name || '冥想' })
  },

  onReady: function() {
    // 延迟1秒自动开始冥想（给页面渲染时间）
    var self = this
    var scene = this.data.scene
    var audioType = scene ? scene.audioType : ''
    var isCDN = !!(AUDIO_CDN[audioType] && AUDIO_CDN[audioType].length > 0)

    var doStart = function() {
      wx.setKeepScreenOn({ keepScreenOn: true })
      setTimeout(function() { self.startTimer() }, 200)
    }

    if (isCDN) {
      // CDN 模式：延迟1秒直接开始
      console.log('CDN 音频模式，1秒后自动开始')
      setTimeout(doStart, 1000)
    } else {
      // 本地分包模式：先 loadSubpackage，成功后再开始
      var pack2Types = { night_ambient: true, singing_bowl: true }
      var packName = pack2Types[audioType] ? 'audio2' : 'audio1'

      if (wx.loadSubpackage) {
        var task = wx.loadSubpackage({
          name: packName,
          success: function() {
            console.log('分包加载成功: ' + packName)
            doStart()
          },
          fail: function(err) {
            console.error('分包加载失败:', JSON.stringify(err))
            doStart()
          }
        })
        if (task && task.onProgressUpdate) {
          task.onProgressUpdate(function(info) {
            console.log('分包下载进度:', info.progress + '%')
          })
        }
      } else {
        setTimeout(doStart, 1000)
      }
    }
  },

  onUnload: function() {
    this.onPlayBtnTouchCancel()
    this.stopAll()
    wx.setKeepScreenOn({ keepScreenOn: false })
  },

  // 播放背景音频（支持 CDN / 本地分包双模式）
  startBgAudio: function() {
    if (!this.data.soundOn) return

    var scene = this.data.scene
    if (!scene || !scene.audioType) return

    var audioSrc = getAudioSrc(scene.audioType)
    if (!audioSrc) return

    console.log('音频来源:', audioSrc.startsWith('http') ? 'CDN' : '本地分包', audioSrc)

    // 销毁旧实例
    if (this.bgAudio) {
      try { this.bgAudio.destroy() } catch(e) {}
      this.bgAudio = null
    }

    var audio = wx.createInnerAudioContext()
    audio.loop = true
    audio.volume = 0.7
    audio.obeyMuteSwitch = false

    var played = false
    audio.onCanplay(function() {
      if (!played) {
        played = true
        console.log('音频就绪，play()')
        audio.play()
      }
    })
    audio.onPlay(function() {
      console.log('音频播放中 ✓')
    })
    audio.onError(function(err) {
      console.error('音频错误 code:', err.errCode, 'msg:', err.errMsg)
    })

    // 设置 src 触发加载（不主动调 play，等 onCanplay）
    audio.src = audioSrc

    this.bgAudio = audio
  },

  // 停止背景音频
  stopBgAudio: function() {
    if (this.bgAudio) {
      try {
        this.bgAudio.stop()
        this.bgAudio.destroy()
      } catch (e) {}
      this.bgAudio = null
    }
  },

  startTimer: function() {
    var self = this
    var duration = this.data.duration

    this.setData({ isPlaying: true })

    // 播放背景音频
    this.startBgAudio()

    this.timer = new MeditationTimer({
      duration: duration,
      onTick: function(info) {
        self.setData({
          timerMinutes: info.minutes,
          timerSeconds: info.seconds,
          progress: info.progress
        })
      },
      onPhaseChange: function(phase) {
        var hints = { inhale: '4 秒', hold: '7 秒', exhale: '8 秒' }
        var labels = { inhale: '吸气', hold: '屏息', exhale: '呼气' }
        self.setData({
          breathPhase: phase.name,
          breathLabel: labels[phase.name] || '',
          breathHint: hints[phase.name] || ''
        })
      },
      onComplete: function() {
        self.onMeditationComplete()
      }
    })

    this.timer.start()
    this.startGuideRotation()
  },

  startGuideRotation: function() {
    var self = this
    var scene = this.data.scene
    if (!scene || !scene.guideScript) return

    var scripts = scene.guideScript
    this.guideIndex = 0

    var rotate = function() {
      self.guideIndex = (self.guideIndex + 1) % scripts.length
      self.setData({ currentGuide: scripts[self.guideIndex] })
      self.guideTimer = setTimeout(rotate, 18000)
    }
    this.guideTimer = setTimeout(rotate, 18000)
  },

  togglePlay: function() {
    if (this.data.isPlaying) {
      // 播放中 → 暂停
      if (this.timer) this.timer.pause()
      this.setData({ isPlaying: false })
      if (this.guideTimer) clearTimeout(this.guideTimer)
      if (this.bgAudio) {
        try { this.bgAudio.pause() } catch (e) {}
      }
    }
  },

  // 中间按钮 touchstart：记录时间 + 启动长按检测
  onPlayBtnTouchStart: function(e) {
    if (e.touches.length > 1) return // 忽略多点触控
    if (this._playBtnTouchActive) return // 防重复
    this._playBtnTouchActive = true
    this._playBtnMoved = false

    if (this.data.isPlaying) return // 播放中不处理长按，等 tap → togglePlay

    var self = this
    this.touchStartTime = Date.now()
    this.longPressCount = 0
    this.setData({ longPressing: true, longPressSec: 0 })

    this.longPressTimer = setInterval(function() {
      self.longPressCount++
      var sec = Math.floor(self.longPressCount / 10)
      self.setData({ longPressSec: sec })
      if (self.longPressCount >= 30) {
        clearInterval(self.longPressTimer)
        self.longPressTimer = null
        self.doEarlyExit()
      }
    }, 100)
  },

  // 中间按钮 touchmove：如果手指移动太远，取消长按
  onPlayBtnTouchMove: function(e) {
    if (!this.data.longPressing) return
    if (e.touches.length < 1) return
    // 获取 touch 相对于元素中心的偏移（简易判断）
    // 微信中 touches[0] 是页面坐标，没有直接的 offsetX
    // 标记为已移动，touchend 时不恢复播放
    this._playBtnMoved = true
  },

  // 中间按钮 touchend：区分 tap（暂停/恢复播放）和长按
  onPlayBtnTouchEnd: function() {
    this._playBtnTouchActive = false
    var wasLongPressing = false
    var elapsed = Date.now() - this.touchStartTime

    if (this.longPressTimer) {
      clearInterval(this.longPressTimer)
      this.longPressTimer = null
    }
    wasLongPressing = this.data.longPressing
    this.setData({ longPressing: false, longPressSec: 0 })

    if (this.data.isPlaying) {
      // 播放中松手 → 暂停
      if (this.timer) this.timer.pause()
      this.setData({ isPlaying: false })
      if (this.guideTimer) clearTimeout(this.guideTimer)
      if (this.bgAudio) {
        try { this.bgAudio.pause() } catch (e) {}
      }
    } else if (wasLongPressing && elapsed < 3000 && !this._playBtnMoved) {
      // 暂停状态下短按（<3秒，未移动）→ 恢复播放
      this.resumePlay()
    }
  },

  // 恢复播放
  resumePlay: function() {
    if (this.timer) this.timer.resume()
    this.setData({ isPlaying: true })
    this.startGuideRotation()
    if (this.bgAudio) {
      try { this.bgAudio.play() } catch (e) {
        this.bgAudio = null
        this.startBgAudio()
      }
    } else {
      this.startBgAudio()
    }
  },

  onPlayBtnTouchCancel: function() {
    if (this.longPressTimer) {
      clearInterval(this.longPressTimer)
      this.longPressTimer = null
    }
    this.setData({ longPressing: false, longPressSec: 0 })
  },

  // 提前结束冥想（长按3秒触发）
  doEarlyExit: function() {
    var duration = this.data.duration
    var progress = this.data.progress
    // 实际冥想时长 = 总时长 × 已完成进度
    var actualMin = Math.max(Math.round(duration * progress), 0)
    if (actualMin < 1 && progress > 0) actualMin = 1

    this.stopAll()

    // 保存记录
    var scene = this.data.scene
    var history = wx.getStorageSync('meditation_history') || []
    var now = new Date()
    var dateStr = now.getFullYear() + '/' + (now.getMonth()+1) + '/' + now.getDate()
    var hour = now.getHours()
    var minute = now.getMinutes()
    var timeStr = (hour < 10 ? '0' : '') + hour + ':' + (minute < 10 ? '0' : '') + minute

    var record = {
      id: Date.now(),
      sceneId: scene.id,
      sceneName: scene.name,
      sceneIcon: scene.icon,
      duration: actualMin,
      date: dateStr,
      time: timeStr,
      timestamp: Date.now()
    }
    history.unshift(record)
    wx.setStorageSync('meditation_history', history)

    var stats = wx.getStorageSync('meditation_stats') || {}
    stats.totalMinutes = (stats.totalMinutes || 0) + actualMin
    stats.totalSessions = (stats.totalSessions || 0) + 1
    if (stats.lastDate !== dateStr) {
      stats.streak = (stats.streak || 0) + 1
    }
    stats.lastDate = dateStr
    wx.setStorageSync('meditation_stats', stats)

    var todayRecords = history.filter(function(r) { return r.date === dateStr })
    var totalToday = todayRecords.reduce(function(sum, r) { return sum + r.duration }, 0)

    this.setData({
      longPressing: false,
      longPressSec: 0,
      showEndToast: true,
      actualMeditated: actualMin,
      totalToday: totalToday,
      newStreak: stats.streak
    })

    wx.vibrateShort({ type: 'medium' })

    // 2秒后自动回到首页
    var self = this
    setTimeout(function() {
      self.setData({ showEndToast: false })
      wx.switchTab({ url: '/pages/home/home' })
    }, 2500)
  },

  toggleGuide: function() {
    this.setData({ showGuide: !this.data.showGuide })
  },

  toggleSound: function() {
    var newSoundOn = !this.data.soundOn
    this.setData({ soundOn: newSoundOn })

    // 实时控制音频开关
    if (newSoundOn) {
      // 开启声音
      if (this.bgAudio) {
        try { this.bgAudio.play() } catch (e) {}
      } else if (this.data.isPlaying) {
        this.startBgAudio()
      }
    } else {
      // 静音
      if (this.bgAudio) {
        try { this.bgAudio.pause() } catch (e) {}
      }
    }
  },

  onMeditationComplete: function() {
    this.stopAll()

    var duration = this.data.duration
    var scene = this.data.scene
    var history = wx.getStorageSync('meditation_history') || []

    var now = new Date()
    var dateStr = now.getFullYear() + '/' + (now.getMonth()+1) + '/' + now.getDate()
    var hour = now.getHours()
    var minute = now.getMinutes()
    var timeStr = (hour < 10 ? '0' : '') + hour + ':' + (minute < 10 ? '0' : '') + minute

    var record = {
      id: Date.now(),
      sceneId: scene.id,
      sceneName: scene.name,
      sceneIcon: scene.icon,
      duration: duration,
      date: dateStr,
      time: timeStr,
      timestamp: Date.now()
    }
    history.unshift(record)
    wx.setStorageSync('meditation_history', history)

    var stats = wx.getStorageSync('meditation_stats') || {}
    stats.totalMinutes = (stats.totalMinutes || 0) + duration
    stats.totalSessions = (stats.totalSessions || 0) + 1

    if (stats.lastDate === dateStr) {
      // 今天已冥想过
    } else {
      stats.streak = (stats.streak || 0) + 1
    }
    stats.lastDate = dateStr
    wx.setStorageSync('meditation_stats', stats)

    var todayRecords = history.filter(function(r) { return r.date === dateStr })
    var totalToday = todayRecords.reduce(function(sum, r) { return sum + r.duration }, 0)

    this.setData({
      showComplete: true,
      totalToday: totalToday,
      newStreak: stats.streak
    })

    wx.vibrateShort({ type: 'medium' })
  },

  finish: function() {
    wx.switchTab({ url: '/pages/home/home' })
  },

  doAgain: function() {
    var self = this
    var scene = this.data.scene
    var duration = this.data.duration
    this.stopBgAudio()
    this.setData({
      showComplete: false,
      progress: 0,
      timerMinutes: duration,
      timerSeconds: 0
    })
    setTimeout(function() { self.startTimer() }, 500)
  },

  confirmExit: function() {
    if (!this.data.isPlaying && this.data.progress === 0) {
      this.stopBgAudio()
      wx.navigateBack()
      return
    }
    var self = this
    wx.showModal({
      title: '退出冥想',
      content: '确定要离开吗？本次记录不会保存。',
      confirmText: '离开',
      cancelText: '继续',
      success: function(res) {
        if (res.confirm) {
          self.stopAll()
          self.stopBgAudio()
          wx.navigateBack()
        }
      }
    })
  },

  stopAll: function() {
    if (this.timer) this.timer.stop()
    if (this.guideTimer) clearTimeout(this.guideTimer)
    this.stopBgAudio()
    this.setData({ isPlaying: false })
  }
})
