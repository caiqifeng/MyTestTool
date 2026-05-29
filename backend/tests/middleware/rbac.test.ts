import { Request, Response, NextFunction } from 'express';
import { requireRole } from '../../src/middleware/rbac';
import { UserRole } from '../../../shared/src/types';

describe('RBAC Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: NextFunction;

  beforeEach(() => {
    mockRequest = {};
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    nextFunction = jest.fn();
  });

  test('should return 401 if user not authenticated', () => {
    requireRole(UserRole.ADMIN)(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(mockResponse.json).toHaveBeenCalledWith({
      success: false,
      message: 'Authentication required'
    });
    expect(nextFunction).not.toHaveBeenCalled();
  });

  test('should return 403 if user does not have required role', () => {
    mockRequest.user = {
      userId: '123',
      role: UserRole.CUSTOMER
    };

    requireRole(UserRole.ADMIN)(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockResponse.status).toHaveBeenCalledWith(403);
    expect(mockResponse.json).toHaveBeenCalledWith({
      success: false,
      message: 'Insufficient permissions'
    });
    expect(nextFunction).not.toHaveBeenCalled();
  });

  test('should call next if user has required role', () => {
    mockRequest.user = {
      userId: '123',
      role: UserRole.ADMIN
    };

    requireRole(UserRole.ADMIN)(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(nextFunction).toHaveBeenCalled();
    expect(mockResponse.status).not.toHaveBeenCalled();
    expect(mockResponse.json).not.toHaveBeenCalled();
  });

  test('should allow multiple roles', () => {
    mockRequest.user = {
      userId: '123',
      role: UserRole.STAFF
    };

    requireRole([UserRole.ADMIN, UserRole.STAFF])(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(nextFunction).toHaveBeenCalled();
    expect(mockResponse.status).not.toHaveBeenCalled();
    expect(mockResponse.json).not.toHaveBeenCalled();
  });
});