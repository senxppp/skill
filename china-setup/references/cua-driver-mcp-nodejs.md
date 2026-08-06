# cua-driver MCP 通信 — Node.js 实操模式

## 概述

cua-driver 通过 MCP 协议（JSON-RPC 2.0 over stdio）暴露 50+ 工具。Hermes 内置 Node.js v22，可直接编写脚本与 cua-driver MCP 服务器通信，实现桌面操控、浏览器自动化、截图分析等。

## 标准通信模板

```javascript
const { spawn } = require('child_process');

const cuaPath = "C:\\Users\\<user>\\AppData\\Local\\Programs\\Cua\\cua-driver\\bin\\cua-driver.exe";
const proc = spawn(cuaPath, ['mcp'], { stdio: ['pipe', 'pipe', 'pipe'] });

let buffer = '';
let reqId = 0;
const pending = {};

proc.stdout.on('data', (data) => {
  buffer += data.toString();
  processBuffer();
});

function processBuffer() {
  let idx;
  while ((idx = buffer.indexOf('\n')) !== -1) {
    const line = buffer.substring(0, idx).trim();
    buffer = buffer.substring(idx + 1);
    if (!line) continue;
    try {
      const parsed = JSON.parse(line);
      const cb = pending[parsed.id];
      if (cb) { delete pending[parsed.id]; cb(parsed); }
    } catch (e) { /* partial JSON — wait for more */ }
  }
}

function call(method, params) {
  return new Promise((resolve, reject) => {
    reqId++;
    pending[reqId] = resolve;
    const msg = JSON.stringify({
      jsonrpc: '2.0', id: reqId,
      method: 'tools/call',
      params: { name: method, arguments: params }
    }) + '\n';
    proc.stdin.write(msg);
    setTimeout(() => reject(new Error('Timeout')), 30000);
  });
}

function getText(r) {
  if (!r.result?.content) return '';
  for (const c of r.result.content) {
    if (c.type === 'text') return c.text;
  }
  return '';
}
```

## 关键工具列表

| 工具名 | 用途 | 重要参数 |
|--------|------|----------|
| `start_session` | 声明会话，获得光标与状态 | `session` (名称), `capture_scope` (auto/window/desktop) |
| `list_apps` | 列出所有已安装/运行的应用 | 无参数 |
| `list_windows` | 列出顶级窗口 | `pid` (筛选), `on_screen_only` |
| `get_window_state` | 获取 UIA 元素树 + 截图 | `pid`, `window_id`, `max_elements`, `max_depth` |
| `click` | 点击元素 | `pid`, `window_id`, `element_index`, `session` |
| `type_text` | 在元素中键入文字 | `pid`, `text`, `delivery_mode`, `session` |
| `press_key` | 发送按键 | `pid`, `key`, `delivery_mode`, `session` |
| `launch_app` | 启动应用/打开URL | `path`, `urls`, `name` |
| `bring_to_front` | 将窗口提到前台（**打破无前台约定**） | `pid`, `window_id` |
| `screenshot` | 截取屏幕 | 需先通过风险审批（首次使用会报错） |

## 已验证的工作流

### 1. 启动会话 + 打开网页

```javascript
await call('start_session', { session: 'my-session', capture_scope: 'auto' });
await call('launch_app', { urls: ["https://www.bilibili.com"] });
// 返回结果包含 pid（如 16060）
```

### 2. 获取窗口状态（UIA 元素树 + 截图）

```javascript
// 先找到窗口
let r = await call('list_windows', { on_screen_only: true });
// 从返回文本中解析 pid 和 window_id

// 然后获取元素树
r = await call('get_window_state', {
  pid: edgePid,
  window_id: edgeWid,
  max_elements: 100,
  max_depth: 10
});
```

`get_window_state` 返回的 `content` 数组包含：
- `content[0]` — 通常是结构化数据或元信息
- `content[1]` — Markdown 格式的 UIA 元素树，每个可交互元素标记为 `[元素索引N]`

### 3. 点击地址栏（已验证 ✅）

Edge Chromium 地址栏的 UIA 元素索引为 **6**（在工具栏中，Edit 类型，名称为"地址和搜索栏"）：

```javascript
// 先获取窗口状态（刷新元素缓存）
await call('get_window_state', { pid, window_id, max_elements: 30 });
// 点击地址栏
await call('click', { pid, window_id, element_index: 6, session: 'my-session' });
```

### 4. 在地址栏输入文字（需前台模式 ⚠️）

**Chromium Edge 的 `Chrome_WidgetWin_1` 窗口类不支持后台键盘输入。** 必须先 `bring_to_front`，然后用 `delivery_mode: 'foreground'`：

