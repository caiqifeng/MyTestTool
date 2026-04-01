import Order from '../../src/models/Order';
import { OrderStatus, DeliveryType, PaymentMethod, PaymentStatus } from '@shared/types';

describe('Order Model', () => {
  test('should be importable', () => {
    expect(Order).toBeDefined();
    expect(typeof Order).toBe('function');
  });

  test('should have static methods', () => {
    expect(Order.getStatusStats).toBeDefined();
    expect(Order.getUserOrders).toBeDefined();
    expect(typeof Order.getStatusStats).toBe('function');
    expect(typeof Order.getUserOrders).toBe('function');
  });

  test('should create order instance', () => {
    const order = new Order({
      userId: 'test_user_id',
      items: [
        {
          productId: 'test_product_id',
          name: 'Test Product',
          price: 10.99,
          quantity: 2,
          image: 'product.jpg'
        }
      ],
      totalAmount: 21.98,
      deliveryFee: 5,
      discountAmount: 0,
      finalAmount: 26.98,
      deliveryType: DeliveryType.DELIVERY,
      deliveryAddress: {
        contactName: 'Test User',
        contactPhone: '13800138000',
        province: 'Test Province',
        city: 'Test City',
        district: 'Test District',
        detail: 'Test Address Detail'
      },
      paymentMethod: PaymentMethod.WECHAT_PAY,
      paymentStatus: PaymentStatus.PENDING,
      orderStatus: OrderStatus.PENDING,
      remark: 'Test remark'
    });

    expect(order).toBeDefined();
    expect(order.userId).toBe('test_user_id');
    expect(order.items.length).toBe(1);
    expect(order.totalAmount).toBe(21.98);
    expect(order.deliveryType).toBe(DeliveryType.DELIVERY);
    expect(order.paymentMethod).toBe(PaymentMethod.WECHAT_PAY);
    expect(order.orderStatus).toBe(OrderStatus.PENDING);
  });
});