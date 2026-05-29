# Break-Mini-App 迁移设计方案

## 概述
将 `break-mini-app` 项目从 worktree 位置迁移到目标目录，创建独立副本用于后续开发。

## 迁移目标
1. 在 `F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app` 创建项目完整副本
2. 排除 `.git` 历史，创建新仓库
3. 排除 `node_modules` 依赖，在目标位置重新安装
4. 保持现有 `break_mini_app` 目录不受影响
5. 确保迁移后项目功能完整（后端测试通过）

## 方案选择
**robocopy（Windows 原生工具）**
- 优势：Windows 内置，稳定，支持大文件复制和断点续传
- 排除模式可精细控制
- 重新安装依赖确保环境一致性

## 源目录和目标目录
- **源目录**: `C:\Users\admin\.config\superpowers\worktrees\MyTestTool\feature\break-mini-app`
- **目标目录**: `F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app`

## 详细步骤

### 1. 准备工作
- 检查目标目录是否存在，若存在则清理
- 创建目标目录结构

### 2. 复制文件（排除特定目录）
使用 robocopy 命令，排除以下内容：
- `.git/` - Git 版本控制目录
- `node_modules/` - Node.js 依赖（467MB，重新安装）
- 临时文件、构建产物等

### 3. 依赖安装
- 在目标目录执行 `npm install`
- 验证依赖安装成功

### 4. 验证迁移
- 检查关键文件完整性
- 运行 `npm test` 执行后端测试（37个测试）
- 调整前端测试脚本（添加 `--passWithNoTests` 避免失败）

### 5. 初始化 Git 仓库（可选）
- 初始化新 Git 仓库
- 创建初始提交

## 排除列表
```
.git/
node_modules/
*.tmp
*.log
dist/（如存在）
build/（如存在）
.DS_Store（macOS 系统文件）
```

## 验证方法
1. **文件完整性检查**
   - 比较源和目标的关键文件数量
   - 验证 package.json 等配置文件存在

2. **功能验证**
   - 后端测试：`npm run test:backend`（应通过 37 个测试）
   - 前端构建：`npm run build:frontend`（检查无错误）

3. **依赖验证**
   - `npm list` 检查依赖树完整
   - 验证 node_modules 目录大小合理

## 风险与缓解
| 风险 | 缓解措施 |
|------|----------|
| 大文件复制耗时 | 排除 node_modules（467MB），重新安装依赖 |
| 文件权限丢失 | robocopy 默认保持文件属性 |
| 依赖版本不一致 | 使用相同的 package-lock.json 确保版本一致 |
| 测试失败 | 迁移前记录测试状态，迁移后对比 |

## 回滚方案
如果迁移失败：
1. 删除目标目录 `F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app`
2. 恢复源目录状态不变

## 成功标准
1. 目标目录包含项目所有源代码文件
2. 依赖安装成功，无错误
3. 后端测试全部通过（37/37）
4. 前端项目可正常构建

## 备注
- 项目为 Node.js monorepo，包含 backend、frontend、shared 工作区
- 后端使用 Express.js，前端框架待确认
- 现有测试：后端 37 个测试，前端暂无测试（需添加 --passWithNoTests 选项）