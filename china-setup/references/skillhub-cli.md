# SkillHub CLI — Windows 安装与发布工作流

## 概述

SkillHub (https://skillhub.cn) 是国内优先的 Skill 商店，CLI 基于 Python，但安装脚本是 bash，Windows 需手动适配。

## 安装（Windows 手动适配）

官方 install.sh 是 bash 脚本，Windows 上需手动执行等效步骤：

```python
import requests, tarfile, io, os, json, shutil

base = r'C:\Users\<user>\.skillhub'
bin_dir = r'C:\Users\<user>\.local\bin'
os.makedirs(base, exist_ok=True)
os.makedirs(bin_dir, exist_ok=True)

# 1. 下载 tarball
url = 'https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/latest.tar.gz'
r = requests.get(url, timeout=30)

# 2. 解压
tmp = os.path.join(base, '_tmp_extract')
with tarfile.open(fileobj=io.BytesIO(r.content), mode='r:gz') as tar:
    tar.extractall(tmp)

# 3. 复制 CLI 文件 (cli/ 子目录下)
cli_src = os.path.join(tmp, 'cli')
for f in ['skills_store_cli.py', 'skills_upgrade.py', 'version.json', 'metadata.json']:
    shutil.copy(os.path.join(cli_src, f), os.path.join(base, f))

# 4. 生成 config.json
with open(os.path.join(cli_src, 'metadata.json')) as fh:
    meta = json.load(fh)
config = {'self_update_url': meta.get('self_update_manifest_url',
    'https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/version.json')}
with open(os.path.join(base, 'config.json'), 'w') as fh:
    json.dump(config, fh, indent=2)

# 5. 创建 Windows .cmd wrapper
wrapper = os.path.join(bin_dir, 'skillhub.cmd')
with open(wrapper, 'w') as fh:
    fh.write('@echo off\r\npython "%USERPROFILE%\\.skillhub\\skills_store_cli.py" %*\r\n')

# 6. 清理
shutil.rmtree(tmp, ignore_errors=True)
```

安装后验证：`python C:\Users\<user>\.skillhub\skills_store_cli.py --version`

> **注意**：`~/.local/bin` 可能不在 PATH 中，直接用完整路径调用即可。

## 发布技能

### 前提
- 注册账号：必须通过 https://skillhub.cn 网站 UI（API 注册端点返回 405）
- 获取 Token：格式 `skh_...`（区别于虾评的 `sk_`）
- 登录：`skillhub login --key skh_xxx`

### SKILL.md 必须字段

**`slug` 字段是必需的**，没有会报错 `Error: SKILL.md 缺少 slug`：

```yaml
---
name: my-skill
slug: my-skill          # ← 必需！CLI 强制检查
description: "..."
version: 1.0.0
author: YourName
license: MIT
---
```

### 发布命令

```powershell
# 预检（不上传）
python $cli publish "path/to/skill-dir" --dry-run

# 正式发布
python $cli publish "path/to/skill-dir" --version 1.0.1 --changelog "fix: ..."

# 指定 token 和 host
python $cli publish "path/to/skill-dir" --token skh_xxx --host https://api.skillhub.cn
```

`$cli` = `C:\Users\<user>\.skillhub\skills_store_cli.py`

### 发布到指定 skills 目录（安装时）

```powershell
python $cli install <slug> --dir "D:\Hermes Agent CN Desktop\data\hermes-home\skills"
```

> ⚠️ 不指定 `--dir` 会装到 `./skills/`（当前工作目录），Hermes 识别不到。

## 已知坑

| 问题 | 原因 | 解决 |
|------|------|------|
| `--dry-run` 退出码 3221225477 | SKILL.md 缺 slug 字段，CLI 崩溃而非友好报错 | 加 `slug: xxx` |
| API 注册 405 | 不支持 API 注册 | 去网站注册 |
| `auth whoami` 报未登录 | 未执行 login | `skillhub login --key skh_xxx` |
| 安装后找不到 skillhub 命令 | `~/.local/bin` 不在 PATH | 用完整路径或加 PATH |

## 与虾评对比

| | 虾评 (xiaping.coze.com) | SkillHub (skillhub.cn) |
|---|---|---|
| Token 格式 | `sk_G2l-...` | `skh_...` |
| 注册方式 | API | 网站 UI |
| 发布方式 | REST API (requests multipart) | CLI (`skillhub publish`) |
| SKILL.md 额外字段 | 无 | `slug` 必需 |
| 网络 | 国内直连 | 国内直连（腾讯云 COS） |
