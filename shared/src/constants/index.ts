export const DEFAULT_PAGE_SIZE = 10;
export const MAX_PAGE_SIZE = 100;

export const PRODUCT_CATEGORIES = [
  { id: 'bread', name: '面包', icon: '🍞' },
  { id: 'cake', name: '蛋糕', icon: '🎂' },
  { id: 'pastry', name: '糕点', icon: '🥐' },
  { id: 'dessert', name: '甜品', icon: '🍰' },
  { id: 'beverage', name: '饮品', icon: '🥤' }
];

export const DELIVERY_FEE = 5;
export const FREE_DELIVERY_THRESHOLD = 50;

export const ORDER_STATUS_MAP = {
  pending: '待确认',
  confirmed: '已确认',
  processing: '制作中',
  ready_for_pickup: '待取货',
  out_for_delivery: '配送中',
  completed: '已完成',
  cancelled: '已取消',
  refunded: '已退款'
};

export const PAYMENT_METHODS = [
  { value: 'wechat_pay', label: '微信支付', icon: '💳' },
  { value: 'alipay', label: '支付宝', icon: '💳' },
  { value: 'cash', label: '现金支付', icon: '💵' },
  { value: 'card', label: '银行卡', icon: '💳' }
];