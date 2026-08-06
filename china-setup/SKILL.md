---
name: china-setup
slug: china-setup
displayName: 大陆环境配置指南
category: 效率工具
description: "Configure Hermes Agent and its dependencies in a mainland-China network environment. Covers Clash Verge proxy setup, npm/PyPI mirrors, cua-driver installation behind GFW, web-search alternatives without proxy (AnySearch + Bing CN), DashScope vision API integration, email IMAP config, WeType IME restart, hermes CLI launch path on Windows, and delegation fallback patterns. When any tool/API fails silently or times out from China, load this skill."
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [china, proxy, mirror, cua-driver, dashscope, email, windows, hermes-cli]
    related_skills: [computer-use, anysearch, xiaping, windows-powershell-http]
---

# 中国大陆网络环境下 Hermes Agent 配置与实操指南

## Overview

本文档汇总在中国大陆使用 Hermes Agent 的全部实战经验：代理配置、镜像源、桌面控制、视觉 API、邮箱、CLI 启动、SkillHub 商店等。所有方案均经实测验证。

## Linked References

- `references/skillhub-cli.md` — SkillHub 商店 CLI 在 Windows 上的手动安装流程、技能发布（slug 字段必需、token 格式 skh_）、与虾评对比
- `references/deepseek-billing.md` — DeepSeek API 峰谷定价（高峰 9-12/14-18 为 2 倍）、官方价目、余额查询、百炼免费额度。**价格/时段是易变事实，回答前必须联网查证，禁止凭记忆编造**
- `references/mimo-api.md` — 小米 MiMo API 调研笔记：**MiMo Claw 免费 4h/天是网页版云端 Agent 不是 API，接不进 Hermes**；平台/API Key 两种（sk- 按量 / tp- 订阅）、新用户 ¥10 体验金、模型定价对比表。用户问"小米 MIMO 省钱/接 MiMo"时先读这篇再答复

## 易变事实必须联网查证（用户强要求）

用户明确要求：**价格、时段、政策、版本号等易变信息，回答前先联网查证**（AnySearch 搜官方文档/新闻），严禁凭记忆编造数字（"不要给我在这编编编"）。参考 deepseek-billing.md 的查证示范。判断"现在几点/是否优惠时段"时：

1. 本地时间 `Get-Date` + 联网交叉验证（至少 2 个独立来源）
2. **timeapi.io 实测不可信**（2026-08 实测比真实时间慢 20 分钟）——用百度响应头 `urllib.request.urlopen("https://www.baidu.com").headers.get("Date")`（GMT，+8 得北京时间）或 worldtimeapi.org 交叉验证
3. 来源冲突时以多数一致 + 国内直连源（百度）为准

## 核心原理

国内环境的两大障碍：
1. **GFW 封锁**：GitHub、npmjs.org、huggingface.co、OpenAI/Claude API 等无法直连
2. **PowerShell 5.1 限制**：& 操作符会吃掉 JSON 引号，环境变量 `$env:` 行为特殊，管道传二进制数据困难

解决方案 = **本地代理 + 国内镜像 + Python 替代脚本**。

## 一、代理配置（翻墙）

### Clash Verge Rev v2.5.2

| 项目 | 值 |
|------|-----|
| 安装路径 | `D:\Clash Verge\clash-verge.exe` |
| 模式 | 服务模式（非用户模式） |
| 端口 | HTTP 7897（GUI 启动后才通） |
| 系统代理 | 必须开启「系统代理」开关，否则工具走不到代理 |

### 授权规则
用户可以自主决定何时启用节点（下载、访问国外网站、API 调用等）。选择标准：低延迟 ≠ 好用，优先选实际稳定节点。任务完成后如无必要可自行关闭代理。

