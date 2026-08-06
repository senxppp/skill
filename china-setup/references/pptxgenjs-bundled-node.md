# Hermes 内置 Node.js + pptxgenjs 做 PPT

## 环境

Hermes CN Desktop 自带 Node.js v22.12.0，路径：
```
D:\Hermes Agent CN Desktop\data\versions\0.18.2-cn.2\node\node.exe
```

npm 也自带：
```
D:\Hermes Agent CN Desktop\data\versions\0.18.2-cn.2\node\npm.cmd
```

## 安装 pptxgenjs

必须在**脚本所在目录本地安装**（全局安装 `-g` 在 Node exe 所在目录，但 require 找不到）：

```powershell
cmd /c 'cd /d "D:\Hermes Agent CN Desktop\data" && set NPM_CONFIG_REGISTRY=https://registry.npmmirror.com && "D:\Hermes Agent CN Desktop\data\versions\0.18.2-cn.2\node\npm.cmd" install pptxgenjs'
```

安装后会在当前目录生成 `node_modules/pptxgenjs`。

## 制作 PPT 脚本模板

```javascript
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "你的名字";
pres.title = "标题";

// 添加页面
let slide = pres.addSlide();
slide.background = { color: "FFFFFF" };
slide.addText("标题文字", { 
  x: 0.5, y: 0.5, w: 9, h: 1, 
  fontSize: 36, fontFace: "Arial Black", color: "1E293B", bold: true 
});

pres.writeFile({ fileName: "output.pptx" })
  .then(() => console.log("✅ PPT 已生成"))
  .catch(err => console.error("❌ 失败:", err));
```

## 运行脚本

```powershell
cmd /c 'cd /d "D:\Hermes Agent CN Desktop\data" && "D:\Hermes Agent CN Desktop\data\versions\0.18.2-cn.2\node\node.exe" script.js'
```

## 注意事项

- 颜色值**不能加 `#` 前缀**：`"FF0000"` ✅，`"#FF0000"` ❌（会损坏文件）
- 每页幻灯片尺寸：16:9 = 10" × 5.625"
- pptxgenjs 会修改传入的 option 对象，**不要复用同一个对象**在多个 addShape/addText 调用中 —— 用工厂函数每次生成新对象
- 字体建议：标题用 `Arial Black` 或 `Georgia`，正文用 `Calibri`
