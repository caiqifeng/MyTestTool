import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import mongoose from 'mongoose';
import config from './config';
import { errorMiddleware, notFoundMiddleware } from './middleware/error';
import { authMiddleware } from './middleware/auth';
import { requireAdmin } from './middleware/rbac';

// 导入路由
import authRoutes from './routes/auth.routes';
import productRoutes from './routes/product.routes';
import orderRoutes from './routes/order.routes';
import cartRoutes from './routes/cart.routes';
import addressRoutes from './routes/address.routes';
import couponRoutes from './routes/coupon.routes';
import bannerRoutes from './routes/banner.routes';
import categoryRoutes from './routes/category.routes';

class App {
  public app: express.Application;

  constructor() {
    this.app = express();
    this.connectDatabase();
    this.initializeMiddlewares();
    this.initializeRoutes();
    this.initializeErrorHandling();
  }

  private connectDatabase(): void {
    mongoose
      .connect(config.mongodbUri)
      .then(() => {
        console.log('Connected to MongoDB');
      })
      .catch((error) => {
        console.error('MongoDB connection error:', error);
        process.exit(1);
      });

    mongoose.connection.on('error', (error) => {
      console.error('MongoDB error:', error);
    });

    mongoose.connection.on('disconnected', () => {
      console.log('MongoDB disconnected');
    });
  }

  private initializeMiddlewares(): void {
    // 安全中间件
    this.app.use(helmet());

    // CORS配置
    this.app.use(cors({
      origin: config.corsOrigin,
      credentials: true
    }));

    // 请求体解析
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // 速率限制
    if (config.env === 'production') {
      this.app.use(rateLimit(config.rateLimit));
    }

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

    // 静态文件服务（如果需要）
    this.app.use('/uploads', express.static('uploads'));
  }

  private initializeErrorHandling(): void {
    // 404处理
    this.app.use(notFoundMiddleware);

    // 全局错误处理
    this.app.use(errorMiddleware);
  }

  public start(): void {
    this.app.listen(config.port, () => {
      console.log(`Server is running on port ${config.port}`);
      console.log(`Environment: ${config.env}`);
      console.log(`MongoDB: ${config.mongodbUri}`);
    });
  }
}

export default App;