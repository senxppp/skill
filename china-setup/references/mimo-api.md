# 小米 MiMo API 调研笔记（2026-08 查证）

用户听说"小米 MIMO 很省钱"主动问过。所有价格/活动数字都是**易变事实**，回答前以官网实时查证为准（用户强烈反感编造数字）。

## 关键认知（最重要的一条）

**MiMo Claw 免费体验（单次 4h/天）是小米云端的网页版 Agent 产品，不是 API——接不进 Hermes。**
- Claw = 云端托管智能体（类似网页版 Agent 平台），搭载 mimo-v2.5-pro，只能在小程序/网页里用
- 它不提供 API Key，Hermes 无法调用。用户常误以为"官网送的免费 4 小时"能让 Hermes 白嫖，必须澄清
- 比喻：Claw 是麦当劳送的就餐券，不能拿回家做饭

## 官网与平台

| 项目 | 地址 |
|------|------|
| 官网/文档 | https://mimo.mi.com |
| API 开放平台（控制台/申请 key） | https://platform.xiaomimimo.com |
| OpenAI 兼容 base URL | `https://api.xiaomimimo.com/v1`（/v1/chat/completions，OpenAI 格式） |
| 定价页 | https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go |
| Token Plan 订阅页 | https://mimo.mi.com/docs/zh-CN/tokenplan/Token%20Plan/subscription |
| 活动/体验金 FAQ | https://mimo.mi.com/docs/zh-CN/quick-start/faq/promotions |

## API Key 两种（互不通用）

- `sk-xxxxx`：按量付费，控制台「API Keys」页申请，按实际 token 消耗扣余额
- `tp-xxxxx`：Token Plan 订阅专属，购买后在「plan-manage」页查看，仅创建时可见可复制
- 官方文档明确列出**支持 Hermes Agent** 接入（还有 Claude Code、OpenClaw、OpenCode、Cline 等）

## 免费额度/体验金（2026-08 查证）

- 新用户注册送 **¥10 体验金**（新浪/IT之家 2026-01 报道，有用户领到 ¥20）
- 邀请有礼：注册 3 天内新用户互绑邀请码，双方各得 ¥10，即时到账；好友首单实付再得 10%
- 体验金仅抵扣 API 调用费，**40 天有效**，过期失效
- 百万亿 Token 激励计划（100T 免费发放）已结束（2026-04-28 ~ 05-28，申请制）
- 国内充值需个人实名认证

## 模型定价（国内，元/百万 tokens，2026-07 官网）

| 模型 | 输入(命中缓存) | 输入(未命中) | 输出 |
|------|------|------|------|
| mimo-v2.5-pro | ¥0.025 | ¥3.00 | ¥6.00 |
| mimo-v2.5 | ¥0.02 | ¥1.00 | ¥2.00 |

- 对比 DeepSeek v4-flash（输入 ¥1 / 输出 ¥2）：mimo-v2.5 价格持平，v2.5 是全模态（文本/图像/视频/音频）
- mimo-v2.5-pro 在 GDPVal-AA / ClawEval 开源模型第一；v2.5 系列 MIT 协议全量开源
- ASR：¥0.5/小时；TTS 系列限时免费
- **TTS 接入 Hermes 的完整指南**见 `references/mimo-tts-integration.md`（插件安装、API 格式、音色列表、配置步骤）

## 接入 Hermes 的步骤（若用户注册后）

1. platform.xiaomimimo.com 注册（小米账号/手机号）→ 控制台申请 `sk-` key
2. `hermes config set model.provider <...>` / model 段改 base_url + api_key（config.yaml 受保护，必须用 hermes config set）
3. 验证：跑一个对话测试
4. ⚠️ 改 providers 有弄坏现有 deepseek 配置的风险，先备份/先问用户
