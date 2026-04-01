import jwt from 'jsonwebtoken';
import config from '../config';
import { UserRole } from '../../../shared/src/types';

interface TokenPayload {
  userId: string;
  role: UserRole;
  openid?: string;
}

export class JWTService {
  static generateToken(payload: TokenPayload): string {
    return jwt.sign(payload, config.jwtSecret, {
      expiresIn: '7d'
    });
  }

  static verifyToken(token: string): TokenPayload {
    try {
      return jwt.verify(token, config.jwtSecret) as TokenPayload;
    } catch (error) {
      throw new Error('Invalid token');
    }
  }

  static generateRefreshToken(payload: TokenPayload): string {
    return jwt.sign(payload, config.jwtSecret, {
      expiresIn: '30d'
    });
  }

  static decodeToken(token: string): TokenPayload | null {
    try {
      return jwt.decode(token) as TokenPayload;
    } catch (error) {
      return null;
    }
  }
}

export default JWTService;