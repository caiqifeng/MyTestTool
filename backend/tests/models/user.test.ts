// Simple test to verify User model can be imported and used
import User from '../../src/models/User';
import { UserRole } from '@shared/types';

describe('User Model', () => {
  test('should be importable', () => {
    expect(User).toBeDefined();
    expect(typeof User).toBe('function');
  });

  test('should have static methods', () => {
    expect(User.findByOpenid).toBeDefined();
    expect(User.createOrUpdate).toBeDefined();
    expect(typeof User.findByOpenid).toBe('function');
    expect(typeof User.createOrUpdate).toBe('function');
  });

  test('should create user instance', () => {
    const user = new User({
      openid: 'test_openid',
      nickname: 'Test User',
      role: UserRole.CUSTOMER
    });

    expect(user).toBeDefined();
    expect(user.openid).toBe('test_openid');
    expect(user.nickname).toBe('Test User');
    expect(user.role).toBe(UserRole.CUSTOMER);
  });

  test('should have instance methods', () => {
    const user = new User({
      openid: 'test_openid',
      nickname: 'Test User',
      role: UserRole.ADMIN
    });

    expect(user.hasRole).toBeDefined();
    expect(user.isAdmin).toBeDefined();
    expect(typeof user.hasRole).toBe('function');
    expect(typeof user.isAdmin).toBe('function');

    expect(user.hasRole(UserRole.ADMIN)).toBe(true);
    expect(user.isAdmin()).toBe(true);
  });
});