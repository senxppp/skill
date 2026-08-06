# AnySearch 安装 + 注册实操（2026-08-04 实测）

AnySearch = 专为 AI Agent 设计的实时搜索引擎（GitHub `anysearch-ai/anysearch-skill`，Apache 2.0）。
国内直连无需代理，免验证码邮箱一键注册。已在本机安装并注册（用户 Outlook 邮箱 xpppjacky@outlook.com）。

## 安装（GitHub 直连即可，无需代理）

```powershell
# 下载最新 release（v3.0.1 实测可用）
Invoke-WebRequest -Uri "https://github.com/anysearch-ai/anysearch-skill/archive/refs/tags/v3.0.1.zip" -OutFile "$env:TEMP\anysearch-skill.zip" -UseBasicParsing
Expand-Archive "$env:TEMP\anysearch-skill.zip" "$env:TEMP\anysearch_x" -Force

# 安装到 Hermes skills 目录，目录名必须是 anysearch（官方包结构，SKILL.md 在根）
$src = Get-ChildItem "$env:TEMP\anysearch_x" -Directory | Select-Object -First 1
Copy-Item $src.FullName "D:\Hermes Agent CN Desktop\data\hermes-home\skills\anysearch" -Recurse -Force
```

⚠️ 不要改目录名或把 SKILL.md 单独抽成 `<name>.md`——该技能带 scripts/ 多运行时 CLI，必须整目录保留。

## 运行时探测 + 固化（runtime.conf）

官方流程：`doc` 命令探测各运行时 → 把推荐运行时写入 `<skill_dir>/runtime.conf`（**不是** SKILL.md）。

```powershell
$dst = "D:\Hermes Agent CN Desktop\data\hermes-home\skills\anysearch"
python "$dst\scripts\anysearch_cli.py" doc   # 验证 Python CLI 可用
# 固化运行时（覆盖写，别追加）：
"Runtime: Python" | Set-Content "$dst\runtime.conf" -Encoding ascii
"Command: python $dst\scripts\anysearch_cli.py" | Add-Content "$dst\runtime.conf" -Encoding ascii
```

## 注册 API key（免验证码，一次调用完成）

```powershell
$body = @{email="user@example.com"} | ConvertTo-Json
Invoke-RestMethod -Uri "https://api.anysearch.com/v1/auth/email/register" -Method Post `
  -Headers @{"Content-Type"="application/json"} -Body $body
```

- 响应 `code: 0` → `data.api_key.key`（形如 `as_sk_...`）是**一次性明文 key，只显示一次**
- **随机密码会发到注册邮箱**——必须告知用户：① 查收邮箱（可能进垃圾邮件，需标记"非垃圾"）② 登录地址 `https://www.anysearch.com/login` ③ 用户名 = 邮箱
- 错误处理：`email_already_registered` → 去登录页，勿重试；`Rate limited` → 读 message 里的秒数等待
- 注册与匿名互斥，选定一条路别中途切换

## 配置 key + 验证

```powershell
"ANYSEARCH_API_KEY=as_sk_xxxxxxxx" | Set-Content "$dst\.env" -Encoding ascii
python "$dst\scripts\anysearch_cli.py" search "hello world" --max_results 1
```

成功返回结构化 JSON（标题+URL+摘要）即连接正常。key 优先级：`--api_key` 参数 > `.env` > 环境变量 > 匿名。

## 日常调用

```powershell
python ...\anysearch_cli.py search "关键词" --max_results 5
python ...\anysearch_cli.py batch_search --queries '[{"query":"q1","max_results":5},{"query":"q2","max_results":5}]'
python ...\anysearch_cli.py extract "https://example.com/page"   # 整页转 Markdown，只收 URL 参数
```

子命令参数不确定时跑 `<command> <subcommand> --help`，别跑完整 `doc`。

## 实测数据点

- 匿名搜索"Bambu Lab 3D打印机"：1.3s / 3 条
- 带 key 搜索"明日方舟终末地"：2.1s / 5 条，中文内容质量好
- 注册返回 rate_limit: 20（匿名限流更低）
- GitHub raw 直连成功（raw.githubusercontent.com 不受 API 限流影响）；GitHub API（api.github.com）未认证会被限流，改用 raw 或网页抓取
