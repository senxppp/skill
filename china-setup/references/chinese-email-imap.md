# Chinese Email Providers: IMAP Access Pitfalls

## 126 / 163 Mail

### Server settings

| Setting | Value |
|---------|-------|
| IMAP server | `imap.126.com` or `imap.163.com` |
| Port | `993` (SSL) |
| Login | Full email address (e.g. `user@126.com`) |
| Password | **Authorization code** (授权码), NOT the account password |

### Auth code setup

用户不能在登录框里直接输入邮箱密码。需要：

1. 登录网页版 mail.126.com（或 mail.163.com）
2. 设置 → POP3/SMTP/IMAP → 开启 IMAP 服务
3. 系统会生成一个 **16位授权码**（例如 `QVbWxp56vvKLJQBc`）
4. 把这个授权码当密码用

### "Unsafe Login" 错误（关键坑）

**症状：** 登录（LOGIN）成功，但 `SELECT INBOX` 失败，返回：
```
SELECT Unsafe Login. Please contact kefu@188.com for help
```

**原因：** 126/163 服务器端安全策略拦截了连接，认定 IP 或客户端环境"不安全"。换授权码无效。

**可能需要的操作（用户端）：**

1. 登录 mail.126.com → **设置 → 账户安全**
   - 关闭"异地登录保护"
   - 关闭"客户端登录限制"
   - 或添加当前 IP 到白名单

2. 查看通知（页面右上角铃铛图标）：
   - 可能有一条"新的客户端登录请求"的通知，需要点"确认是我"

3. 联系客服（kefu@188.com）申请解除限制

### Python imaplib 连接模板

```python
import imaplib, ssl
from email.header import decode_header

ctx = ssl.create_default_context()
mail = imaplib.IMAP4_SSL("imap.126.com", 993, ssl_context=ctx)
mail.login("user@126.com", "AUTH_CODE_HERE")

# 列出所有文件夹
status, folders = mail.list()
for f in folders:
    print(f.decode("gbk", errors="replace"))

# 注意：INBOX 可能被安全策略拦截
status, data = mail.select("INBOX")
if status != "OK":
    print(f"FAILED: {data}")  # 可能是 Unsafe Login
```

### 注意事项

- 126 和 163 的 IMAP 文件夹名使用 **IMAP UTF-7** 编码（非直接中文），Python imaplib 默认使用 ASCII encoding，读取 GBK 编码的文件夹名时需要用 `decode("gbk")`
- 不要用 inline `python -c "..."` 方式在 PowerShell 中运行 imaplib 代码——引号嵌套和转义极易出错。**始终写 .py 文件然后用 `python script.py` 执行**
- 如果 IMAP 始终被拦截，可以试试 POP3 协议（pop3.126.com, port 995 SSL），但 POP3 功能比 IMAP 少很多

## QQ Mail

（TODO — 尚未测试，但已知 IMAP 设置更顺畅，很少遇到 Unsafe Login 拦截）

## Outlook / Hotmail

Outlook 的 IMAP 连接通常没有 126/163 这种安全限制，可以直接用 Microsoft 账号 + 应用专用密码连接：

| Setting | Value |
|---------|-------|
| IMAP server | `outlook.office365.com` |
| Port | `993` (SSL) |
| Login | Full email address |
| Password | Microsoft account password or app password |