### 代理使用注意
```powershell
# ❌ 错误：HTTPS_PROXY 环境变量对 Invoke-RestMethod / Invoke-WebRequest 无效
$env:HTTPS_PROXY = 'http://127.0.0.1:7897'
Invoke-RestMethod 'https://api.example.com'  # 不走代理！

# ✅ 正确：必须显式指定 -Proxy 参数
Invoke-RestMethod -Uri 'https://api.example.com' -Proxy 'http://127.0.0.1:7897'

# ✅ Python 自动读系统代理（需 pip install requests）
import requests; requests.get('https://api.example.com')  # 走代理
```

## 二、镜像源配置

### npm 镜像（npmmirror.com）
用于 playwright-core、pptxgenjs 等 npm 包。配置后：
```bash
npm config set registry https://registry.npmmirror.com
```
⚠️ **仅适用于 npm 包，不适用于 cua-driver**（cua-driver 从 GitHub releases 下载）。

### PyPI 镜像
```bash
pip install -i https://mirrors.aliyun.com/pypi/simple/ <package>
```
常用替换包：beautifulsoup4、requests 等。

## 三、桌面控制（cua-driver）

### 安装
```bash
hermes computer-use install
# 从 GitHub releases 下载 → 安装到 %LOCALAPPDATA%\Programs\Cua\cua-driver\bin
```

### MCP 服务器配置
```yaml
mcp_servers:
  cua-driver:
    command: "C:\\Users\\<username>\\AppData\\Local\\Programs\\Cua\\cua-driver\\bin\\cua-driver.exe"
    args: ["mcp"]
```
修改后必须 `/reload-mcp` 或重启 gateway。简单 `/reset` 不重载 MCP 服务器。

### 最佳实践
1. **capture 永远先行**：先 `action='capture', mode='som'`，再按 element index 点击
2. **element_index > 像素坐标**：更可靠，支持后台/最小化窗口
3. **background-first 升级 ladder**：
   - `effect: 'confirmed'` → 完成
   - `effect: 'unverifiable'` → 重新 capture 自己验证
   - `suspected_noop / background_unavailable` → 改用 foreground 或像素坐标
4. **不要预判 foreground**：除非 driver 明确返回 error 信号才升级
5. **不要 raise_window=true**：除非用户明确要求前台显示

### 常见故障排查
- **空 capture / 元素缺失**：运行 `hermes computer-use doctor` 检查健康状态
- **click 没反应**：可能是 Chromium/Electron 应用需要 foreground delivery
- **type_text 文字消失**：某些 Web 输入框只用 keystrokes 不用 ValuePattern
- **MCP 连接失败**：检查 cua-driver 是否 running + 配置文件是否正确

### PowerShell JSON 传参问题
PowerShell 5.1 用 `&` 执行外部命令时，JSON 中的双引号会被当作字符串分隔符吃掉。解决方案：
- 用 Python 脚本代替 inline JSON
- 或用单引号包裹整个 JSON（但含单引号的 JSON 内转义麻烦）

## 四、视觉 API（DashScope Qwen-VL-Plus）

### 为什么用它
Hermes 内置的 `auxiliary.vision` 有 key 解析 bug。**不要用那个！** 直接用 DashScope API。

### API 配置
- 端点：`https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`
- 密钥：`DASHSCOPE_API_KEY`（在 hermes-home/.env 中）

### 识图模型按难易度分流（用户指示 2026-08-05）
- **简单任务**（纯 OCR/读文字/简单描述/识别按钮）→ `qwen-vl-plus`（2.5代，省钱）
- **复杂任务**（深度推理/GUI 操作分析/长文档理解/多步视觉/风格复刻描述）→ `qwen3-vl-plus`（第三代，更强，已实测可用）
- 完整分流表与调用代码见 `dashscope-image-generation` skill「识图模型分流」节

### 生图模型（2026-08 升级）
- **首选 `qwen-image-2.0-pro`**（同步接口，0.5元/张，新用户免费额度100张/90天），**不是**万相的异步端点，用错返回 400
- 兜底 `wanx-v1`（万相异步）。完整调用流程见 `dashscope-image-generation` skill

