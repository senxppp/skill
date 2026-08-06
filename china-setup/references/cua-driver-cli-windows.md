# cua-driver CLI direct approach (Windows)

When the Hermes `computer_use` tool is **not available** in the current session (e.g. only `web` toolset is exposed for the weixin channel), you can still drive the desktop using cua-driver's CLI commands directly via `terminal`.

## Prerequisites: daemon must be running

```powershell
# Start the daemon (one-time, survives until reboot or crash)
Start-Process -FilePath "C:\Users\$env:USERNAME\AppData\Local\Programs\Cua\cua-driver\bin\cua-driver.exe" -ArgumentList "serve" -WindowStyle Minimized

# Verify
C:\Users\xpppj\AppData\Local\Programs\Cua\cua-driver\bin\cua-driver.exe status
# → "Cua Driver daemon is running"
```

## The PowerShell 5.1 pipe problem

`cua-driver call <tool>` requires JSON on stdin. PowerShell 5.1 strips quotes from JSON when passed as `--json` argument. Piping via `| & "path.exe"` is detected as "backgrounding" by Hermes' terminal tool.

### Python subprocess (reliable)

Write a `.py` file, then call it with properly quoted paths:

```python
import subprocess, json

driver = r"C:\Users\xpppj\AppData\Local\Programs\Cua\cua-driver\bin\cua-driver.exe"

# Launch an app
args = {"path": r"D:\Program Files\Tencent\Androws\WmpfRuntime\5.10.2700.327\runtime\WeChatAppEx.exe"}
proc = subprocess.run([driver, "call", "launch_app"],
    input=json.dumps(args), capture_output=True, text=True, timeout=30)
result = json.loads(proc.stdout)
```

Then invoke with properly quoted paths:

```powershell
& 'C:\Users\xpppj\AppData\Local\Programs\Python\Python312\python.exe' 'D:\path\to\script.py'
```

The `&` operator + single quotes works for executing Python. The `&` only fails when it appears after a pipe `|`.

### Alternative: cmd.exe /c with pipe

For simple one-liners (not multi-arg JSON):

```powershell
cmd.exe /c echo '{"key":"value"}' | "C:\path\to\cua-driver.exe" call tool_name
```

But this struggles with paths containing spaces — the pipe symbol breaks path quoting.

## Key CLI tools

| Tool | What it does | Typical use |
|------|-------------|-------------|
| `status` | Check if daemon is running | Before any operation |
| `list-tools` | List all available tools | Find tool names |
| `describe <tool>` | Get input schema for a tool | Know what args to pass |
| `call launch_app` | Launch an app without stealing focus | Open WeChat, Notepad, etc. |
| `call list_windows` | List all open windows (name, pid, bounds, window_id) | Find target window |
| `call get_window_state` | Get UIA tree for a window | Read app content via accessibility |
| `call get_desktop_state` | Full desktop screenshot (returns base64 PNG) | Vision analysis of screen |
| `call get_accessibility_tree` | Lightweight process/window overview | Quick window inventory |
| `call click` | Click at pixel coords on a target pid | Click buttons |
| `call type_text` | Type text into a focused window | Fill forms |

### Finding the right window

```python
# After launch_app, wait for window to appear
import time
time.sleep(3)

# List all windows
proc = subprocess.run([driver, "call", "list_windows"],
    input="{}", capture_output=True, text=True, timeout=30)
result = json.loads(proc.stdout)
windows = result.get("windows", [])

# Find your target
for w in windows:
    name = w.get("title", w.get("name", ""))
    pid = w.get("pid", "")
    print(f"  PID={pid} Name={name}")
```

The returned window object contains:
```json
{
  "app_name": "Weixin.exe",
  "title": "微信",
  "pid": 39708,
  "window_id": 1443564,
  "bounds": {"x": 1486, "y": 9, "width": 2350, "height": 1346},
  "minimized": false,
  "is_on_screen": true,
  "z_index": 7
}
```

## Reading app content

### Approach A: UIA tree (text-based apps)

Good for standard Windows apps (Notepad, Settings, File Explorer). Bad for apps using custom rendering (WeChatAppEx, Electron apps without accessibility enabled).

```python
args = {"pid": 39708, "window_id": 1443564}
proc = subprocess.run([driver, "call", "get_window_state"],
    input=json.dumps(args), capture_output=True, text=True, timeout=30)
result = json.loads(proc.stdout)
elements = result.get("elements", [])
```

### Approach B: Screenshot + vision model (universal)

Use when UIA tree is empty or the app uses custom rendering (WeChat, games, media players).

**Full pipeline:**

```python
import subprocess, json, base64, urllib.request

# 1. Get desktop screenshot
proc = subprocess.run([driver, "call", "get_desktop_state"],
    input="{}", capture_output=True, text=True, timeout=60)
result = json.loads(proc.stdout)
b64_data = result["screenshot_png_b64"]  # 4K PNG ~2MB base64

# 2. Send to vision model (DashScope Qwen-VL-Plus)
api_key = "sk-..."
url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
payload = {
    "model": "qwen-vl-plus",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "描述这个微信窗口里有什么消息"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_data}"}}
        ]
    }]
}
req = urllib.request.Request(url, json.dumps(payload).encode(),
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=120) as resp:
    analysis = json.loads(resp.read())
```

**Pitfalls:**
- Full 4K screenshots are ~2MB base64 — OK for DashScope API but consumes tokens
- The vision model sees the whole screen, not just your target window. Consider cropping if PIL is available, or ask the vision model to focus on a specific region
- The `get_desktop_state` screenshot is in *physical pixels*. Window bounds from `list_windows` are in *virtual pixels* (scaled). On a 200% display on 3840×2160: screenshot = 3840×2160, but bounds may need scaling. If using `click` with pixel coordinates, pass the scaled ones

## Example: full WeChat message check workflow

See the conversation for a real run — the complete flow was:

1. Start cua-driver daemon
2. `call launch_app` with WeChat path → get PID
3. Wait 3-5s for window to appear
4. `call list_windows` → find "微信" window, record bounds
5. `call get_desktop_state` → get 4K screenshot
6. Send screenshot to DashScope Qwen-VL-Plus with prompt asking about visible messages
7. Report structured results back to user

## Cleaning up

```python
# Stop the daemon when done (optional, keeps running for later use)
subprocess.run([driver, "stop"], input="{}", capture_output=True, text=True)
```

Or leave it running — the daemon is lightweight and subsequent calls are instant.