```javascript
// 1. 激活窗口（用户会看到 Edge 跳到前台）
await call('bring_to_front', { pid });

// 2. 全选 + 输入
await call('press_key', { pid, key: 'ctrl+a', delivery_mode: 'foreground', session });
await new Promise(r => setTimeout(r, 300));
await call('type_text', { pid, text: 'bilibili.com', delivery_mode: 'foreground', session });
await new Promise(r => setTimeout(r, 300));
await call('press_key', { pid, key: 'return', delivery_mode: 'foreground', session });
```

**限制：**
- ✅ `click`（UIA 后台点击） — 背景可用，无需前台
- ❌ `type_text` / `press_key` — 对 `Chrome_WidgetWin_1` 需要前台
- ✅ `type_text` / `press_key` — 对原生 Windows 窗口（记事本、资源管理器等）后台可用

### 5. 浏览器 CDP 工具

cua-driver 暴露了 CDP 级的浏览器工具（`browser_launch`, `browser_navigate`, `browser_click`, `browser_type`, `browser_pointer`），但这些需要 `target_id` + `tab_id`（从 `get_browser_state` 获取），**不能直接用 `pid` 和 `window_id`**。

尝试用 `browser_navigate` 传 `pid`/`window_id` 会报错：`Missing required string field: tab_id`。

## PowerShell 5.1 运行 Node 脚本

```powershell
cmd /c '"D:\Hermes Agent CN Desktop\data\versions\0.18.2-cn.2\node\node.exe" script.js'
```

脚本建议放在无空格的临时路径下：
```powershell
C:\Users\用户名\AppData\Local\Temp\hermes-cua-script.js
```

## 完整 E2E 示例：B站自动化（已验证 ✅）

以下示例演示了完整的浏览器自动化流程：打开网页 → 读取 UIA 树 → 找到目标元素 → 点击 → 等待 → 再次读取 → 再次点击。

### 场景：进入 B站 空间页 → 点击「投稿」标签 → 点开一个视频

```javascript
const { spawn } = require('child_process');
const cuaPath = "C:\\Users\\<user>\\AppData\\Local\\Programs\\Cua\\cua-driver\\bin\\cua-driver.exe";

async function main() {
  const proc = spawn(cuaPath, ['mcp'], { stdio: ['pipe', 'pipe', 'pipe'] });
  let buffer = '';
  let reqId = 0;
  const pending = {};

  proc.stdout.on('data', (data) => {
    buffer += data.toString();
    let idx;
    while ((idx = buffer.indexOf('\\n')) !== -1) {
      const line = buffer.substring(0, idx).trim();
      buffer = buffer.substring(idx + 1);
      if (!line) continue;
      try {
        const parsed = JSON.parse(line);
        const cb = pending[parsed.id];
        if (cb) { delete pending[parsed.id]; cb(parsed); }
      } catch (e) {}
    }
  });

  function call(method, params) {
    return new Promise((resolve, reject) => {
      reqId++;
      pending[reqId] = resolve;
      const msg = JSON.stringify({
        jsonrpc: '2.0', id: reqId,
        method: 'tools/call',
        params: { name: method, arguments: params }
      }) + '\\n';
      proc.stdin.write(msg);
      setTimeout(() => reject(new Error('Timeout')), 30000);
    });
  }

  function getText(r) {
    if (!r.result?.content) return '';
    for (const c of r.result.content) {
      if (c.type === 'text') return c.text;
    }
    return '';
  }

  try {
    // Step 1: 启动会话
    await call('start_session', { session: 'bilibili-demo', capture_scope: 'auto' });

    // Step 2: 用 Start-Process 或 launch_app 打开目标网站
    // （用 launch_app 可以只传 urls 参数，不传 path/name 则用默认浏览器）
    await call('launch_app', { urls: ["https://space.bilibili.com/1027151705"] });

    await new Promise(r => setTimeout(r, 5000)); // 等页面加载

    // Step 3: 找 Edge 窗口
    let r = await call('list_windows', { on_screen_only: true });
    const winsText = getText(r);
    // 从 winsText 解析 pid 和 window_id（正则匹配 msedge 相关的行）
    const pidMatch = winsText.match(/msedge\\.exe.*?pid[\\:\\s]*(\\d+)/i);
    const widMatch = winsText.match(/window_id[\\:\\s]*(\\d+)/i);
    const edgePid = pidMatch ? parseInt(pidMatch[1]) : null;
    const edgeWid = widMatch ? parseInt(widMatch[1]) : null;

    // Step 4: 刷新元素缓存，获取 UIA 树
    r = await call('get_window_state', {
      pid: edgePid, window_id: edgeWid,
      max_elements: 300, max_depth: 20   // Chromium 网页内容需要较深遍历
    });
    const tree = getText(r);
    // tree = Markdown 格式的 UIA 树, 每行如:
    // "- [73] Hyperlink " 投稿 1" [value=... actions=[invoke,set_value]]"
    // 从 tree 文本中查找目标元素索引

    // Step 5: 在 UIA 树中查找目标元素
    // 方法：在 tree 文本中用正则匹配关键文本和 [索引]
    const targetMatch = tree.match(/\\[([0-9]+)\\].*?投稿/);
    const tabIndex = targetMatch ? parseInt(targetMatch[1]) : null;

    if (tabIndex !== null) {
      // Step 6: 点击元素
      r = await call('click', {
        pid: edgePid, window_id: edgeWid,
        element_index: tabIndex, session: 'bilibili-demo'
      });
      // 返回: ✅ Posted click on Chromium element [N] at screen (x,y) (background)

      await new Promise(r => setTimeout(r, 2000)); // 等待页面变化

      // Step 7: 刷新元素树（重要！点击后必须重新获取）
      r = await call('get_window_state', {
        pid: edgePid, window_id: edgeWid,
        max_elements: 300, max_depth: 20
      });
      const newTree = getText(r);

      // Step 8: 在更新后的树中找视频链接
      const videoMatch = newTree.match(/\\[([0-9]+)\\].*?P2s唱歌/);
      const videoIndex = videoMatch ? parseInt(videoMatch[1]) : null;

      if (videoIndex !== null) {
        // Step 9: 点击视频
        await call('click', {
          pid: edgePid, window_id: edgeWid,
          element_index: videoIndex, session: 'bilibili-demo'
        });
        console.log('✅ 视频已点击播放！');
      }
    }
  } catch (e) {
    console.error('错误:', e.message);
  }

  proc.kill();
}

main();
```

