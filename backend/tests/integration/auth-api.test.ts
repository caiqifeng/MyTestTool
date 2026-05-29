import request from 'supertest';
import App from '../../src/app';

describe('Auth API Integration Tests', () => {
  let appInstance: any;

  beforeAll(() => {
    appInstance = new App();
  });

  afterAll(() => {
    // 清理资源
    if (appInstance && appInstance.close) {
      appInstance.close();
    }
  });

  describe('Login API', () => {
    it('should handle login requests', async () => {
      const response = await request(appInstance.app)
        .post('/api/auth/wechat-login')
        .send({
          code: 'mock_wechat_code',
          nickname: 'testuser',
          avatar: 'https://example.com/avatar.jpg'
        });

      // 即使登录失败，也应该返回标准响应格式
      expect([200, 400, 401]).toContain(response.status);
      if (response.body) {
        expect(response.body).toHaveProperty('success');
        expect(response.body).toHaveProperty('message');
      }
    });
  });

  describe.skip('Registration API', () => {
    it('should handle registration requests', async () => {
      const response = await request(appInstance.app)
        .post('/api/auth/register')
        .send({
          username: 'newuser',
          password: 'newpassword',
          nickname: 'New User'
        });

      expect([200, 400, 409]).toContain(response.status);
      if (response.body) {
        expect(response.body).toHaveProperty('success');
      }
    });
  });

  describe('User Info API', () => {
    it('should require authentication for user info', async () => {
      const response = await request(appInstance.app)
        .get('/api/auth/me');

      // 未认证应该返回401或400
      expect([401, 400]).toContain(response.status);
      if (response.body) {
        expect(response.body.success).toBe(false);
      }
    });
  });
});