### Python 调用示例
```python
import base64, requests, json

def analyze_image(image_path, question):
    with open(image_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    
    payload = {
        "model": "qwen-vl-plus",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                {"type": "text", "text": question}
            ]
        }]
    }
    
    headers = {"Authorization": f"Bearer {os.environ['DASHSCOPE_API_KEY']}", "Content-Type": "application/json"}
    resp = requests.post("https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", json=payload, headers=headers)
    return resp.json()['choices'][0]['message']['content']
```

### 用途
- 截图分析（配合 cua-driver 桌面 capture）
- 看图识图（用户发的图片）
- PPT 视觉 QA 自检

## 五、联网搜索

### 主力：AnySearch skill
```bash
python <hermes_home>/skills/anysearch/scripts/anysearch_cli.py search "查询内容" --max_results 5
```
- 匿名可用，注册 key 可提升限流
- 支持垂直领域搜索 + extract 整页提取
- 账号：xpppjacky@outlook.com

### 备用：必应国内版
Edge 打开 cn.bing.com 搜索，搜完关浏览器窗口。

## 六、邮件配置

### 126 邮箱
| 项目 | 值 |
|------|-----|
| 地址 | sen0951@126.com |
| POP3 | pop.126.com:995 |
| 授权码 | 在 126 邮箱设置→客户端授权密码 生成 |
| 清理偏好 | 收据/交易保留、广告删、安全通知可保留 |

### 其他
- 163 邮箱、Outlook 邮箱（xpppjacky@outlook.com）也在使用
- POP3 无回收站，删除不可恢复，先列清单再删

## 七、微信输入法（WeType）

| 项目 | 值 |
|------|-----|
| 版本 | 腾讯 WeType 2.1.1.6 |
| 路径 | C:\Program Files\Tencent\WeType\2.1.1.6 |
| 进程 | wetype_service, wetype_server, wetype_renderer |

### 故障处理
输入框旁出现黑框/UI 异常 → 重启 `wetype_service.exe`（会自动拉起 renderer）。

## 八、Hermes CLI 启动

### ⚠️ 重要：hermes.cmd 指向旧版
```
hermes.cmd → 指向 0.18.2 旧版（不能用来做 config 等管理操作）
```

### 正确方式
```powershell
& "D:\Hermes Agent CN Desktop\data\versions\0.19.0-cn.7\hermes-agent-cn-runtime-win32-x64.exe" config get
```
或者用 Start-Process 避免 & 符号被终端工具误判：
```powershell
Start-Process -Wait -FilePath "..."
```

### 配置修改
config.yaml 受保护，不能直接 patch。必须用：
```powershell
& hermes config set <key> <value>
```

## 九、虾评平台（xiaping.coze.com）

### 触发词
装/卸/发布技能、评测/打分、虾米/打卡、许愿、找技能/技能榜

### 实测差异（官方文档有误）
- 评测限流：**3/h**（不是 5/h，第 4 条起 429）
- 打卡时段：仅 09:00-10:00 / 17:00-19:00（时段外 400）
- 发布技能需 pledge 承诺流程（409 PLEDGE_REQUIRED）

### PowerShell + JSON 坑
curl.exe 传 JSON 时双引号被 PowerShell 吃掉 → 必须用 Python requests 发 multipart：
```python
# pledge 参数必须原样传，不能用 curl
requests.post(url, data={"pledge": {"agreed": True}}, ...)
```

### Zip 打包坑
Python zipfile（相对路径）✅ vs Compress-Archive（绝对路径含反斜杠）❌
平台 Linux 解压时绝对路径会崩。

### 安全检测
analysis_error = 平台 LLM 分析器自己崩了，不是代码问题，不影响安全性。

## 十、delegation 配置

复杂任务通过 delegation 下发给 deepseek-v4-pro 处理。保持这个配置不变。

## 十一、小米 MiMo TTS 接入 Hermes

