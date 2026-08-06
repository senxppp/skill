---
name: mimo-tts-setup
description: "Hermes Agent 专属：接入小米 MiMo TTS 语音合成（含插件安装、配置修复、ffmpeg 依赖处理）。仅适用于 Hermes Agent 用户，非 Hermes 环境无法使用。"
version: 1.2.0
author: xpppj
metadata:
  hermes:
    tags: [语音合成, 小米, 中文语音, 文字转语音, Hermes插件]
---

# 小米 MiMo TTS 接入 Hermes Agent

> ⚠️ **本技能仅适用于 Hermes Agent 用户**。非 Hermes 环境（如纯 Python 项目、其他 Agent 框架）无法使用本技能，但可直接参考 [MiMo TTS 官方文档](https://platform.xiaomimimo.com/docs/zh-CN/usage-guide/speech-synthesis-v2.5) 调用 API。

## Trigger
- 用户说"朗读"、"语音合成"、"文字转语音"、"TTS朗读"、"语音播放"
- `text_to_speech` 工具报错 `No TTS provider available` 或 `MiMo TTS failed`
- 需要配置高质量中文语音合成

## 前置条件
- **Hermes Agent 已安装**（本技能不支持其他框架）
- MiMo API Key（从 platform.xiaomimimo.com 获取）
- Python 环境（openai 包已内置）

## 完整安装流程（5 步）

### Step 1：安装 mimo-tts 插件

插件来源：GitHub `Stark-X/hermes-mimo-tts`

```powershell
$pluginDir = "$env:HERMES_HOME\plugins\mimo-tts"
New-Item -ItemType Directory -Path $pluginDir -Force
Invoke-WebRequest -Uri "https://github.com/Stark-X/hermes-mimo-tts/archive/refs/heads/main.zip" -OutFile "$env:TEMP\mimo-tts.zip"
Expand-Archive "$env:TEMP\mimo-tts.zip" -DestinationPath "$env:TEMP\mimo-tts" -Force
Copy-Item "$env:TEMP\mimo-tts\hermes-mimo-tts-main\*" $pluginDir -Recurse -Force
```

### Step 2：配置 API Key

在 `$HERMES_HOME/.env` 中添加：

```
MIMO_API_KEY=你的MiMo API Key
```

> ⚠️ MiMo TTS 用 chat completions 协议（非标准 `/v1/audio/speech`），Hermes 内置 TTS 工具不支持此格式，必须用插件。

### Step 3：启用插件 + 配置 config.yaml

```powershell
hermes plugins enable mimo-tts
hermes config set tts.provider mimo
```

手动编辑 config.yaml，确保 tts.mimo 段正确：

```yaml
tts:
  provider: mimo
  mimo:
    voice: 冰糖          # 可选：冰糖/茉莉/苏打/白桦/Mia/Chloe/Milo/Dean
    model: mimo-v2.5-tts  # 可选：mimo-v2.5-tts-voicedesign / mimo-v2.5-tts-voiceclone
    base_url: https://api.xiaomimimo.com/v1  # 按量付费用这个
    timeout: 60
```

### Step 4：修复插件配置路径（关键坑！）

插件硬编码读 `~/.hermes/config.yaml`，但 Hermes Desktop 的 HERMES_HOME 可能在别处。

**必须在 `~/.hermes/config.yaml` 创建配置文件**：

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.hermes" -Force
@"
tts:
  mimo:
    base_url: https://api.xiaomimimo.com/v1
    voice: 冰糖
    model: mimo-v2.5-tts
    timeout: 60
"@ | Out-File -FilePath "$env:USERPROFILE\.hermes\config.yaml" -Encoding UTF8
```

### Step 5：安装 ffmpeg（依赖项）

插件默认输出 MP3 格式，需要 ffmpeg 做 WAV→MP3 转换。

```powershell
# 方法 1：winget（较慢）
winget install Gyan.FFmpeg

# 方法 2：pip 安装静态构建（快速）
pip install imageio-ffmpeg
python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
Copy-Item "<上一步输出的路径>" "$env:USERPROFILE\AppData\Local\Programs\Python\Python312\ffmpeg.exe"
```

## 故障排查流程图

遇到报错时，按以下路径逐步排查：

### 错误：`No TTS provider available`
→ 检查 `hermes plugins list` 是否显示 mimo-tts 为 enabled
→ 未启用？执行 `hermes plugins enable mimo-tts`
→ 已启用？检查 `pip show openai` 是否安装

### 错误：`MiMo TTS failed: 401 Invalid API Key`
→ 检查 `.env` 中 `MIMO_API_KEY` 是否正确
→ Key 正确？确认是否用错节点：按量付费用 `api.xiaomimimo.com`，Token Plan 用 `token-plan-sgp.xiaomimimo.com`
→ 节点正确？重启桌面版（.env 缓存问题）

### 错误：`WinError 2 系统找不到指定的文件`
→ 缺 ffmpeg。执行 `where.exe ffmpeg` 确认
→ 未安装？按 Step 5 安装

### 错误：`MiMo TTS failed: 404 Not Found`
→ base_url 错误。确认 config 中是 `https://api.xiaomimimo.com/v1`（不是 token-plan-sgp）

### 错误：生成了音频但没声音 / 乱码
→ 检查 `~/.hermes/config.yaml` 中 voice 字段是否为正常中文（不是乱码）
→ 乱码？手动编辑文件，不要用 `hermes config set`（PowerShell 编码问题）

### 错误：改了配置不生效
→ 重启 Hermes 桌面版。`/reload` 在桌面版中效果有限

## Pitfalls

1. **base_url 节点选择**：按量付费用 `api.xiaomimimo.com`，Token Plan 用 `token-plan-sgp.xiaomimimo.com`，搞混会 401/404。

2. **插件读错配置路径**：插件硬编码 `Path.home() / ".hermes" / "config.yaml"`，不读 `$HERMES_HOME`。

3. **hermes config set 中文乱码**：PowerShell 5.1 处理 UTF-8 中文有问题，直接编辑文件更可靠。

4. **ffmpeg 未安装**：`WinError 2` = 缺 ffmpeg。

5. **.env 改了不生效**：必须重启桌面版。

6. **协议非标准**：走 `/v1/chat/completions` + `audio` 参数，不是 `/v1/audio/speech`。

## 可用音色

| 音色 | 语言 | 性别 |
|------|------|------|
| 冰糖 | 中文 | 女声 |
| 茉莉 | 中文 | 女声 |
| 苏打 | 中文 | 男声 |
| 白桦 | 中文 | 男声 |
| Mia | 英文 | 女声 |
| Chloe | 英文 | 女声 |
| Milo | 英文 | 男声 |
| Dean | 英文 | 男声 |

## 验证方式

```powershell
# 重启 Hermes 后，调用 text_to_speech 工具
text_to_speech("你好，测试朗读功能")
```

**判定结果：**

| 返回 | 含义 |
|------|------|
| `success: true` + `file_path: ...mp3` | ✅ 成功，音频已生成 |
| `success: false` + `401 Invalid API Key` | ❌ Key 错误或节点错误，见故障排查 |
| `success: false` + `WinError 2` | ❌ 缺 ffmpeg，见 Step 5 |
| `success: false` + `No TTS provider` | ❌ 插件未启用或 openai 未安装 |
| `success: false` + `404 Not Found` | ❌ base_url 错误 |

成功后可在聊天中直接播放返回的 mp3 文件，或用 `read_file` 查看路径手动打开。

## 支持的模型

| 模型 | 用途 | voice 参数 |
|------|------|-----------|
| mimo-v2.5-tts | 预设音色（默认） | 音色名，如"冰糖" |
| mimo-v2.5-tts-voicedesign | 文字描述生成音色 | 无需传，用 style 字段描述音色特征 |
| mimo-v2.5-tts-voiceclone | 音频样本克隆 | base64 编码的音频数据 URL |
