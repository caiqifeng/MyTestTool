import Coupon from '../../src/models/Coupon';

describe('Coupon Model', () => {
  test('should be importable', () => {
    expect(Coupon).toBeDefined();
    expect(typeof Coupon).toBe('function');
  });

  test('should create coupon instance', () => {
    const coupon = new Coupon({
      code: 'TEST2024',
      name: 'Test Coupon',
      description: 'Test coupon description',
      discountType: 'percentage',
      discountValue: 20,
      minPurchaseAmount: 50,
      maxDiscountAmount: 30,
      startDate: new Date('2024-01-01'),
      endDate: new Date('2024-12-31'),
      usageLimit: 100,
      usedCount: 0,
      isActive: true,
      applicableCategories: ['category1', 'category2']
    });

    expect(coupon).toBeDefined();
    expect(coupon.code).toBe('TEST2024');
    expect(coupon.name).toBe('Test Coupon');
    expect(coupon.discountType).toBe('percentage');
    expect(coupon.discountValue).toBe(20);
    expect(coupon.minPurchaseAmount).toBe(50);
    expect(coupon.isActive).toBe(true);
  });

  test('should have instance methods', () => {
    const coupon = new Coupon({
      code: 'TEST2024',
      name: 'Test Coupon',
      discountType: 'percentage',
      discountValue: 20,
      startDate: new Date('2024-01-01'),
      endDate: new Date('2024-12-31'),
      isActive: true
    });

    expect(coupon.canApplyToOrder).toBeDefined();
    expect(coupon.calculateDiscount).toBeDefined();
    expect(typeof coupon.canApplyToOrder).toBe('function');
    expect(typeof coupon.calculateDiscount).toBe('function');
  });
});