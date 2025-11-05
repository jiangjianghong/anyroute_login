from playwright.sync_api import sync_playwright
import os
import json

# 配置文件路径
ACCOUNTS_CONFIG_FILE = "accounts_config.json"

LOGIN_URL = "https://anyrouter.top/login"  # anyrouter登录页
HOME_URL = "https://anyrouter.top/"       # 登录后主页
AUTH_URL = "https://linux.do/"            # 认证账号登录页（linux.do）
BROWSER_TYPE = "firefox"  # 可选: "chromium", "firefox", "webkit"


def load_accounts():
    """加载账号配置"""
    if not os.path.exists(ACCOUNTS_CONFIG_FILE):
        # 初始化默认配置
        default_accounts = [
            {
                "name": "jiangxihong",
                "storage_file": "account1.json",
                "auth_storage_file": "auth_account1.json"  # linux.do认证账号的cookie
            },
            {
                "name": "hjj",
                "storage_file": "account2.json",
                "auth_storage_file": "auth_account2.json"
            },
            {
                "name": "account3",
                "storage_file": "account3.json",
                "auth_storage_file": "auth_account3.json"
            },
        ]
        save_accounts(default_accounts)
        return default_accounts

    with open(ACCOUNTS_CONFIG_FILE, "r", encoding="utf-8") as f:
        accounts = json.load(f)
        # 向后兼容：为旧账号添加 auth_storage_file
        for i, acc in enumerate(accounts):
            if "auth_storage_file" not in acc:
                acc["auth_storage_file"] = f"auth_account{i+1}.json"
        return accounts


def save_accounts(accounts):
    """保存账号配置"""
    with open(ACCOUNTS_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, ensure_ascii=False, indent=2)


def get_browser(pw):
    """获取配置好的浏览器实例"""
    # 浏览器启动参数
    launch_args = [
        '--ignore-certificate-errors',
        '--ignore-ssl-errors',
        '--disable-web-security'
    ]

    # 根据配置选择浏览器类型
    if BROWSER_TYPE == "firefox":
        return pw.firefox.launch(headless=False, args=launch_args)
    elif BROWSER_TYPE == "webkit":
        return pw.webkit.launch(headless=False)
    else:  # chromium
        return pw.chromium.launch(headless=False, args=launch_args)


def show_menu():
    """显示主菜单"""
    print("\n" + "="*50)
    print("       AnyRoute 多账号管理系统")
    print("="*50)
    print("1. 一键登录所有账号")
    print("2. 增加账号")
    print("3. 删除账号")
    print("4. 维护账号（更新cookie）")
    print("5. 查看账号列表")
    print("0. 退出")
    print("="*50)


def login_all_accounts():
    """一键登录所有账号"""
    accounts = load_accounts()

    if not accounts:
        print("❌ 当前没有配置任何账号，请先添加账号！")
        return

    with sync_playwright() as pw:
        browser = get_browser(pw)
        contexts = []

        for acc in accounts:
            storage_file = acc["storage_file"]
            auth_storage_file = acc.get("auth_storage_file")

            # 判断是否有已保存的 anyrouter cookie
            if os.path.exists(storage_file):
                # 使用已保存 cookie 自动登录
                ctx = browser.new_context(storage_state=storage_file, ignore_https_errors=True)
                print(f"✅ [{acc['name']}] 使用已保存 cookie 自动登录")
            else:
                # 第一次登录流程
                # 先检查是否有 linux.do 认证 cookie
                if auth_storage_file and os.path.exists(auth_storage_file):
                    # 使用已保存的 linux.do cookie
                    ctx = browser.new_context(storage_state=auth_storage_file, ignore_https_errors=True)
                    print(f"✅ [{acc['name']}] 使用已保存的 linux.do 认证登录")
                else:
                    # 需要先登录 linux.do
                    ctx = browser.new_context(ignore_https_errors=True)
                    page = ctx.new_page()

                    print(f"\n📝 [{acc['name']}] 步骤1: 请先登录 linux.do")
                    page.goto(AUTH_URL)
                    print(f"⚠️  请在浏览器完成 linux.do 登录，然后回车继续...")
                    input()

                    # 保存 linux.do cookie
                    if auth_storage_file:
                        ctx.storage_state(path=auth_storage_file)
                        print(f"✅ [{acc['name']}] linux.do cookie 已保存")

                # 打开 anyrouter 登录页
                print(f"\n📝 [{acc['name']}] 步骤2: 登录 anyrouter")
                page = ctx.new_page()
                page.goto(LOGIN_URL)
                print(f"⚠️  请点击 'linux.do' 按钮完成登录，然后回车继续...")
                input()

                # 保存 anyrouter cookie
                ctx.storage_state(path=storage_file)
                print(f"✅ [{acc['name']}] anyrouter cookie 已保存到 {storage_file}")

            # 打开主页，验证是否自动登录成功
            page = ctx.new_page()
            page.goto(HOME_URL)
            contexts.append(ctx)

        print("\n✅ 所有账号窗口已打开，互不干扰。")
        input("完成操作后回车关闭所有浏览器...")

        # 关闭所有 context 和浏览器
        for ctx in contexts:
            ctx.close()
        browser.close()


