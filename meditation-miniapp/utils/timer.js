// 计时器工具类（ES5 兼容写法）
function MeditationTimer(options) {
  this.totalSeconds = (options.duration || 10) * 60
  this.remaining = this.totalSeconds
  this.onTick = options.onTick || null
  this.onComplete = options.onComplete || null
  this.onPhaseChange = options.onPhaseChange || null
  this.timer = null
  this.isRunning = false
  this.isPaused = false

  // 呼吸节奏：4秒吸气 / 7秒屏息 / 8秒呼气
  this.breathPhases = [
    { name: 'inhale', label: '吸气', duration: 4 },
    { name: 'hold', label: '屏息', duration: 7 },
    { name: 'exhale', label: '呼气', duration: 8 }
  ]
  this.breathCycleTotal = 19
  this.breathElapsed = 0
  this.currentBreathPhase = 0
}

MeditationTimer.prototype.start = function() {
  if (this.isRunning) return
  this.isRunning = true
  this.isPaused = false
  this._tick()
}

MeditationTimer.prototype.pause = function() {
  this.isPaused = true
  this.isRunning = false
  if (this.timer) clearTimeout(this.timer)
}

MeditationTimer.prototype.resume = function() {
  if (!this.isPaused) return
  this.isRunning = true
  this.isPaused = false
  this._tick()
}

MeditationTimer.prototype.stop = function() {
  this.isRunning = false
  this.isPaused = false
  if (this.timer) clearTimeout(this.timer)
}

MeditationTimer.prototype._tick = function() {
  var self = this
  if (!this.isRunning) return
  this.timer = setTimeout(function() {
    self.remaining--
    self.breathElapsed = (self.breathElapsed + 1) % self.breathCycleTotal

    // 计算呼吸阶段
    var i, acc = 0
    for (i = 0; i < self.breathPhases.length; i++) {
      acc += self.breathPhases[i].duration
      if (self.breathElapsed < acc) {
        if (self.currentBreathPhase !== i) {
          self.currentBreathPhase = i
          if (self.onPhaseChange) self.onPhaseChange(self.breathPhases[i])
        }
        break
      }
    }

    // 当前阶段进度 (0~1)
    var phaseStart = 0
    for (i = 0; i < self.currentBreathPhase; i++) {
      phaseStart += self.breathPhases[i].duration
    }
    var phaseProgress = (self.breathElapsed - phaseStart) / self.breathPhases[self.currentBreathPhase].duration

    if (self.onTick) {
      self.onTick({
        remaining: self.remaining,
        total: self.totalSeconds,
        progress: 1 - self.remaining / self.totalSeconds,
        breathPhase: self.breathPhases[self.currentBreathPhase],
        breathProgress: phaseProgress,
        minutes: Math.floor(self.remaining / 60),
        seconds: self.remaining % 60
      })
    }

    if (self.remaining <= 0) {
      self.isRunning = false
      if (self.onComplete) self.onComplete()
      return
    }

    self._tick()
  }, 1000)
}

module.exports = { MeditationTimer: MeditationTimer }