### UIA 树解析要点

1. **Chromium Edge 的 UIA 树深度** — 网页内容（按钮、链接、文本）会深入到 15-20 层，所以设 `max_depth: 20, max_elements: 300`。浏览器工具栏只有约 15 个元素（索引 0-14），网页内容从索引 15+ 开始。
2. **索引编号规则** — UIA 元素的索引格式为 `[数字]`，缩进表示层级关系。每个 `max_elements`/`max_depth` 限制下的子树索引是唯一的整数。
3. **文本匹配** — 在 UIA 树中查找元素时，用 JavaScript 正则匹配 `\\[([0-9]+)\\].*?<目标文字>` 即可提取索引号。目标文字可以包含中文、特殊符号。
4. **多次匹配** — 同一文字可能出现在多个元素中（标题 + Hyperlink）。取第一个匹配通常够用，若担心不准确可增加上下文匹配（如匹配 `Hyperlink.*目标文字` 而非所有类型）。
5. **get_window_state 附带截图** — `content[1]` 是 base64 PNG 格式的截图（约 700KB），可用于视觉分析。`content[0]` 是 UIA 树文本。调用 `get_window_state` 永远返回两者。

### Chromium Edge 特殊处理总结

| 操作 | Edge Chromium | 原生 Windows 窗口 |
|------|--------------|-------------------|
| `click` | ✅ 后台可用（UIA） | ✅ 后台可用 |
| `type_text` | ❌ 需 `bring_to_front` + `foreground` | ✅ 后台可用 |
| `press_key` | ❌ 需 `bring_to_front` + `foreground` | ✅ 后台可用 |
| `get_window_state` | ✅ 返回浏览器 chrome + 网页内容 | ✅ 返回完整树 |
| 元素索引寿命 | 单次 `get_window_state` 有效 | 同左 |

## 已知问题

| 问题 | 原因 | 对策 |
|------|------|------|
| `screenshot` 工具返回 `"Permission denied: tool has no reviewed risk classification"` | 第一次使用需要风险审批 | 改用 `get_window_state`（自带截图）；或通过 `hermes` 自带的 MCP 客户端调用（已预审批） |
| 同时运行的 cua-driver 实例不能超过 1 个 daemon + N 个 CLI/MCP 客户端 | 竞态条件 | 每个脚本结束时 `proc.kill()` |
| `get_window_state` 返回空树（0 elements） | window_id 与 pid 不匹配 | 先 `list_windows` 获取正确的 window_id |
| 元素索引过时（Element N not in cache） | 每次 `get_window_state` 刷新索引 | 每次 click 前重新 `get_window_state` |
