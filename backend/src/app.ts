// import 'module-alias/register';
console.log('app.ts: Starting imports...');
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import mongoose from 'mongoose';
import path from 'path';
import config from './config';
import { errorMiddleware, notFoundMiddleware } from './middleware/error';
import { authMiddleware } from './middleware/auth';
import { requireAdmin } from './middleware/rbac';
console.log('app.ts: Imports completed');

// 导入路由
import authRoutes from './routes/auth.routes';
import productRoutes from './routes/product.routes';
import orderRoutes from './routes/order.routes';
import cartRoutes from './routes/cart.routes';
import addressRoutes from './routes/address.routes';
import couponRoutes from './routes/coupon.routes';
import bannerRoutes from './routes/banner.routes';
import categoryRoutes from './routes/category.routes';
import ProductController from './controllers/product.controller';

class App {
  public app: express.Application;

  constructor() {
    try {
      console.log('App constructor start');
      this.app = express();
      this.connectDatabase();
      this.initializeMiddlewares();
      this.initializeRoutes();
      this.initializeErrorHandling();
      console.log('App constructor end');
    } catch (error) {
      console.error('App constructor error:', error);
      throw error;
    }
  }

  private connectDatabase(): void {
    console.log('Skipping MongoDB connection for development');
    // 为了开发测试，跳过数据库连接
    // 实际使用时需要连接MongoDB
  }

  private initializeMiddlewares(): void {
    // 安全中间件 - 配置CSP允许内联事件处理器
    this.app.use(
      helmet({
        contentSecurityPolicy: {
          useDefaults: false,
          directives: {
            defaultSrc: ["'self'"],
            scriptSrc: ["'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'"],
            styleSrc: ["'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'"],
            fontSrc: ["'self'", "https://cdn.jsdelivr.net"],
            imgSrc: ["'self'", "data:", "https:"],
            connectSrc: ["'self'"],
            baseUri: ["'self'"],
            formAction: ["'self'"],
            frameAncestors: ["'self'"],
            objectSrc: ["'none'"],
            scriptSrcAttr: ["'unsafe-inline'"],
            upgradeInsecureRequests: [],
          },
        },
      })
    );

    // CORS配置
    this.app.use(cors({
      origin: config.env === 'development' ? '*' : config.corsOrigin,
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
    }));


    // 请求体解析
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // 速率限制
    if (config.env === 'production') {
      this.app.use(rateLimit(config.rateLimit));
    }

    // 处理OPTIONS预检请求
    this.app.options('*', (req, res) => {
      res.header('Access-Control-Allow-Origin', '*');
      res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');
      res.status(200).end();
    });

    // 请求日志
    this.app.use((req, res, next) => {
      if (config.env !== 'test') {
        console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
      }
      next();
    });
  }

  private initializeRoutes(): void {
    // 健康检查
    this.app.get('/health', (req, res) => {
      res.json({
        success: true,
        message: 'Server is healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
      });
    });

    // API路由
    this.app.use('/api/auth', authRoutes);
    this.app.use('/api/products', productRoutes);
    this.app.use('/api/orders', orderRoutes);
    this.app.use('/api/cart', cartRoutes);
    this.app.use('/api/addresses', addressRoutes);
    this.app.use('/api/coupons', couponRoutes);
    this.app.use('/api/banners', bannerRoutes);
    this.app.use('/api/categories', categoryRoutes);

    // 测试路由
    this.app.get('/api/test', (req, res) => {
      console.log('Test route called');
      res.json({ success: true, message: 'Test route works' });
    });
    // 产品测试路由（绕过验证）
    this.app.get('/api/products-test', (req, res) => {
      console.log('Products test route called');
      ProductController.getProducts(req, res, () => {});
    });

    // 静态文件服务
    this.app.use('/uploads', express.static(path.join(__dirname, '../uploads')));
    // 静态资源服务（图片、CSS、JS等）- 指向前端的static目录
    this.app.use('/static', express.static(path.join(__dirname, '../../frontend/static')));
    // 管理页面静态文件服务，禁用缓存
    this.app.use('/admin', express.static(path.join(__dirname, '../public'), {
      setHeaders: (res) => {
        res.set('Cache-Control', 'no-cache, no-store, must-revalidate');
        res.set('Pragma', 'no-cache');
        res.set('Expires', '0');
      }
    }));

    // 管理页面路由
    this.app.get('/admin', (req, res) => {
      res.sendFile('admin.html', { root: 'public' });
    });
  }

  private initializeErrorHandling(): void {
    // 404处理
    this.app.use(notFoundMiddleware);

    // 全局错误处理
    this.app.use(errorMiddleware);
  }

  public start(): void {
    console.log('Starting server on port:', config.port);
    console.log('Environment:', config.env);
    console.log('MongoDB URI:', config.mongodbUri);

    const server = this.app.listen(config.port, () => {
      console.log(`Server is running on port ${config.port}`);
      console.log(`Environment: ${config.env}`);
      console.log(`MongoDB: ${config.mongodbUri}`);
    });

    server.on('error', (error: any) => {
      console.error('Server error:', error);
      if (error.code === 'EADDRINUSE') {
        console.error(`Port ${config.port} is already in use.`);
      }
    });
  }

  public close(): void {
    // 清理资源（如果有）
    console.log('App closed');
  }
}

export default App;