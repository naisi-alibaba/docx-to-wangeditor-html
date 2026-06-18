# docx-to-wangeditor-html

> **把 Word(.docx)协议/政策文档，转成"粘进 wangEditor 富文本编辑框后格式不丢"的 HTML。**
> **Convert Word (.docx) docs into HTML that survives a copy‑paste into a wangEditor rich‑text editor — with headings, bold and tables intact.**

`中文文档` ↓ ｜ [English below ↓](#english)

---

## 中文

### 一句话说明
你在 Word 里写好的**隐私政策 / 用户协议 / 服务协议 / 各类清单**，需要粘进后台系统里一个**基于 wangEditor 的富文本编辑框**。但直接粘贴：要么排版乱七八糟，要么标题、加粗全部丢失，甚至**整篇文档塌成一坨没有任何格式的纯文本**。
这个技能把 `.docx` 转成**专门适配 wangEditor**的干净 HTML——你打开后 `Ctrl+A → Ctrl+C → 粘贴`，标题层级、加粗、表格都会被完整保留。

### 它到底解决什么问题（痛点）
把 Word 文档塞进 wangEditor 编辑框时，你几乎一定会撞上下面这几种情况：

1. **直接从 Word 复制粘贴** → 带进大量 Word 的垃圾内联样式，字体怪、行距乱、夹带多余空行，根本没法看。
2. **把文档另存成网页 / 渲染后再复制粘贴** → 标题不再是标题、加粗消失，**粘进去就是一片纯文本**。
3. **最让人崩溃的一种**：同样的操作，**有的文档粘进去格式好好的、有的却整篇变成一行行纯文本**，毫无规律可循——你改字体、改对齐、加空格，全都没用，完全是"玄学"。

这个技能就是为彻底根治以上问题而生，尤其是第 3 种谁都查不出原因的"玄学塌陷"。

### 为什么会这样（根因，也是这个技能的价值所在）
目标编辑框是 **wangEditor v4**——一个 `contenteditable` 的富文本编辑器（DOM 上是 `<div class="w-e-text">`），国内大量后台 / CMS / OMS 都在用它。它的**粘贴管线**有两个关键行为，决定了"你必须喂给它什么样的 HTML"：

- **行为一：粘贴时会剥离内联样式，但保留 HTML 标签。**
  它会丢掉 `style="font-size:24px"` 这类内联样式，但保留 `<h1>/<h2>/<h3>/<strong>/<table>` 等**标签**，再用它自己的 CSS 去渲染。
  → 所以正确姿势**不是**靠内联样式（必被丢弃），而是用**真正的语义标签**：标题就是 `<h2>`，加粗就是 `<strong>`，表格就是 `<table>`。本技能产出的正是这种干净语义化 HTML，于是标题、加粗、表格都能"活着"进编辑器。

- **行为二（致命坑，玄学塌陷的真凶）：内容里只要出现 `http(s)://` 网址，整篇就可能塌成纯文本。**
  wangEditor 会**自动把网址转成超链接**。当网址**紧贴中文**时（Word 文档里极其常见，例如 `您可访问https://account.example.com/完成注销`，网址和中文之间没有空格），它的自动链接逻辑会出错、底层 `insertHTML` 调用失败，于是**把整篇文档降级处理成一个 `<p>` 加一长串 `<br>`——所有标题、加粗瞬间全没**。而且只要带 `https://`，加空格也救不回来。
  → 这就是"**没有网址的隐私政策一直能正常粘贴、带了一个网址的服务协议却整篇炸掉**"的真正原因。
  → 本技能的解法：输出网址时**去掉 `http(s)://` 前缀、并且不包 `<a>` 标签**（渲染成 `account.example.com/…`）。这样 wangEditor 不会去自动转链接，`insertHTML` 不再失败，整篇格式完好。

> 一句话总结根因：**wangEditor 认标签不认内联样式（所以要喂语义化 HTML），且会被 `http(s)://` 自动链接搞崩（所以要给网址去 scheme）。**

### 转换前 vs 转换后
以一段真实出现过的源文本为例：

| | 内容 / 结果 |
|---|---|
| **源（Word）** | `网页端：您可通过访问https://account.example.com/完成账号注销` |
| **直接粘贴** | ❌ **整份文档**变成无格式纯文本（标题/加粗全丢） |
| **本技能产出后粘贴** | ✅ 该处显示 `account.example.com/完成账号注销`，且**整份文档**的标题、加粗、表格全部正常 |

### 它具体做了什么
输入一个 `.docx`（或一个目录），输出可直接粘贴的 HTML。转换规则：
- Word 大纲级别 → `<h1>/<h2>/<h3>`；
- 加粗 → `<strong>`；Word 表格 → `<table>`；
- `版本：` / `发布时间：` → 居中小字；
- **所有 `http(s)://` 网址去掉 scheme、不加链接**（核心避坑）；
- 默认整篇左对齐（可加 `--center-title` 让标题居中，wangEditor 两种都接受）；
- **忠实保留原文结构，绝不擅自把清单改成表格**；
- 纯 Python 标准库实现，**无需安装 python-docx 或任何第三方依赖**。

### 适用场景
- 法务 / 合规 / 产品同学，在 Word 里维护**隐私政策、用户协议、服务协议、个人信息收集清单、第三方 SDK 共享清单、权限清单**等文本，需要发布到后台 wangEditor 编辑框。
- 任何"把 Word 粘进 wangEditor 后格式丢失 / 变纯文本 / 整篇居中"的场景。
- 任何**基于 wangEditor 的富文本编辑器**（本技能针对的是这个框架，不绑定某个具体系统）。

### 安装
```text
/plugin marketplace add naisi-alibaba/docx-to-wangeditor-html
/plugin install docx-to-wangeditor-html@docx-to-wangeditor
/reload-plugins
```

### 使用
最简单：直接对 Claude Code 说 **"把这些 Word 转成能粘进 wangEditor 编辑框的 HTML"**，它会调用本技能。
或手动运行转换脚本：
```bash
# 单个文件
py "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/docx2wangeditor.py" "C:/路径/服务协议.docx"
# 整个目录（自动跳过 ~$ 开头的 Word 临时锁文件）；加 --center-title 让标题居中
py "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/docx2wangeditor.py" "C:/路径/目录"
```

### 产出文件（每个 .docx 旁生成两个）
- **`<name>.html`** —— 完整网页。**用浏览器打开 → `Ctrl+A` 全选 → `Ctrl+C` 复制 → 粘进编辑框**（主用法）。
- `<name>_fragment.html` —— 只含正文的 HTML 源码。如果某个字段要求你**直接填 HTML 代码**，用这个。

### 在真实编辑器里验证（可选，但被怀疑格式不对时强烈建议）
光看 HTML 看不出粘贴效果，用内置的 Playwright 脚本真刀真枪粘一遍：
```bash
npx --yes playwright@1.61 install chromium            # 仅首次
PWPATH=$(find "$(npm config get cache)/_npx" -maxdepth 3 -name playwright -type d -path '*node_modules*' | head -1)
NODE_PATH=$(dirname "$PWPATH") node "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/validate_paste.js" \
  "<编辑器页面URL>" "C:/路径/服务协议.html"
```
会弹出有界面的 Chromium，**登录一次**（会话保存在 `C:/tmp/oms_profile`，可用环境变量 `OMS_PROFILE` 改）；
随后逐个把 HTML 粘进编辑器，输出 `PASS`（有标题/加粗、无塌陷）或 `FAIL`（塌成纯文本）。
定位罪魁的方法：把正文按块二分截断分别粘贴，出问题的通常就是含网址的那一段。

### 常见问题（FAQ）
- **Q：网址去掉 `https://` 算不算改了内容？** A：这是让粘贴不崩的必要取舍；`account.example.com` 仍清晰可读。若必须保留 `https://`，可在粘贴后于编辑器里手动补那一处。
- **Q：为什么不顺手把清单做成表格，更好看？** A：刻意忠实保留原文结构；要表格化请明确提出。
- **Q：验证脚本用 headless 打不开编辑器？** A：这类后台有权限校验，需用 headed（有界面）模式并登录一次，本脚本默认就是 headed。
- **Q：会处理图片吗？** A：不导出 Word 内嵌图片（协议类文档通常无图）。

### 已知限制
- 针对 **wangEditor v4** 的粘贴行为调校；其它富文本编辑器（如 TinyMCE/CKEditor/Quill）行为不同，可能不适用。
- 仅处理 `.docx`（不处理老的 `.doc`）。

---

## English

### In one sentence
You author **privacy policies / user & service agreements / various lists** in Word, and need to paste them into a back‑office **wangEditor rich‑text box**. But pasting directly either looks messy, drops all headings and bold, or — worst of all — **collapses the entire document into a wall of unformatted plain text**. This skill converts `.docx` into HTML **tailored to wangEditor**, so a plain `Ctrl+A → Ctrl+C → paste` keeps headings, bold and tables intact.

### The problem it solves
Pasting a Word document into a wangEditor box, you almost always hit one of these:
1. **Paste straight from Word** → tons of junk inline styles, weird fonts/spacing, stray blank lines.
2. **Save as a web page / copy a rendered page, then paste** → headings are no longer headings, bold is gone — **it looks like plain text**.
3. **The maddening one**: the exact same method **works for some documents but turns others into line‑after‑line of unformatted plain text**, with no apparent pattern — changing fonts, alignment, or adding spaces does nothing.

This skill exists to fix all of the above, especially the inexplicable case #3.

### Why it happens (the root cause — and the point of this skill)
The target is **wangEditor v4**, a `contenteditable` rich‑text editor (`<div class="w-e-text">`) used by many Chinese admin panels / CMS / OMS systems. Its **paste pipeline** has two behaviors that dictate what HTML you must feed it:

- **Behavior 1: on paste it strips inline styles but keeps tags.** It discards `style="font-size:24px"` etc., but keeps tags like `<h1>/<h2>/<h3>/<strong>/<table>` and renders them with its own CSS.
  → So the right approach is **not** inline styles (always discarded) but **real semantic tags**: a heading is `<h2>`, bold is `<strong>`, a table is `<table>`. This skill emits exactly that clean semantic HTML — so formatting survives.

- **Behavior 2 (the killer bug): any `http(s)://` URL can flatten the whole document into plain text.** wangEditor **auto‑links URLs**; when a URL is **glued to CJK text** (very common in Word, e.g. `…visithttps://account.example.com/done` with no space), its auto‑link logic breaks, the underlying `insertHTML` fails, and it **degrades the ENTIRE document to one `<p>` plus a long run of `<br>` — every heading and bold instantly gone**. A space doesn't help; the mere presence of `https://` triggers it.
  → This is exactly why a **URL‑free privacy policy always pasted fine while a service agreement with a single URL blew up entirely**.
  → The fix this skill applies: emit URLs **without the `http(s)://` scheme and without `<a>`** (e.g. `account.example.com/…`). wangEditor then won't auto‑link, `insertHTML` no longer fails, and formatting is preserved.

> Root cause in one line: **wangEditor honors tags but not inline styles (so feed it semantic HTML), and it chokes on `http(s)://` auto‑linking (so de‑scheme URLs).**

### Before vs after
| | Content / result |
|---|---|
| **Source (Word)** | `…you can visit https://account.example.com/ to delete your account` (URL glued to text) |
| **Paste directly** | ❌ the **whole document** becomes unformatted plain text |
| **Paste this skill's output** | ✅ shows `account.example.com/…` there, and the **whole document** keeps headings, bold and tables |

### What it does
Takes a `.docx` (or a folder) and writes paste‑ready HTML. Rules:
- Word outline level → `<h1>/<h2>/<h3>`; bold → `<strong>`; Word tables → `<table>`;
- `版本：` / `发布时间：` → small meta lines;
- **all `http(s)://` URLs de‑schemed, no `<a>`** (the key fix);
- left‑aligned by default (`--center-title` to center the title; wangEditor accepts both);
- faithfully preserves source structure (does **not** turn lists into tables);
- pure Python stdlib — **no python-docx or any dependency needed**.

### When to use it
- Legal/compliance/product folks maintaining **privacy policies, user/service agreements, data‑collection lists, third‑party SDK lists, permission lists** in Word, who must publish into a wangEditor back‑office box.
- Any "Word → wangEditor paste loses formatting / goes plain / centers everything" situation.
- Any **wangEditor‑based** rich‑text editor (this targets the framework, not one product).

### Install
```text
/plugin marketplace add naisi-alibaba/docx-to-wangeditor-html
/plugin install docx-to-wangeditor-html@docx-to-wangeditor
/reload-plugins
```

### Use
Just tell Claude Code: *"Convert these Word docs to HTML I can paste into the wangEditor box."* Or run the script:
```bash
# one file
py "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/docx2wangeditor.py" "C:/path/agreement.docx"
# a folder (skips ~$ Word lock files); add --center-title to center the title
py "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/docx2wangeditor.py" "C:/path/folder"
```

### Output (two files per .docx)
- **`<name>.html`** — full page. **Open in a browser → `Ctrl+A` → `Ctrl+C` → paste into the editor** (primary).
- `<name>_fragment.html` — body‑only HTML, for fields that take raw HTML source.

### Verify against a live editor (optional)
```bash
npx --yes playwright@1.61 install chromium
PWPATH=$(find "$(npm config get cache)/_npx" -maxdepth 3 -name playwright -type d -path '*node_modules*' | head -1)
NODE_PATH=$(dirname "$PWPATH") node "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/validate_paste.js" \
  "<editor-page-url>" "C:/path/agreement.html"
```
A headed Chromium opens; log in once (session persists in `C:/tmp/oms_profile`, override with `OMS_PROFILE`). It pastes each file and prints `PASS` (headings/bold present, no flatten) or `FAIL`. To find a culprit, bisect the body by blocks and paste subsets — the offender is usually a paragraph with a URL.

### FAQ
- **Does de‑scheming the URL change the content?** A necessary trade‑off so the paste doesn't crash; `account.example.com` is still readable, and you can re‑add `https://` by hand in the editor for that one line if required.
- **Why not make lists into tables?** Faithful structure is intentional; ask explicitly if you want tables.
- **Headless can't open the editor?** Such back‑offices gate on permissions; use headed mode and log in once (the script defaults to headed).
- **Images?** Embedded Word images are not exported (policy docs rarely have any).

### Limitations
- Tuned for **wangEditor v4** paste behavior; other editors (TinyMCE/CKEditor/Quill) differ and may not apply.
- Handles `.docx` only (not legacy `.doc`).

---

## License
MIT
