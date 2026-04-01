import { Request, Response } from 'express';
import { UserModel } from '../models/User';
import JWTService from '../utils/jwt';
import { UserRole } from '../../../shared/src/types';
import { asyncHandler } from '../middleware/error';

export class AuthController {
  /**
   * 微信小程序登录
   * 在实际应用中，这里应该调用微信API获取openid
   * 目前模拟实现
   */
  static wechatLogin = asyncHandler(async (req: Request, res: Response) => {
    const { code, nickname, avatar } = req.body;

    // 这里应该调用微信API获取openid
    // const openid = await WechatService.getOpenid(code);
    const openid = `mock_openid_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // 创建或更新用户
    const user = await UserModel.createOrUpdate({
      openid,
      nickname: nickname || '微信用户',
      avatar: avatar || 'https://example.com/default-avatar.jpg'
    });

    // 生成JWT令牌
    const token = JWTService.generateToken({
      userId: user._id.toString(),
      role: user.role,
      openid: user.openid
    });

    const refreshToken = JWTService.generateRefreshToken({
      userId: user._id.toString(),
      role: user.role,
      openid: user.openid
    });

    res.json({
      success: true,
      data: {
        user: {
          _id: user._id,
          openid: user.openid,
          nickname: user.nickname,
          avatar: user.avatar,
          phone: user.phone,
          email: user.email,
          role: user.role,
          createdAt: user.createdAt,
          updatedAt: user.updatedAt
        },
        token,
        refreshToken
      }
    });
  });

  /**
   * 刷新访问令牌
   */
  static refreshToken = asyncHandler(async (req: Request, res: Response) => {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({
        success: false,
        message: 'Refresh token is required'
      });
    }

    try {
      const decoded = JWTService.verifyToken(refreshToken);
      const user = await UserModel.findById(decoded.userId);

      if (!user) {
        return res.status(404).json({
          success: false,
          message: 'User not found'
        });
      }

      const newToken = JWTService.generateToken({
        userId: user._id.toString(),
        role: user.role,
        openid: user.openid
      });

      res.json({
        success: true,
        data: {
          token: newToken
        }
      });
    } catch (error) {
      return res.status(401).json({
        success: false,
        message: 'Invalid refresh token'
      });
    }
  });

  /**
   * 获取当前用户信息
   */
  static getCurrentUser = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Not authenticated'
      });
    }

    const user = await UserModel.findById(req.user.userId);

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    res.json({
      success: true,
      data: {
        user: {
          _id: user._id,
          openid: user.openid,
          nickname: user.nickname,
          avatar: user.avatar,
          phone: user.phone,
          email: user.email,
          role: user.role,
          createdAt: user.createdAt,
          updatedAt: user.updatedAt
        }
      }
    });
  });

  /**
   * 更新用户信息
   */
  static updateProfile = asyncHandler(async (req: Request, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Not authenticated'
      });
    }

    const { nickname, phone, email } = req.body;
    const updates: any = {};

    if (nickname !== undefined) updates.nickname = nickname;
    if (phone !== undefined) updates.phone = phone;
    if (email !== undefined) updates.email = email;

    const user = await UserModel.findByIdAndUpdate(
      req.user.userId,
      { $set: updates },
      { new: true, runValidators: true }
    );

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    res.json({
      success: true,
      data: {
        user: {
          _id: user._id,
          openid: user.openid,
          nickname: user.nickname,
          avatar: user.avatar,
          phone: user.phone,
          email: user.email,
          role: user.role,
          createdAt: user.createdAt,
          updatedAt: user.updatedAt
        }
      }
    });
  });

  /**
   * 管理员获取用户列表
   */
  static getUsers = asyncHandler(async (req: Request, res: Response) => {
    const { page = 1, limit = 10, role, search } = req.query;
    const pageNum = parseInt(page as string);
    const limitNum = parseInt(limit as string);
    const skip = (pageNum - 1) * limitNum;

    const query: any = {};

    if (role) {
      query.role = role;
    }

    if (search) {
      query.$or = [
        { nickname: { $regex: search, $options: 'i' } },
        { phone: { $regex: search, $options: 'i' } },
        { email: { $regex: search, $options: 'i' } }
      ];
    }

    const [users, total] = await Promise.all([
      UserModel.find(query)
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limitNum),
      UserModel.countDocuments(query)
    ]);

    res.json({
      success: true,
      data: {
        users: users.map(user => ({
          _id: user._id,
          openid: user.openid,
          nickname: user.nickname,
          avatar: user.avatar,
          phone: user.phone,
          email: user.email,
          role: user.role,
          createdAt: user.createdAt,
          updatedAt: user.updatedAt
        })),
        pagination: {
          page: pageNum,
          limit: limitNum,
          total,
          pages: Math.ceil(total / limitNum)
        }
      }
    });
  });

  /**
   * 管理员更新用户角色
   */
  static updateUserRole = asyncHandler(async (req: Request, res: Response) => {
    const { userId } = req.params;
    const { role } = req.body;

    if (!Object.values(UserRole).includes(role as UserRole)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid role'
      });
    }

    const user = await UserModel.findByIdAndUpdate(
      userId,
      { $set: { role } },
      { new: true, runValidators: true }
    );

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    res.json({
      success: true,
      data: {
        user: {
          _id: user._id,
          openid: user.openid,
          nickname: user.nickname,
          avatar: user.avatar,
          phone: user.phone,
          email: user.email,
          role: user.role,
          createdAt: user.createdAt,
          updatedAt: user.updatedAt
        }
      }
    });
  });
}

export default AuthController;