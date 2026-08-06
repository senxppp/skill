# 小米 MiMo TTS 接入 Hermes 详细指南

## API 格式（重要！非标准）

MiMo TTS **不走** OpenAI 标准 `/v1/audio/speech`，而是走 **chat completions**：

```
POST https://api.xiaomimimo.com/v1/chat/completions
```

### 请求格式
```json
{
    "model": "mimo-v2.5-tts",
    "messages": [
        {"role": "user", "content": "用温柔活泼的语气"},
        {"role": "assistant", "content": "要合成的文本"}
    ],
    "audio": {
        "format": "wav",
        "voice": "冰糖"
    }
}
```

- `role: assistant` = 要合成的文本（必填）
- `role: user` = 风格指令（可选，voicedesign 时为必填的音色描述）。可用自然语言控制语速/语气/情感，如 `"语速稍快，节奏轻快"`、`"温柔缓慢，像在哄小朋友"`、`"成熟稳重，新闻主播风格"`。改 style 后无需重启，插件每次调用重新读取配置。
- `audio.format` = `wav` 或 `pcm16`（流式用 pcm16）
- `audio.voice` = 预置音色 ID 或 base64 音频数据 URL（voiceclone 时）

### 响应格式
```json
{
    "choices": [{
        "message": {
            "audio": {
                "data": "base64-encoded-wav-bytes..."
            }
        }
    }]
}
```

### 认证
- `Authorization: Bearer <key>` 或 `api-key: <key>` 请求头
- 环境变量：`MIMO_API_KEY`（hermes-mimo-tts 插件用这个名字）

## 可用模型

| Model ID | 功能 | 音色来源 |
|---|---|---|
| `mimo-v2.5-tts` | 预置音色合成 | 9 个预置音色 |
| `mimo-v2.5-tts-voicedesign` | 文字描述生成音色 | `user` message 中的描述 |
| `mimo-v2.5-tts-voiceclone` | 音频样本克隆 | base64 音频 data URL |

## 预置音色

**中文（5 个）：** `mimo_default` / `冰糖` / `茉莉` / `苏打` / `白桦`
**英文（4 个）：** `Mia` / `Chloe` / `Milo` / `Dean`

## 端点选择

| 端点 | 用途 |
|---|---|
| `https://api.xiaomimimo.com/v1` | **国内推荐** |
| `https://token-plan-cn.xiaomimimo.com/v1` | 国内（按量） |
| `https://token-plan-sgp.xiaomimimo.com/v1` | 新加坡（hermes-mimo-tts 插件默认值，也能用） |

## hermes-mimo-tts 插件安装

### 方式一：hermes plugins install（需 git 在 PATH）
```
hermes plugins install Stark-X/hermes-mimo-tts --enable
```

### 方式二：手动下载（Windows 无 git）
```python
import urllib.request, zipfile, io, os

proxy = 'http://127.0.0.1:7897'
handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
opener = urllib.request.build_opener(handler)

# 注意：默认分支是 master，不是 main
url = 'https://github.com/Stark-X/hermes-mimo-tts/archive/refs/heads/master.zip'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = opener.open(req, timeout=30)
data = resp.read()

hermes_home = r'<hermes_home_path>'
plugins_dir = os.path.join(hermes_home, 'plugins', 'mimo-tts')
os.makedirs(plugins_dir, exist_ok=True)

prefix = 'hermes-mimo-tts-master/'
with zipfile.ZipFile(io.BytesIO(data)) as zf:
    for info in zf.infolist():
        if info.filename.startswith(prefix):
            rel = info.filename[len(prefix):]
            if not rel: continue
            target = os.path.join(plugins_dir, rel)
            if info.is_dir():
                os.makedirs(target, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, 'wb') as f:
                    f.write(zf.read(info.filename))
```

### 配置步骤
1. `.env` 添加 `MIMO_API_KEY=<your_key>`（与 XIAOMI_API_KEY 同值）
2. `hermes config set tts.provider mimo`
3. `hermes config set tts.mimo.voice 冰糖`
4. `hermes config set tts.mimo.base_url https://api.xiaomimimo.com/v1`
5. `hermes config set tts.mimo.model mimo-v2.5-tts`
6. `hermes plugins enable mimo-tts`
7. `/reset` 新会话生效

### 验证
```python
from openai import OpenAI
import base64, os

client = OpenAI(api_key=os.environ['MIMO_API_KEY'], base_url="https://api.xiaomimimo.com/v1")
completion = client.chat.completions.create(
    model="mimo-v2.5-tts",
    messages=[
        {"role": "user", "content": "用温柔活泼的语气"},
        {"role": "assistant", "content": "你好！测试一下MiMo语音合成。"}
    ],
    audio={"format": "wav", "voice": "冰糖"},
)
wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
# wav_bytes 就是 WAV 音频
```

## ASR（语音识别）

`mimo-v2.5-asr` 也走 `/v1/chat/completions`，音频通过 `input_audio` content block 传入。
价格 ¥0.5/小时，支持粤语/吴语/闽南语/四川话方言。

## 定价（2026-08 查证）

| 模型 | 价格 | 备注 |
|---|---|---|
| TTS 系列（3 个） | **免费** | 限时 |
| ASR | ¥0.5/小时 | — |

## 实际调试路径（2026-08-06 实测）

接入过程中踩的 7 个坑，按顺序：

1. **API 协议不兼容**：标准 `/v1/audio/speech` 返回 404，确认走 chat completions
2. **插件安装**：下载 zip → 解压到 `plugins/mimo-tts/` → `hermes plugins enable`
3. **API Key**：`MIMO_API_KEY` 独立于 `XIAOMI_API_KEY`，改 .env 后必须重启桌面版
4. **base_url 节点**：插件默认 token-plan-sgp（新加坡），按量付费用 `api.xiaomimimo.com`
5. **插件读错配置路径**（核心 bug）：硬编码 `~/.hermes/config.yaml`，不读 `$HERMES_HOME`，必须在 `C:\Users\<user>\.hermes\config.yaml` 也写一份
6. **ffmpeg 缺失**：默认输出 MP3 需转码，`pip install imageio-ffmpeg` + 复制 binary 到 PATH
7. **中文乱码**：`hermes config set` 写中文会真乱码（文件里也乱），必须直接编辑 YAML

## 替代方案

`yshtcn/xiaomiTTS2OpenAITTSAPI`（22⭐）— 独立代理服务，把 MiMo TTS 包装成 OpenAI 标准 `/v1/audio/speech`。
有 Web UI + Docker 支持，适合需要标准接口的场景。

## 相关链接

- 官方文档：https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/audio/speech-synthesis-v2.5
- 控制台：https://platform.xiaomimimo.com
- 插件源码：https://github.com/Stark-X/hermes-mimo-tts
- 代理服务：https://github.com/yshtcn/xiaomiTTS2OpenAITTSAPI
- Hermes 讨论：#19605, #43700, #46257
