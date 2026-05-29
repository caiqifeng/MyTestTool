import { Request, Response, NextFunction } from 'express';
import { validationResult } from 'express-validator';

export const validate = (validations: any[]) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    await Promise.all(validations.map(validation => validation.run(req)));

    const errors = validationResult(req);
    if (errors.isEmpty()) {
      return next();
    }

    res.status(400).json({
      success: false,
      message: 'Validation failed',
      errors: errors.array()
    });
  };
};

// 通用验证规则
export const commonValidators = {
  objectId: (field: string) => ({
    custom: {
      options: (value: string) => {
        if (!value) return true;
        return /^[0-9a-fA-F]{24}$/.test(value);
      },
      errorMessage: `${field} must be a valid ObjectId`
    }
  }),

  email: {
    isEmail: true,
    errorMessage: 'Invalid email address'
  },

  phone: {
    matches: {
      options: /^1[3-9]\d{9}$/,
      errorMessage: 'Invalid phone number format'
    }
  },

  password: {
    isLength: {
      options: { min: 6 },
      errorMessage: 'Password must be at least 6 characters long'
    }
  },

  positiveNumber: (field: string) => ({
    custom: {
      options: (value: number) => value > 0,
      errorMessage: `${field} must be a positive number`
    }
  }),

  nonNegativeNumber: (field: string) => ({
    custom: {
      options: (value: number) => value >= 0,
      errorMessage: `${field} must be a non-negative number`
    }
  })
};