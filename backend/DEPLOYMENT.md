# 生产环境部署指南

## 环境要求

- Node.js 18 LTS 或更高版本
- Docker 和 Docker Compose（可选，用于容器化部署）
- MongoDB 4.4+ 或 MongoDB Atlas
- Redis 6.0+
- 微信小程序商户号（用于支付功能）

## 配置文件

### 环境变量

复制 `.env.production` 为 `.env` 并修改相应值：

```bash
cp .env.production .env
```

重要环境变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `NODE_ENV` | 环境标识 | `production` |
| `PORT` | 服务端口 | `3000` |
| `MONGODB_URI` | MongoDB 连接字符串 | `mongodb://localhost:27017/break_mini_app` |
| `JWT_SECRET` | JWT 签名密钥 | 随机长字符串 |
| `WECHAT_APP_ID` | 微信小程序 AppID | 小程序后台获取 |
| `WECHAT_APP_SECRET` | 微信小程序 AppSecret | 小程序后台获取 |
| `WECHAT_MCH_ID` | 微信支付商户号 | 商户平台获取 |
| `WECHAT_API_KEY` | 微信支付 API 密钥 | 商户平台设置 |
| `WECHAT_API_V3_KEY` | 微信支付 API V3 密钥 | 商户平台设置 |
| `WECHAT_USE_MOCK_PAYMENT` | 是否使用模拟支付 | `false`（生产环境必须为 false） |
| `WECHAT_CERT_PATH` | 微信支付证书路径 | `/app/cert/wechat_cert.pem` |
| `WECHAT_KEY_PATH` | 微信支付密钥路径 | `/app/cert/wechat_key.pem` |
| `REDIS_URL` | Redis 连接字符串 | `redis://localhost:6379` |
| `CORS_ORIGIN` | 允许跨域源 | `https://your-mini-app-domain.com` |

### 微信支付证书

1. 登录微信支付商户平台
2. 下载 API 证书（V3）
3. 将证书文件（.pem）放置到 `cert/` 目录
4. 确保 `.env` 中的证书路径正确

## 部署方式

### 方式一：Docker 部署（推荐）

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

### 方式二：传统部署

#### 1. 安装依赖

```bash
npm ci --only=production
```

#### 2. 构建应用

```bash
npm run build
```

#### 3. 启动服务

```bash
# 使用 PM2（推荐）
npm install -g pm2
pm2 start dist/index.js --name "break-mini-app"

# 或直接启动
npm start
```

#### 4. 配置 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # 静态文件缓存
    location /uploads/ {
        alias /path/to/app/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

## 健康检查

服务启动后，可以通过以下端点检查健康状态：

```bash
# 健康检查
curl http://localhost:3000/health

# 响应示例
{
  "success": true,
  "message": "Server is healthy",
  "timestamp": "2026-04-13T13:45:00.000Z",
  "uptime": 3600
}
```

## 监控和日志

### 日志配置

日志默认输出到控制台，生产环境建议配置日志轮转：

```bash
# 使用 PM2 日志管理
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 30
```

### 监控指标

应用暴露以下监控端点：

- `/health` - 健康状态
- `/metrics` - 性能指标（待实现）

## 安全建议

1. **环境变量保护**：确保 `.env` 文件不被提交到版本控制系统
2. **防火墙配置**：只开放必要端口（如 80, 443, 3000）
3. **数据库安全**：为 MongoDB 和 Redis 设置强密码
4. **HTTPS 强制**：生产环境必须使用 HTTPS
5. **定期更新**：保持依赖包和系统安全更新

## 故障排除

### 常见问题

1. **端口占用**
   ```bash
   # 检查端口占用
   lsof -i :3000
   # 或修改 .env 中的 PORT 值
   ```

2. **数据库连接失败**
   - 检查 MongoDB 服务状态
   - 验证连接字符串
   - 检查网络防火墙设置

3. **微信支付回调失败**
   - 确保回调 URL 可公开访问
   - 验证签名算法
   - 检查证书路径和权限

### 日志分析

查看应用日志获取详细错误信息：

```bash
# Docker 部署
docker-compose logs backend

# PM2 部署
pm2 logs break-mini-app
```

## 备份和恢复

### MongoDB 备份

```bash
# 备份数据库
mongodump --uri="mongodb://localhost:27017/break_mini_app" --out=/backup/mongodb-$(date +%Y%m%d)

# 恢复数据库
mongorestore --uri="mongodb://localhost:27017/break_mini_app" /backup/mongodb-20260413
```

### Redis 备份

```bash
# 创建快照
redis-cli SAVE

# 快照文件位置
/var/lib/redis/dump.rdb
```

## 版本升级

1. 备份数据库和配置文件
2. 更新代码和依赖
3. 运行数据库迁移（如果有）
4. 重启服务
5. 验证功能

---

如需更多帮助，请查看详细文档或联系开发团队。