# PPT 页面切换动画参考

## 概述

PptxGenJS **原生不支持**页面切换动画（transition）。本 skill 通过 **python-pptx + lxml XML 注入**的方式在生成的 `.pptx` 中添加 `p:transition` 元素，实现 PowerPoint 级别的切换效果。

**工作流**：PptxGenJS 生成 PPTX → Python 脚本注入动画 → 输出最终文件

---

## 可用切换效果

| 效果名 | XML 标签 | 方向/参数 | 说明 |
|--------|---------|----------|------|
| **zoom（缩放）** | `<p:zoom dir="in"/>` | `in` / `out` | 页面放大进入/缩小退出 |
| **dissolve（溶解）** | `<p:dissolve/>` | 无 | 像素化溶解过渡 |
| **push（推入）** | `<p:push dir="l"/>` | `l` / `r` / `u` / `d` | 新页面推走旧页面 |
| **wipe（擦除）** | `<p:wipe dir="l"/>` | `l` / `r` / `u` / `d` | 从一侧擦出显示 |
| **split（分裂）** | `<p:split orient="horz" dir="out"/>` | `horz`/`vert`, `in`/`out` | 左右/上下分裂 |
| **comb（梳齿）** | `<p:comb dir="l"/>` | `l` / `r` | 梳齿状交错推进 |
| **wheel（转轮）** | `<p:wheel/>` | 无 | 轮辐旋转展开 |
| **fade（淡入）** | `<p:fade/>` | 无 | 淡入淡出，最通用 |

### 速度设置

| 速度 | `spd` 值 | 适用场景 |
|------|----------|---------|
| 慢 | `slow` | 封面页、结尾页 |
| 中 | `med` | 内容页（默认） |
| 快 | `fast` | 快速浏览场景 |

### 推进方向

| 方向 | `dir` 值 | 说明 |
|------|----------|------|
| 左 | `l` | 从右向左推/擦 |
| 右 | `r` | 从左向右推/擦 |
| 上 | `u` | 从下向上推/擦 |
| 下 | `d` | 从上向下推/擦 |

---

## 一键注入脚本

已附带 `scripts/inject_transitions.py`，使用方法：

```bash
python scripts/inject_transitions.py input.pptx output.pptx
```

**默认策略**：封面 slow+zoom-in → 内容页混合不同效果 → 结尾 slow+fade，每页效果不重复。

超出 10 页时自动回退为 `med + fade`。

### 自定义注入

修改脚本中的 `TRANSITIONS` 列表即可自定义每页效果：

```python
TRANSITIONS = [
    ('slow', 'zoom-in'),   # 第1页
    ('med', 'push-r'),     # 第2页
    ('med', 'fade'),       # 第3页
    # ... 按需添加
]
```

---

## 在 PptxGenJS 工作流中使用

### 完整流程

```
1. PptxGenJS 生成 presentation.pptx
2. 运行: python scripts/inject_transitions.py presentation.pptx presentation_animated.pptx
3. 交付 presentation_animated.pptx
```

### compile.js 中添加动画步骤

在 `slides/compile.js` 末尾添加：

```javascript
// compile.js 末尾
const { execSync } = require('child_process');
try {
    execSync('python scripts/inject_transitions.py ./output/presentation.pptx ./output/presentation_animated.pptx');
    console.log('✓ 切换动画注入完成');
} catch (e) {
    console.log('⚠ 动画注入跳过:', e.message);
}
```

---

## 推荐动画搭配

### 商务汇报
```
封面: slow + fade
目录: med + push-r
内容: med + fade（保持一致性）
结尾: slow + fade
```

### 创意展示
```
封面: slow + zoom-in
内容: 混合 push-l / wipe-r / dissolve
结尾: slow + dissolve
```

### 教学课件
```
封面: slow + fade
章节分隔: med + split-horz
内容: med + push-r
结尾: slow + fade
```

---

## 注意事项

1. **动画仅在 PowerPoint / WPS 中可见**，浏览器/在线预览不会播放
2. 封面和结尾建议用 `slow`，内容页用 `med`
3. 不要每页用不同的剧烈动画（如 comb、wheel），会显得花哨
4. 整个演示最多 2-3 种效果混搭即可，`fade` 是万能安全牌
5. 通过 `pres.save()` 保存（python-pptx 原生），不要用 zipfile 重写
