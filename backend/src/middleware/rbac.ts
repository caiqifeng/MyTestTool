import { Request, Response, NextFunction } from 'express';
import { UserRole } from '../../../shared/src/types';

export const requireRole = (role: UserRole | UserRole[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Authentication required'
      });
    }

    const requiredRoles = Array.isArray(role) ? role : [role];
    const hasRole = requiredRoles.includes(req.user.role);

    if (!hasRole) {
      return res.status(403).json({
        success: false,
        message: 'Insufficient permissions'
      });
    }

    next();
  };
};

// 检查是否是管理员（admin或staff）
export const requireAdmin = requireRole([UserRole.ADMIN, UserRole.STAFF]);

// 检查是否是普通用户
export const requireCustomer = requireRole(UserRole.CUSTOMER);