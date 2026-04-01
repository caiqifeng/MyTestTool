import dotenv from 'dotenv';
import path from 'path';

// 加载环境变量
dotenv.config();

interface Config {
  env: string;
  port: number;
  mongodbUri: string;
  jwtSecret: string;
  wechat: {
    appId: string;
    appSecret: string;
    mchId: string;
    apiKey: string;
  };
  redisUrl: string;
  corsOrigin: string[];
  rateLimit: {
    windowMs: number;
    max: number;
  };
}

const config: Config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '3000', 10),
  mongodbUri: process.env.MONGODB_URI || 'mongodb://localhost:27017/break_mini_app',
  jwtSecret: process.env.JWT_SECRET || 'your_jwt_secret_key_here',
  wechat: {
    appId: process.env.WECHAT_APP_ID || '',
    appSecret: process.env.WECHAT_APP_SECRET || '',
    mchId: process.env.WECHAT_MCH_ID || '',
    apiKey: process.env.WECHAT_API_KEY || ''
  },
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',
  corsOrigin: (process.env.CORS_ORIGIN || 'http://localhost:8080').split(','),
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15分钟
    max: 100 // 每个IP每15分钟100个请求
  }
};

// 验证必要环境变量
if (config.env === 'production') {
  const requiredEnvVars = ['JWT_SECRET', 'MONGODB_URI'];
  for (const envVar of requiredEnvVars) {
    if (!process.env[envVar]) {
      throw new Error(`Missing required environment variable: ${envVar}`);
    }
  }
}

export default config;