MiMo TTS 系列（`mimo-v2.5-tts` / `voicedesign` / `voiceclone`）**限时免费**。
API 非标准：走 `/v1/chat/completions` + `audio` 参数，**不是** `/v1/audio/speech`。
详细 API 格式和配置步骤见 `references/mimo-tts-integration.md`。

### 快速安装（hermes-mimo-tts 插件）
```powershell
# 1. 下载插件（无 git 环境用 Python + 代理）
# 2. 解压到 hermes-home/plugins/mimo-tts/
# 3. .env 添加 MIMO_API_KEY=xxx
# 4. hermes config set tts.provider mimo
# 5. hermes config set tts.mimo.voice 冰糖
# 6. hermes config set tts.mimo.base_url https://api.xiaomimimo.com/v1  # 国内用这个！
# 7. hermes plugins enable mimo-tts
# 8. /reset 新会话生效
```

**关键坑：**\n- **🔴 插件读错配置路径**：插件硬编码 `Path.home() / \".hermes\" / \"config.yaml\"`，不读 `$HERMES_HOME`。桌面版必须在 `C:\\Users\\<user>\\.hermes\\config.yaml` 也写一份 tts.mimo 配置，否则插件全用默认值（base_url 打到 token-plan-sgp、voice=Chloe）\n- 插件默认 base_url 是新加坡 `token-plan-sgp`，按量付费用 `api.xiaomimimo.com`\n- **🔴 `hermes config set` 中文会真乱码**：不是终端显示问题，文件里也会写成 `鍐扮硸`。必须用 `[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))` 直接写 UTF-8 文件\n- **🔴 ffmpeg 是必需依赖**：默认输出 MP3 需要转码，没装 ffmpeg → `WinError 2`。安装：`pip install imageio-ffmpeg` + 复制 binary 到 PATH\n- 改 `.env` 后必须**重启桌面版**，`/reload` 对 TTS 插件不一定生效\n- 插件读 `MIMO_API_KEY` 环境变量，config.yaml 里的 `tts.mimo.api_key` 字段会被忽略

## Common Pitfalls

1. **PowerShell 吃引号**：任何 curl/JSON/multipart 操作都换成 Python
2. **Proxy 环境变量无效**：Windows PowerShell 的 HTTPS_PROXY 对 Invoke-RestMethod 无用，必须用 -Proxy 参数
3. **hermes.cmd 是旧版**：管理操作必须用 versions/*/完整路径
4. **config.yaml 不能直接改**：只能用 hermes config set
5. **Chrome/Edge --remote-debugging-port**：已有实例运行时启动可能静默失败，先杀进程
6. **DashScope key 别动 providers 配置**：千问 qwen3.7-plus 在用，改了会影响主模型
7. **虾评 zip 必须相对路径**：Compress-Archive 生成的绝对路径 ZIP 在平台侧 Linux 解压失败
8. **cua-driver 直接 CLI pipe 报错**：必须走 MCP 模式（`cua-driver.exe mcp`）
9. **`hermes config set` 中文真乱码**：不是终端显示问题！文件里也会写成乱码（如 `鍐扮硸` 而非 `冰糖`）。必须用 `[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))` 直接写 UTF-8 文件，或手动编辑 YAML
10. **.env 改了但不生效**：桌面版改 .env 后必须完全退出重启，`/reload` 对插件/TTS 等不一定生效\n11. **社区插件不读 $HERMES_HOME**：部分插件硬编码 `Path.home() / \".hermes\"`，桌面版用户需在 `~/.hermes/config.yaml` 也写一份相关配置

## Verification Checklist

- [ ] 代理已开（Clash Verge 绿色/已连接状态）
- [ ] 7897 端口通（`Test-NetConnection 127.0.0.1 -Port 7897`）
- [ ] npm registry = npmmirror.com（`npm config get registry`）
- [ ] cua-driver installed + MCP server configured
- [ ] DASHSCOPE_API_KEY in .env
- [ ] hermes CLI 用正确路径调用（不是 hermes.cmd）
- [ ] 任何 curl/JSON 相关命令已改为 Python 实现
