# SkillHub Windows 安装指南

## 前提条件

- Python 3.x（**必须真正安装**，WindowsApps 零字节空壳不行）
- tar.exe（Windows 11 自带）
- 翻墙代理（下载用国内 CDN，一般不需要，但第一次可能需代理）

## 安装步骤

### 1. 检查/安装 Python

```powershell
# WindowsApps 的 python.exe 是空壳，会跳转 Microsoft Store
# 用 winget 装真正的 Python：
winget install --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
# 安装后验证：
python --version
# 应输出类似 "Python 3.12.10"
```

> 装完后 `where python` 会显示两个路径，WindowsApps 的空壳排在前面但不影响功能。

### 2. 下载 skillhub 工具包

```powershell
$tmpDir = "$env:TEMP\skillhub-install"
New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null

curl.exe -fsSL "https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/latest.tar.gz" -o "$tmpDir\kit.tar.gz"

tar -xzf "$tmpDir\kit.tar.gz" -C $tmpDir
# 解压得到 cli/ 目录，里面包含 skills_store_cli.py
```

### 3. 安装 CLI 文件

```powershell
$src = "$tmpDir\cli"
$dest = "$env:USERPROFILE\.skillhub"
New-Item -ItemType Directory -Force -Path $dest | Out-Null

Copy-Item "$src\skills_store_cli.py" "$dest\skills_store_cli.py" -Force
Copy-Item "$src\skills_upgrade.py" "$dest\skills_upgrade.py" -Force
Copy-Item "$src\version.json" "$dest\version.json" -Force
Copy-Item "$src\metadata.json" "$dest\metadata.json" -Force
```

### 4. 创建配置文件

```powershell
$config = @{
    self_update_url = "https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/version.json"
} | ConvertTo-Json
Set-Content -Path "$dest\config.json" -Value $config -Encoding UTF8
```

### 5. 创建 Windows 包装器（.cmd）

bash 包装器在 Windows 上不工作，创建一个 `.cmd` 文件：

```powershell
$binDir = "$env:USERPROFILE\.local\bin"
New-Item -ItemType Directory -Force -Path $binDir | Out-Null

$wrapper = "@echo off`npython `"$dest\skills_store_cli.py`" %*"
Set-Content -Path "$binDir\skillhub.cmd" -Value $wrapper -Encoding ASCII
```

### 6. 加入 PATH 并测试

```powershell
# 把 .local\bin 加入当前会话 PATH
$env:Path += ";$env:USERPROFILE\.local\bin"

# 测试
python "$env:USERPROFILE\.skillhub\skills_store_cli.py" --version
# 或直接调用 .cmd 包装器
$env:USERPROFILE\.local\bin\skillhub.cmd search --version
```

> 重启终端后，`$env:USERPROFILE\.local\bin` 通常已在 PATH 中。如果不在，手动添加。

## 安装技能到 Hermes

Hermes 的 skills 目录在：`D:\Hermes Agent CN Desktop\data\hermes-home\skills`

```powershell
# 用完整路径调用，避免 PATH 解析问题
python "$env:USERPROFILE\.skillhub\skills_store_cli.py" install <技能名称> --dir "D:\Hermes Agent CN Desktop\data\hermes-home\skills"
```

搜索技能：
```powershell
python "$env:USERPROFILE\.skillhub\skills_store_cli.py" search <关键词>
```

## 设定 SkillHub 为优先源

如果用户同意，按照 SkillHub 安装说明中的「优先策略」处理：
- 涉及技能发现/安装/升级时优先 `skillhub`（国内 CDN 更快更合规）
- 不可用/无匹配则回退默认源
- 本会话即刻生效，无需重启

## 已知坑

- **`&` 操作符冲突**：PowerShell 5.1 下 `&` 在行首会被 Hermes 终端识别为后台操作符。用完整路径直接调用 Python 脚本，不用包装器的 `&` 方式。
- **WindowsApps python.exe 零字节问题**：`where python` 返回 Store 空壳路径 → 需要用 `"C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe"` 完整路径。
- **bash 包装器不可用**：`install.sh` 创建的是 bash shebang 脚本，Windows 无法直接执行。替代方案是 `.cmd` 包装器或直接调 Python。
