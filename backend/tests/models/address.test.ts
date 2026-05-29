import Address from '../../src/models/Address';

describe('Address Model', () => {
  test('should be importable', () => {
    expect(Address).toBeDefined();
    expect(typeof Address).toBe('function');
  });

  test('should create address instance', () => {
    const address = new Address({
      userId: 'test_user_id',
      contactName: 'Test User',
      contactPhone: '13800138000',
      province: 'Test Province',
      city: 'Test City',
      district: 'Test District',
      detail: 'Test Address Detail',
      isDefault: true
    });

    expect(address).toBeDefined();
    expect(address.userId).toBe('test_user_id');
    expect(address.contactName).toBe('Test User');
    expect(address.contactPhone).toBe('13800138000');
    expect(address.province).toBe('Test Province');
    expect(address.detail).toBe('Test Address Detail');
    expect(address.isDefault).toBe(true);
  });
});