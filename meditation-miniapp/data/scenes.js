// 冥想场景数据 + 引导脚本
// isVip: 是否需要VIP才能使用
// price: 单独购买价格（分），0表示免费，null表示仅VIP
// purchased: 运行时从本地存储读取
var MEDITATION_SCENES = [
  {
    id: 'forest_rain',
    name: '林间细雨',
    icon: '🌧',
    color: '#5A9E6F',
    bgGradient: ['#E8F0EB', '#D1E4D9'],
    bgImage: '/assets/bg/forest_rain.jpg',
    effect: 'rain',
    description: '让雨声洗去一天的疲惫',
    duration: [5, 10, 15, 20],
    defaultDuration: 10,
    audioType: 'rain_forest',
    isVip: false,
    price: 0,
    guideScript: [
      '轻轻闭上眼睛，感受呼吸随着雨声起伏……',
      '每一滴雨水，都在带走你心中的负担……',
      '吸气，感受清新的雨后空气进入肺腑……',
      '呼气，释放所有紧张与焦虑……',
      '你只是此刻这片林间细雨中的一个观察者，安静，平和……'
    ]
  },
  {
    id: 'ocean_wave',
    name: '深洋海浪',
    icon: '🌊',
    color: '#4A90B8',
    bgGradient: ['#E6EFF5', '#CDDFEC'],
    bgImage: '/assets/bg/ocean_wave.jpg',
    effect: 'wave',
    description: '随浪潮找回内心的宁静',
    duration: [5, 10, 15, 20],
    defaultDuration: 10,
    audioType: 'ocean_waves',
    isVip: false,
    price: 0,
    guideScript: [
      '想象自己站在辽阔的海边，脚踩细沙……',
      '海浪一次次涌来，又一次次退去……',
      '就像你的思绪，来了，再让它走……',
      '吸气时，感受海浪的力量托起你……',
      '呼气时，随着退潮，一切烦恼远离……'
    ]
  },
  {
    id: 'dawn_light',
    name: '晨曦初露',
    icon: '☀️',
    color: '#D4943A',
    bgGradient: ['#FDF3E4', '#F8E4C4'],
    bgImage: '/assets/bg/dawn_light.jpg',
    effect: 'sunbeam',
    description: '用清晨的光开启崭新一天',
    duration: [5, 10, 15],
    defaultDuration: 5,
    audioType: 'morning_birds',
    isVip: false,
    price: 0,
    guideScript: [
      '想象一束温暖的晨光，轻轻照在你的脸上……',
      '新的一天开始了，带着无限的可能……',
      '深深吸一口气，吸入这清新的晨光……',
      '感受身体从头到脚被温暖充满……',
      '今天，你有能力面对一切，你已准备好……'
    ]
  },
  {
    id: 'starry_sky',
    name: '星空静夜',
    icon: '🌙',
    color: '#6B6BA8',
    bgGradient: ['#EDE8F4', '#D9D0E8'],
    bgImage: '/assets/bg/starry_sky.jpg',
    effect: 'star',
    description: '在繁星下放空，与宇宙同频',
    duration: [10, 15, 20, 30],
    defaultDuration: 15,
    audioType: 'night_ambient',
    isVip: true,
    price: 600, // ¥6
    guideScript: [
      '抬起头，想象自己凝望着无边的星空……',
      '每一颗星，都是一个安静的存在……',
      '就像此刻的你，渺小却完整……',
      '将思绪交给星空，不必执着于任何事……',
      '在宇宙的尺度里，一切都会过去，一切都会好的……'
    ]
  },
  {
    id: 'volcano_breath',
    name: '火山呼吸',
    icon: '🫧',
    color: '#C76B5A',
    bgGradient: ['#F7ECE8', '#F0DAD3'],
    bgImage: '/assets/bg/volcano_breath.jpg',
    effect: 'bubble',
    description: '释放压力，激活内在能量',
    duration: [5, 10],
    defaultDuration: 5,
    audioType: 'deep_rumble',
    isVip: true,
    price: 300, // ¥3
    guideScript: [
      '感受内心深处积聚的能量，如同火山的岩浆……',
      '这份能量是你的力量，不是负担……',
      '用力吸气，让能量在胸腔汇聚……',
      '大力呼气，将所有压抑一并释放……',
      '你是有力量的，你可以驾驭一切……'
    ]
  },
  {
    id: 'mindfulness',
    name: '正念冥想',
    icon: '🧘',
    color: '#8B7B5E',
    bgGradient: ['#F0EDE5', '#E4DED2'],
    bgImage: '/assets/bg/mindfulness.jpg',
    effect: 'lotus',
    description: '专注当下，回归自我',
    duration: [5, 10, 15, 20, 30],
    defaultDuration: 10,
    audioType: 'singing_bowl',
    isVip: false,
    price: 0,
    guideScript: [
      '将注意力带回此刻，就是这里，就是现在……',
      '不评判，不分析，只是观察……',
      '感受呼吸，这是你与当下最直接的连接……',
      '思绪飘走了？轻轻将它带回来，一次次……',
      '你不是你的思绪，你是那个观察思绪的人……'
    ]
  }
]

// VIP 会员方案（单位：分）
var VIP_PLANS = [
  { id: 'monthly', name: '月度会员', price: 1800, label: '¥18/月', desc: '解锁全部场景' },
  { id: 'yearly', name: '年度会员', price: 12800, label: '¥128/年', desc: '解锁全部场景，省 ¥88' }
]

module.exports = {
  MEDITATION_SCENES: MEDITATION_SCENES,
  VIP_PLANS: VIP_PLANS
}