def add_account():
    """增加账号"""
    accounts = load_accounts()

    print("\n--- 添加新账号 ---")
    name = input("请输入账号名称: ").strip()

    if not name:
        print("❌ 账号名称不能为空！")
        return

    # 检查账号名是否已存在
    if any(acc["name"] == name for acc in accounts):
        print(f"❌ 账号 '{name}' 已存在！")
        return

    # 生成存储文件名
    storage_file = f"account_{len(accounts) + 1}.json"
    auth_storage_file = f"auth_account_{len(accounts) + 1}.json"

    # 使用浏览器完成登录流程
    with sync_playwright() as pw:
        browser = get_browser(pw)

        # 步骤1: 先登录 linux.do 认证账号
        print(f"\n📝 步骤1: 请先登录 linux.do 认证账号")
        print(f"⚠️  浏览器将打开 {AUTH_URL}")
        print("请在浏览器中完成 linux.do 的登录...")

        ctx = browser.new_context(ignore_https_errors=True)
        page = ctx.new_page()
        page.goto(AUTH_URL)

        print("登录完成后，请回车继续...")
        input()

        # 保存 linux.do 的 cookie
        ctx.storage_state(path=auth_storage_file)
        print(f"✅ linux.do 认证账号 cookie 已保存到 {auth_storage_file}")

        # 步骤2: 使用已登录的 linux.do context 登录 anyrouter
        print(f"\n📝 步骤2: 现在登录 anyrouter")
        print(f"⚠️  浏览器将打开 {LOGIN_URL}")
        print(f"请点击 'linux.do' 登录按钮，会自动使用刚才登录的账号认证...")

        page.goto(LOGIN_URL)

        print("登录并授权完成后，请回车继续...")
        input()

        # 保存 anyrouter 的 cookie（包含认证后的状态）
        ctx.storage_state(path=storage_file)
        print(f"✅ [{name}] anyrouter cookie 已保存到 {storage_file}")

        ctx.close()
        browser.close()

    # 添加到配置
    accounts.append({
        "name": name,
        "storage_file": storage_file,
        "auth_storage_file": auth_storage_file
    })
    save_accounts(accounts)
    print(f"✅ 账号 '{name}' 添加成功！")


