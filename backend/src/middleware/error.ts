import { Request, Response, NextFunction } from 'express';
import config from '../config';

interface AppError extends Error {
  statusCode?: number;
  code?: number;
}

export const errorMiddleware = (
  error: AppError,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const statusCode = error.statusCode || 500;
  const message = error.message || 'Internal Server Error';

  // 记录错误
  if (config.env !== 'test') {
    console.error(`[${new Date().toISOString()}] ${req.method} ${req.url}`, {
      error: message,
      stack: config.env === 'development' ? error.stack : undefined,
      body: req.body,
      query: req.query,
      params: req.params
    });
  }

  res.status(statusCode).json({
    success: false,
    message,
    ...(config.env === 'development' && { stack: error.stack })
  });
};

// 404处理中间件
export const notFoundMiddleware = (req: Request, res: Response) => {
  res.status(404).json({
    success: false,
    message: `Route ${req.method} ${req.url} not found`
  });
};

// 异步错误包装器
export const asyncHandler = (fn: Function) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};