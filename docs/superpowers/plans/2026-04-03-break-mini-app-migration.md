# Break-Mini-App 迁移实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 break-mini-app 项目从 worktree 位置迁移到目标目录，创建独立副本用于后续开发

**Architecture:** 使用 robocopy 复制文件（排除 .git 和 node_modules），在目标位置重新安装依赖，验证功能完整性

**Tech Stack:** Windows robocopy, Node.js/npm, Git

---

### Task 1: 准备目标目录

**Files:**
- 检查目录: `F:\caiqifeng\MyTestProject\MyTestTool\`
- 创建目录: `F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app`

- [ ] **Step 1: 检查目标目录是否存在**

```bash
if exist "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app" (
    echo Directory exists, need to clean up
    exit /b 1
) else (
    echo Directory does not exist, proceed
)
```

预期：如果目录存在则退出，否则继续

- [ ] **Step 2: 检查现有 break_mini_app 目录**

```bash
dir "F:\caiqifeng\MyTestProject\MyTestTool\break_mini_app"
```

预期：显示 break_mini_app 目录内容，确认不冲突

- [ ] **Step 3: 创建目标目录**

```bash
mkdir "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app"
dir "F:\caiqifeng\MyTestProject\MyTestTool\"
```

预期：显示创建的 break-mini-app 目录

---

### Task 2: 使用 robocopy 复制文件

**Files:**
- 源目录: `C:\Users\admin\.config\superpowers\worktrees\MyTestTool\feature\break-mini-app`
- 目标目录: `F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app`

- [ ] **Step 1: 运行 robocopy 复制（排除 .git 和 node_modules）**

```bash
robocopy "C:\Users\admin\.config\superpowers\worktrees\MyTestTool\feature\break-mini-app" "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app" /E /COPY:DAT /R:3 /W:10 /XF .DS_Store *.tmp *.log /XD .git node_modules dist build
```

参数说明：
- `/E`: 复制子目录，包括空目录
- `/COPY:DAT`: 复制数据、属性和时间戳
- `/R:3`: 失败重试3次
- `/W:10`: 重试等待10秒
- `/XF`: 排除文件（.DS_Store, *.tmp, *.log）
- `/XD`: 排除目录（.git, node_modules, dist, build）

预期：显示复制统计信息，ExitCode 为 0-7 表示成功

- [ ] **Step 2: 验证复制结果**

```bash
dir "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app" /s | find /c "File(s)"
```

预期：显示复制的文件数量

- [ ] **Step 3: 检查关键文件是否存在**

```bash
dir "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\package.json"
dir "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\backend\package.json"
dir "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\frontend\package.json"
dir "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\shared\package.json"
```

预期：显示所有 package.json 文件存在

- [ ] **Step 4: 验证 .git 目录被排除**

```bash
if exist "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\.git" (
    echo ERROR: .git directory was not excluded
    exit /b 1
) else (
    echo SUCCESS: .git directory excluded
)
```

预期：成功消息，没有 .git 目录

---

### Task 3: 在目标位置安装依赖

**Files:**
- 修改: `F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\package.json`

- [ ] **Step 1: 导航到目标目录并检查 package-lock.json**

```bash
cd /d "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app"
dir package-lock.json
```

预期：显示 package-lock.json 文件存在（约 500KB）

- [ ] **Step 2: 安装根目录依赖**

```bash
npm install
dir node_modules
```

预期：显示 node_modules 目录创建成功

- [ ] **Step 3: 安装 backend 依赖**

```bash
cd backend
npm install
cd ..
```

预期：backend/node_modules 目录创建成功

- [ ] **Step 4: 安装 frontend 依赖**

```bash
cd frontend
npm install
cd ..
```

预期：frontend/node_modules 目录创建成功

- [ ] **Step 5: 安装 shared 依赖**

```bash
cd shared
npm install
cd ..
```

预期：shared/node_modules 目录创建成功

- [ ] **Step 6: 验证依赖安装**

```bash
npm list --depth=0
cd backend && npm list --depth=0 && cd ..
cd frontend && npm list --depth=0 && cd ..
```

预期：显示所有依赖包列表，无错误

---

### Task 4: 验证迁移完整性

**Files:**
- 测试: `F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\backend` 中的测试文件

- [ ] **Step 1: 运行后端测试**

```bash
cd /d "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\backend"
npm test
```

预期：37 个测试全部通过

- [ ] **Step 2: 检查前端构建**

```bash
cd /d "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\frontend"
npm run build
```

预期：构建成功，无错误

- [ ] **Step 3: 调整前端测试脚本（如有需要）**

检查 frontend/package.json 中的 test 脚本：

```bash
type package.json | findstr "test"
```

如果 test 脚本没有 `--passWithNoTests` 选项，可能需要添加：

```bash
# 检查是否需要修改
npm test 2>&1 | findstr "No tests found"
```

预期：可能需要修改测试脚本以避免无测试失败

- [ ] **Step 4: 运行完整项目测试**

```bash
cd /d "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app"
npm test
```

预期：后端测试通过，前端测试处理得当

---

### Task 5: 初始化 Git 仓库（可选）

**Files:**
- 创建: `F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\.gitignore`
- 修改: 根据需要

- [ ] **Step 1: 初始化 Git 仓库**

```bash
cd /d "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app"
git init
```

预期：显示 "Initialized empty Git repository"

- [ ] **Step 2: 创建 .gitignore 文件**

```bash
echo node_modules/ > .gitignore
echo dist/ >> .gitignore
echo build/ >> .gitignore
echo .DS_Store >> .gitignore
echo *.log >> .gitignore
echo *.tmp >> .gitignore
type .gitignore
```

预期：显示 .gitignore 文件内容

- [ ] **Step 3: 添加文件并创建初始提交**

```bash
git add .
git commit -m "Initial commit: break-mini-app migrated from worktree"
git status
```

预期：显示 "nothing to commit, working tree clean"

---

### Task 6: 最终验证和清理

**Files:**
- 验证所有迁移步骤完成

- [ ] **Step 1: 检查目录结构**

```bash
cd /d "F:\caiqifeng\MyTestProject\MyTestTool"
tree break-mini-app /F /A | head -50
```

预期：显示完整的目录结构

- [ ] **Step 2: 验证与源目录比较**

```bash
# 检查关键文件数量
dir "C:\Users\admin\.config\superpowers\worktrees\MyTestTool\feature\break-mini-app\backend\src" /s /b | find /c ".js" > source_count.txt
dir "F:\caiqifeng\MyTestProject\MyTestTool\break-mini-app\backend\src" /s /b | find /c ".js" > target_count.txt
fc source_count.txt target_count.txt
```

预期：文件数量相同

- [ ] **Step 3: 清理临时文件**

```bash
del source_count.txt target_count.txt 2>nul
echo Migration completed successfully
```

预期：清理成功，显示完成消息