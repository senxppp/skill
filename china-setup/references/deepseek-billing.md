# DeepSeek API Billing & Balance Checks（2026-08 查证更新）

> ⚠️ 价格/时段是**易变事实**，回答用户前必须联网查证（AnySearch 搜「DeepSeek API 定价」或直接看官方 https://api-docs.deepseek.com/zh-cn/quick_start/pricing/），禁止凭记忆报数字。以下为 2026-08-05 查证结果。

## 峰谷定价（当前机制：高峰翻倍，不是夜间打折）

| 时段 | 价格 |
|------|------|
| 高峰：每天 9:00-12:00、14:00-18:00（共 7h） | 平时价的 **2 倍**（所有计费项统一翻倍） |
| 其余时段（晚上/凌晨/周末） | 平价，不加价 |

- 官方原话："DeepSeek API 服务即将采用峰谷定价策略，高峰时段价格为平时价格 2 倍"
- 历史坑：2025-02 曾有 V3/R1 时代的夜间错峰优惠（00:30-08:30，V3 半价/R1 25 折）——**已过时**，别拿旧政策当现在的答案
- 腾讯云代理的 DeepSeek API 另有自己的 00:30-08:30 半价时段（那是腾讯云的优惠，不是 DeepSeek 官方）——注意区分

## 官方价目（平时价，元/百万 tokens）

| 模型 | 输入(缓存命中) | 输入(缓存未命中) | 输出 |
|------|------|------|------|
| deepseek-v4-flash | 0.02 | 1 | 2 |
| deepseek-v4-pro | 0.025 | 3 | 6 |

- 缓存命中输入成本极低（几分钱/百万 token），是控成本核心抓手
- 输出 + 缓存未命中输入占总成本 90%+，日间批量执行显著拉高账单

## Quick Balance Query

```python
import requests

# Read the API key from .env
with open("D:/Hermes Agent CN Desktop/data/hermes-home/.env") as f:
    for line in f:
        if line.startswith("DEEPSEEK_API_KEY="):
            key = line.strip().split("=", 1)[1]
            break

r = requests.get(
    "https://api.deepseek.com/user/balance",
    headers={"Authorization": f"Bearer {key}"}
)
print(r.json())
```

**Response format:**
```json
{
  "is_available": true,
  "balance_infos": [
    {
      "currency": "CNY",
      "total_balance": "3.75",
      "granted_balance": "0.00",
      "topped_up_balance": "3.75"
    }
  ]
}
```

| Field | Meaning |
|-------|---------|
| `is_available` | Account active? |
| `total_balance` | Total remaining (CNY) |
| `granted_balance` | Free credits (0 = used up) |
| `topped_up_balance` | User-recharged amount |

## 阿里云百炼免费额度（用户曾用它薅羊毛，2026-08 查证）

- 新用户开通百炼：**每个模型 100 万 tokens**，覆盖 70+ 模型，合计超 7000 万
- 有效期 **90 天**（2025/9/8 后开通用户）；先扣免费额度，用完：未认证用户停用、已认证用户直接扣费（可开「用完即停」）
- 每个模型额度独立，用完不自动切换其他模型
- 官方文档：https://help.aliyun.com/zh/model-studio/new-free-quota

## When to Check

- User asks "还剩多少钱" or "要不要充钱"
- User asks about costs or token consumption
- Primary model keeps failing with 429/402 errors
- 用户问「现在是不是便宜时段」→ 先联网查官方定价页确认当前机制，再对照本地时间（`Get-Date`）判断是否在高峰 9-12/14-18 区间
