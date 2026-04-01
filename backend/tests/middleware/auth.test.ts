import { Request, Response, NextFunction } from 'express';
import { authMiddleware } from '../../src/middleware/auth';
import JWTService from '../../src/utils/jwt';

jest.mock('../../src/utils/jwt');

describe('Auth Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: NextFunction;

  beforeEach(() => {
    mockRequest = {
      headers: {}
    };
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    nextFunction = jest.fn();
  });

  test('should return 401 if no authorization header', () => {
    authMiddleware(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(mockResponse.json).toHaveBeenCalledWith({
      success: false,
      message: 'No authorization token provided'
    });
    expect(nextFunction).not.toHaveBeenCalled();
  });

  test('should return 401 if token format is invalid', () => {
    mockRequest.headers = {
      authorization: 'InvalidFormat'
    };

    authMiddleware(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(mockResponse.json).toHaveBeenCalledWith({
      success: false,
      message: 'Invalid token format'
    });
    expect(nextFunction).not.toHaveBeenCalled();
  });

  test('should return 401 if token is invalid', () => {
    mockRequest.headers = {
      authorization: 'Bearer invalid.token.here'
    };

    (JWTService.verifyToken as jest.Mock).mockImplementation(() => {
      throw new Error('Invalid token');
    });

    authMiddleware(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(mockResponse.json).toHaveBeenCalledWith({
      success: false,
      message: 'Invalid token'
    });
    expect(nextFunction).not.toHaveBeenCalled();
  });

  test('should attach user to request and call next if token is valid', () => {
    const mockUser = {
      userId: '123',
      role: 'customer',
      openid: 'test_openid'
    };

    mockRequest.headers = {
      authorization: 'Bearer valid.token.here'
    };

    (JWTService.verifyToken as jest.Mock).mockReturnValue(mockUser);

    authMiddleware(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockRequest.user).toEqual(mockUser);
    expect(nextFunction).toHaveBeenCalled();
    expect(mockResponse.status).not.toHaveBeenCalled();
    expect(mockResponse.json).not.toHaveBeenCalled();
  });
});