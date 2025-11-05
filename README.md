## anyroute-login
## 多账号自动登录 AnyRoute 并保存登录状态

支持通过 **linux.do OAuth 认证**登录 anyrouter.top

## 快速开始

1. 克隆本仓库：

   ```bash
   git clone https://github.com/yourusername/anyroute-login.git
   cd anyroute-login
   ```

2. 安装 Playwright：
    ```bash
    pip install playwright
    ```

3. 安装浏览器驱动（推荐使用 Firefox）：
    ```bash
    playwright install firefox
    ```

4. 安装环境：
    ```bash
    uv sync
    ```

5. 运行：
    ```bash
    uv run app.py
    ```

## 功能说明

### 1. 一键登录所有账号
- 同时打开所有已配置的账号
- 自动使用保存的 cookie 登录

### 2. 增加账号
- **步骤1**: 先登录 linux.do 认证账号
- **步骤2**: 使用 linux.do OAuth 登录 anyrouter
- 自动保存两个网站的 cookie

### 3. 删除账号
- 删除账号配置
- 同时删除 anyrouter 和 linux.do 的 cookie 文件

### 4. 维护账号（更新cookie）
- 当 cookie 过期时使用
- **步骤1**: 重新登录 linux.do 更新认证
- **步骤2**: 重新登录 anyrouter

### 5. 查看账号列表
- 显示所有已配置的账号
- 显示登录状态

## 登录流程说明

anyrouter 使用 linux.do 的 OAuth 认证：

1. 打开 anyrouter.top/login
2. 点击 "linux.do" 登录按钮
3. 跳转到 linux.do OAuth 授权页面
4. 使用 linux.do 账号授权
5. 自动跳回 anyrouter 完成登录

本工具会：
- 保存 linux.do 的登录状态（`auth_account*.json`）
- 保存 anyrouter 的登录状态（`account*.json`）
- 下次登录时自动使用保存的状态

## 文件说明

- `accounts_config.json` - 账号配置文件
- `account*.json` - anyrouter 的登录 cookie
- `auth_account*.json` - linux.do 认证账号的 cookie