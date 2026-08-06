# Windows 路径空格引号处理

## 问题

Hermes 在 Windows PowerShell 5.1 中执行 `terminal` 命令时，路径含空格会出错：

```powershell
# ❌ 报错：'D:\Hermes' 不是内部或外部命令
cmd /c set NPM_CONFIG_REGISTRY=https://registry.npmmirror.com && D:\Hermes Agent CN Desktop\...\npm.cmd install -g pptxgenjs
```

原因：PowerShell 将空格解释为参数分隔符，`cmd /c` 把路径截断在第一个空格处。

## 解决方案

### 用单引号包住 cmd /c 的完整命令（推荐）

```powershell
cmd /c 'set VAR=VAL && "C:\Path With Spaces\program.exe" args'
```

注意：
- 外层用 **单引号 `'...'`** 包住整个命令字符串
- 内层程序路径用 **双引号 `"..."`** 包住
- 环境变量设置和命令用 `&&` 连接

### 实际例子

```powershell
# 设置 npm 镜像 + 安装包
cmd /c 'set NPM_CONFIG_REGISTRY=https://registry.npmmirror.com && "D:\Hermes Agent CN Desktop\data\versions\0.18.2-cn.2\node\npm.cmd" install pptxgenjs'

# 运行 Node.js 脚本
cmd /c 'cd /d "D:\Hermes Agent CN Desktop\data" && "D:\Hermes Agent CN Desktop\data\versions\0.18.2-cn.2\node\node.exe" script.js'
```

### 备选方案：用短路径 8.3 别名

```powershell
# 查看短路径
cmd /c 'for %I in ("D:\Hermes Agent CN Desktop") do @echo %~sI'
# 输出类似：D:\HERMES~1\AGENT~1\...
```

## 已验证的完整命令模式

### npm 安装
```powershell
cmd /c 'set NPM_CONFIG_REGISTRY=https://registry.npmmirror.com && "D:\Hermes Agent CN Desktop\data\versions\0.18.2-cn.2\node\npm.cmd" install -g <package>'
```

### 运行 Node 脚本
```powershell
cmd /c 'cd /d "D:\Hermes Agent CN Desktop\data" && "D:\Hermes Agent CN Desktop\data\versions\0.18.2-cn.2\node\node.exe" script.js'
```