def delete_account():
    """删除账号"""
    accounts = load_accounts()

    if not accounts:
        print("❌ 当前没有任何账号！")
        return

    print("\n--- 删除账号 ---")
    list_accounts()

    name = input("\n请输入要删除的账号名称: ").strip()

    # 查找账号
    account_to_delete = None
    for acc in accounts:
        if acc["name"] == name:
            account_to_delete = acc
            break

    if not account_to_delete:
        print(f"❌ 找不到账号 '{name}'！")
        return

    # 确认删除
    confirm = input(f"⚠️  确认删除账号 '{name}' 吗？(y/n): ").strip().lower()

    if confirm == 'y':
        # 删除 anyrouter cookie 文件
        if os.path.exists(account_to_delete["storage_file"]):
            os.remove(account_to_delete["storage_file"])
            print(f"✅ 已删除文件 {account_to_delete['storage_file']}")

        # 删除 linux.do 认证 cookie 文件
        auth_storage_file = account_to_delete.get("auth_storage_file")
        if auth_storage_file and os.path.exists(auth_storage_file):
            os.remove(auth_storage_file)
            print(f"✅ 已删除文件 {auth_storage_file}")

        # 从配置中移除
        accounts.remove(account_to_delete)
        save_accounts(accounts)
        print(f"✅ 账号 '{name}' 已删除！")
    else:
        print("❌ 取消删除操作")


def maintain_account():
    """维护账号（更新cookie）"""
    accounts = load_accounts()

    if not accounts:
        print("❌ 当前没有任何账号！")
        return

    print("\n--- 维护账号（更新cookie）---")
    list_accounts()

    name = input("\n请输入要维护的账号名称: ").strip()

    # 查找账号
    account_to_maintain = None
    for acc in accounts:
        if acc["name"] == name:
            account_to_maintain = acc
            break

    if not account_to_maintain:
        print(f"❌ 找不到账号 '{name}'！")
        return

    storage_file = account_to_maintain["storage_file"]
    auth_storage_file = account_to_maintain.get("auth_storage_file", f"auth_{storage_file}")

    # 使用浏览器重新登录
    with sync_playwright() as pw:
        browser = get_browser(pw)

        # 步骤1: 先更新 linux.do 认证账号
        print(f"\n📝 步骤1: 更新 linux.do 认证账号")
        print(f"⚠️  浏览器将打开 {AUTH_URL}")
        print("请在浏览器中重新登录 linux.do...")

        ctx = browser.new_context(ignore_https_errors=True)
        page = ctx.new_page()
        page.goto(AUTH_URL)

        print("登录完成后，请回车继续...")
        input()

        # 更新 linux.do 的 cookie
        ctx.storage_state(path=auth_storage_file)
        print(f"✅ linux.do 认证账号 cookie 已更新到 {auth_storage_file}")

        # 步骤2: 使用已登录的 linux.do context 重新登录 anyrouter
        print(f"\n📝 步骤2: 重新登录 anyrouter")
        print(f"⚠️  浏览器将打开 {LOGIN_URL}")
        print(f"请点击 'linux.do' 登录按钮，会自动使用刚才登录的账号认证...")

        page.goto(LOGIN_URL)

        print("登录并授权完成后，请回车继续...")
        input()

        # 更新 anyrouter 的 cookie
        ctx.storage_state(path=storage_file)
        print(f"✅ [{name}] anyrouter cookie 已更新到 {storage_file}")

        ctx.close()
        browser.close()

    # 更新配置（确保有 auth_storage_file）
    account_to_maintain["auth_storage_file"] = auth_storage_file
    save_accounts(accounts)
    print(f"✅ 账号 '{name}' 维护完成！")


def list_accounts():
    """查看账号列表"""
    accounts = load_accounts()

    if not accounts:
        print("❌ 当前没有任何账号！")
        return

    print("\n--- 账号列表 ---")
    for i, acc in enumerate(accounts, 1):
        status = "✅ 已保存cookie" if os.path.exists(acc["storage_file"]) else "⚠️  未登录"
        print(f"{i}. {acc['name']} - {status}")


def main():
    """主函数"""
    while True:
        show_menu()
        choice = input("\n请选择操作 (0-5): ").strip()

        if choice == "1":
            login_all_accounts()
        elif choice == "2":
            add_account()
        elif choice == "3":
            delete_account()
        elif choice == "4":
            maintain_account()
        elif choice == "5":
            list_accounts()
        elif choice == "0":
            print("👋 感谢使用，再见！")
            break
        else:
            print("❌ 无效的选择，请重新输入！")


if __name__ == "__main__":
    main()
