# 🎯 Hermes Agent 技能集

本仓库收录了我为 [Hermes Agent](https://hermes-agent.nousresearch.com) 编写的技能（Skills）。技能是 Hermes Agent 的可复用程序性记忆——遇到匹配场景时自动加载，指导 Agent 完成任务。

## 📦 技能列表

| 技能 | 分类 | 作用 | 依赖 |
|------|------|------|------|
| [mimo-tts-setup](mimo-tts-setup/) | 语音合成 | 在 Hermes Agent 中接入小米 MiMo TTS 语音合成，含插件安装、配置修复、ffmpeg 依赖处理 | 🔑 MiMo API Key |
| [china-setup](china-setup/) | 网络配置 | 大陆网络环境下配置 Hermes 的完整方案：代理、镜像、搜索替代、工具安装 | 无（按需自备代理） |
| [pptx-generator](pptx-generator/) | PPT 生成 | 用 PptxGenJS / python-pptx 生成高颜值中英文演示文稿，支持页面切换动画 | 无（本地运行） |

---

## 🗣️ mimo-tts-setup — 小米语音合成接入

**触发词**：朗读 / 语音合成 / 文字转语音 / TTS朗读 / 语音播放

在 Hermes Agent 中接入小米 MiMo TTS 的完整指南：

- **插件安装**：`Stark-X/hermes-mimo-tts`（MIT 协议）
- **5 步配置流程**：插件下载 → API Key 配置 → config.yaml → 路径修复 → ffmpeg
- **8 种中英文音色**：冰糖 / 茉莉 / 苏打 / 白桦 / Mia / Chloe / Milo / Dean
- **3 种模型**：预设音色 / 文字描述生成音色（VoiceDesign）/ 音频样本克隆（VoiceClone）
- **故障排查流程图**：6 种常见报错 → 检查 → 修复路径

> ⚠️ 仅适用于 Hermes Agent 用户。MiMo TTS 使用 chat completions 协议（非标准 `/v1/audio/speech`），需专用插件支持。

## 🌐 china-setup — 大陆网络环境配置

**触发词**：网络配置 / 代理设置 / 镜像源 / 装工具失败

大陆网络环境下使用 Hermes Agent 的完整实操方案：

- **Clash Verge 代理**：7897 端口配置、PowerShell `-Proxy` 参数
- **镜像源**：npmmirror / 阿里云 PyPI / GitHub 加速
- **搜索替代**：AnySearch + 必应国内版（无代理可用）
- **工具安装**：cua-driver、ffmpeg 等受限网络环境的安装替代方案
- **邮件 IMAP**：126 / 163 / QQ 邮箱配置

> 含 11 篇参考资料 + 代理测试脚本，全部为大陆网络实测经验。

## 📊 pptx-generator — 多主题 PPT 生成

**触发词**：做PPT / 生成演示文稿 / 幻灯片 / 汇报课件

用 PptxGenJS / python-pptx 生成精美演示文稿的完整工作流：

- **多主题支持**：深空科技风 / 商务蓝金风 / 极简灰白风 / 高级暗紫渐变风
- **5 种页面积木**：封面 / 数据页 / 卡片网格 / 时间线 / 结尾
- **切换动画**：推入 / 擦除 / 溶解 / 缩放（XML 注入）
- **视觉 QA**：PowerPoint COM 导出图片 + 视觉模型自检修复
- **中英文预设**：字体、排版、文化习惯自动适配

---

## 🛠️ 安装方式

### 方式一：直接下载

```bash
git clone https://github.com/senxppp/skill.git
# 将需要的技能目录复制到 $HERMES_HOME/skills/ 下
```

### 方式二：hermes skills install（支持 URL）

```bash
hermes skills install https://raw.githubusercontent.com/senxppp/skill/main/mimo-tts-setup/SKILL.md
```

### 方式三：手动安装

下载 ZIP → 解压 → 将技能目录放入 `$HERMES_HOME/skills/<技能名>/` → `/reload-skills` 生效

---

## 📝 许可

- mimo-tts-setup：基于 [Stark-X/hermes-mimo-tts](https://github.com/Stark-X/hermes-mimo-tts)（MIT）整理
- china-setup / pptx-generator：原创，MIT

如有问题欢迎提 [Issue](https://github.com/senxppp/skill/issues)！
