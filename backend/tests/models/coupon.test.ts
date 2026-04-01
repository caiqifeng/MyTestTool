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
    const now = new Date();
    const startDate = new Date(now.getTime() - 86400000); // Yesterday
    const endDate = new Date(now.getTime() + 86400000); // Tomorrow

    const coupon = new Coupon({
      code: 'TEST2026',
      name: 'Test Coupon',
      discountType: 'percentage',
      discountValue: 20,
      startDate: startDate,
      endDate: endDate,
      isActive: true
    });

    expect(coupon.canApplyToOrder).toBeDefined();
    expect(coupon.calculateDiscount).toBeDefined();
    expect(typeof coupon.canApplyToOrder).toBe('function');
    expect(typeof coupon.calculateDiscount).toBe('function');
  });

  test('should have virtual property isValid', () => {
    const now = new Date();
    const startDate = new Date(now.getTime() - 86400000); // Yesterday
    const endDate = new Date(now.getTime() + 86400000); // Tomorrow

    const coupon = new Coupon({
      code: 'TEST2026',
      name: 'Test Coupon',
      discountType: 'percentage',
      discountValue: 20,
      startDate: startDate,
      endDate: endDate,
      isActive: true,
      usedCount: 0,
      usageLimit: 100
    });

    expect(coupon.isValid).toBeDefined();
    // The coupon should be valid since dates are in range and usage limit not exceeded
    expect(coupon.isValid).toBe(true);
  });

  test('canApplyToOrder should validate correctly', () => {
    const now = new Date();
    const startDate = new Date(now.getTime() - 86400000); // Yesterday
    const endDate = new Date(now.getTime() + 86400000); // Tomorrow

    const coupon = new Coupon({
      code: 'TEST2026',
      name: 'Test Coupon',
      discountType: 'percentage',
      discountValue: 20,
      minPurchaseAmount: 50,
      startDate: startDate,
      endDate: endDate,
      isActive: true,
      applicableCategories: ['cat1', 'cat2'],
      applicableProducts: ['prod1', 'prod2']
    });

    // Test with sufficient order amount
    expect(coupon.canApplyToOrder(100)).toBe(true);

    // Test with insufficient order amount
    expect(coupon.canApplyToOrder(30)).toBe(false);

    // Test with matching categories
    expect(coupon.canApplyToOrder(100, undefined, ['cat1'])).toBe(true);

    // Test with non-matching categories
    expect(coupon.canApplyToOrder(100, undefined, ['cat3'])).toBe(false);

    // Test with matching products
    expect(coupon.canApplyToOrder(100, ['prod1'])).toBe(true);

    // Test with non-matching products
    expect(coupon.canApplyToOrder(100, ['prod3'])).toBe(false);
  });

  test('calculateDiscount should work correctly', () => {
    const now = new Date();
    const startDate = new Date(now.getTime() - 86400000); // Yesterday
    const endDate = new Date(now.getTime() + 86400000); // Tomorrow

    // Test percentage discount
    const percentageCoupon = new Coupon({
      code: 'PERCENT20',
      name: '20% Off',
      discountType: 'percentage',
      discountValue: 20,
      maxDiscountAmount: 30,
      startDate: startDate,
      endDate: endDate,
      isActive: true
    });

    expect(percentageCoupon.calculateDiscount(100)).toBe(20); // 20% of 100 = 20
    expect(percentageCoupon.calculateDiscount(200)).toBe(30); // 20% of 200 = 40, capped at 30

    // Test fixed discount
    const fixedCoupon = new Coupon({
      code: 'FIXED10',
      name: '$10 Off',
      discountType: 'fixed',
      discountValue: 10,
      startDate: startDate,
      endDate: endDate,
      isActive: true
    });

    expect(fixedCoupon.calculateDiscount(100)).toBe(10);
    expect(fixedCoupon.calculateDiscount(5)).toBe(5); // Discount cannot exceed order amount
  });
});