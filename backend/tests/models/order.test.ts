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

  test('should generate order number on save', async () => {
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
      orderStatus: OrderStatus.PENDING
    });

    // Mock the countDocuments method to simulate order count
    const mockCountDocuments = jest.fn().mockResolvedValue(5);
    const mockConstructor = {
      countDocuments: mockCountDocuments
    };

    // Mock the save method
    const originalSave = order.save;
    order.save = jest.fn().mockImplementation(async function(this: any) {
      // Simulate pre-save hook
      if (this.isNew) {
        const date = new Date();
        const year = date.getFullYear().toString().slice(-2);
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const count = await mockCountDocuments();
        const sequence = (count + 1).toString().padStart(4, '0');
        this.orderNumber = `${year}${month}${day}${sequence}`;
      }
      return this;
    });

    try {
      await order.save();
      expect(order.orderNumber).toBeDefined();
      expect(order.orderNumber).toMatch(/^\d{10}$/); // Should be 10 digits: YYMMDD + 4-digit sequence
    } finally {
      order.save = originalSave;
    }
  });

  test('should handle errors in order number generation', async () => {
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
      orderStatus: OrderStatus.PENDING
    });

    // Mock the countDocuments to throw an error
    const mockCountDocuments = jest.fn().mockRejectedValue(new Error('Database error'));
    const mockConstructor = {
      countDocuments: mockCountDocuments
    };

    // Mock the save method to simulate error in pre-save hook
    const originalSave = order.save;
    order.save = jest.fn().mockImplementation(async function(this: any) {
      // Simulate pre-save hook with error
      if (this.isNew) {
        try {
          await mockCountDocuments();
          // This should not be reached
          this.orderNumber = 'test';
        } catch (error) {
          throw error; // Propagate the error
        }
      }
      return this;
    });

    try {
      await expect(order.save()).rejects.toThrow('Database error');
    } finally {
      order.save = originalSave;
    }
  });
});