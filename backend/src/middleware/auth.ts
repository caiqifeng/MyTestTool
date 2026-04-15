import { Request, Response, NextFunction } from 'express';
import JWTService from '../utils/jwt';
import { UserRole } from '../../../shared/src/types';
import config from '../config';

declare global {
  namespace Express {
    interface Request {
      user?: {
        userId: string;
        role: UserRole;
        openid?: string;
      };
    }
  }
}

export const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization;

  // 开发环境模拟用户
  if (config.env !== 'production' && !authHeader) {
    req.user = {
      userId: 'dev_user_001',
      role: UserRole.CUSTOMER,
      openid: 'dev_openid_001'
    };
    return next();
  }

  if (!authHeader) {
    return res.status(401).json({
      success: false,
      message: 'No authorization token provided'
    });
  }

  const tokenParts = authHeader.split(' ');

  if (tokenParts.length !== 2 || tokenParts[0] !== 'Bearer') {
    return res.status(401).json({
      success: false,
      message: 'Invalid token format'
    });
  }

  const token = tokenParts[1];

  try {
    // 检查是否为模拟管理员令牌
    if (token === 'mock_jwt_token_for_admin') {
      req.user = {
        userId: 'admin_001',
        role: UserRole.ADMIN,
        openid: 'mock_openid_admin'
      };
      next();
    } else {
      const decoded = JWTService.verifyToken(token);
      req.user = decoded;
      next();
    }
  } catch (error) {
    return res.status(401).json({
      success: false,
      message: 'Invalid token'
    });
  }
};

// 可选的认证中间件，不强制要求登录
export const optionalAuthMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return next();
  }

  const tokenParts = authHeader.split(' ');

  if (tokenParts.length !== 2 || tokenParts[0] !== 'Bearer') {
    return next();
  }

  const token = tokenParts[1];

  try {
    const decoded = JWTService.verifyToken(token);
    req.user = decoded;
    next();
  } catch (error) {
    next();
  }
};