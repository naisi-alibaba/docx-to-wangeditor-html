# DOCX → wangEditor HTML

Convert Word (`.docx`) documents into clean **semantic HTML** that pastes correctly into a
**wangEditor** rich-text editor — preserving headings, bold, and tables, and working around
wangEditor's URL-autolink bug that otherwise flattens the whole document into plain text.

> **About the editor:** wangEditor (v4) is a `contenteditable` rich-text editor
> (`<div class="w-e-text">`) used by many admin panels. This skill targets the *framework*,
> not any one product. The stepos OMS protocol editor is just one real-world instance.

---

## English

### What it does
- Reads a `.docx` with **no external dependencies** (pure Python stdlib — no `python-docx`).
- Emits **clean semantic HTML**: `<h1>/<h2>/<h3>` by Word outline level, `<strong>` for bold,
  `<table>` for Word tables, small meta lines for `版本：`/`发布时间：`.
- **De-schemes URLs** (`https://x.com/…` → `x.com/…`, no `<a>`). This is the critical fix:
  wangEditor auto-links `http(s)://` URLs on paste, and a URL glued to CJK text makes its
  `insertHTML` fail — collapsing the **entire** document into one paragraph of plain text.
- Faithfully preserves the source structure (does **not** turn lists into tables).

### When to use it (scenarios)
- You maintain legal/policy text (privacy policy, user/service agreement, data-collection
  list, third-party SDK list, permission list) in Word and must paste it into a wangEditor
  admin/CMS box.
- Pasting straight from Word looks messy, or pasting a rendered HTML page **loses all
  formatting / flattens to plain text / centers everything**.
- Any wangEditor-backed editor where pasted rich content silently loses headings & bold.

### Install
```text
/plugin marketplace add <your-git-repo-or-path>
/plugin install docx-to-wangeditor-html@step-skills
/reload-plugins
```

### Use
Ask Claude Code: *"Convert these Word docs to HTML I can paste into the wangEditor box,"*
or run directly:
```bash
# one file
py "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/docx2wangeditor.py" "C:/path/agreement.docx"
# a folder (skips ~$ Word lock files); add --center-title to center the title
py "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/docx2wangeditor.py" "C:/path/folder"
```
Each `.docx` produces `<name>.html` (open in a browser → **Ctrl+A → Ctrl+C → paste**) and
`<name>_fragment.html` (body-only, for raw-HTML fields).

### Verify against a real editor (optional)
```bash
npx --yes playwright@1.61 install chromium
PWPATH=$(find "$(npm config get cache)/_npx" -maxdepth 3 -name playwright -type d -path '*node_modules*' | head -1)
NODE_PATH=$(dirname "$PWPATH") node "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/validate_paste.js" \
  "<editor-url>" "C:/path/agreement.html"
```
A browser opens; log in once. It pastes each file and prints `PASS`/`FAIL` (FAIL = flattened).

### Why pasting from Word/HTML usually fails
| Symptom | Cause | This skill's fix |
|---|---|---|
| Pasted text is messy | Word injects junk inline styles | Emit clean semantic tags only |
| Headings/bold disappear, looks plain | wangEditor strips inline styles, keeps tags | Use real `<h*>`/`<strong>` tags (rendered by editor CSS) |
| **Whole doc becomes one block of plain text** | wangEditor auto-links a `http(s)://` URL and `insertHTML` crashes | **De-scheme URLs** (no `http(s)://`, no `<a>`) |
| Everything centered, uneditable | a centered first block + the flatten above | Left-align; remove the flatten cause |

---

## 中文

### 这个技能做什么
- 读取 `.docx`，**零外部依赖**（纯 Python 标准库，无需 `python-docx`）。
- 产出**干净的语义化 HTML**：按 Word 大纲级别生成 `<h1>/<h2>/<h3>`，加粗用 `<strong>`，
  Word 表格转 `<table>`，`版本：`/`发布时间：` 作居中小字。
- **去掉 URL 的 scheme**（`https://x.com/…` → `x.com/…`，且不包 `<a>`）。这是关键修复：
  wangEditor 粘贴时会自动把 `http(s)://` 网址转成链接，而网址紧贴中文会导致它的
  `insertHTML` 失败，**整篇文档塌成一段纯文本**（标题/加粗全没）。
- 忠实保留原文结构（**不**擅自把清单改成表格）。

### 使用场景
- 用 Word 维护法务/政策文本（隐私政策、用户/服务协议、个人信息收集清单、第三方 SDK 共享
  清单、权限清单），需要粘进基于 wangEditor 的后台/CMS 编辑框。
- 直接从 Word 粘贴很乱，或粘贴浏览器渲染页后**格式全丢/变纯文本/整篇居中**。
- 任何用 wangEditor 的编辑器，粘贴富文本后标题与加粗悄悄丢失。

### 安装
```text
/plugin marketplace add <你的-git-仓库或路径>
/plugin install docx-to-wangeditor-html@step-skills
/reload-plugins
```

### 使用
对 Claude Code 说：**“把这些 Word 转成能粘进 wangEditor 编辑框的 HTML”**，或直接运行：
```bash
# 单个文件
py "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/docx2wangeditor.py" "C:/路径/服务协议.docx"
# 整个目录（自动跳过 ~$ Word 锁文件）；加 --center-title 让标题居中
py "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/docx2wangeditor.py" "C:/路径/目录"
```
每个 `.docx` 生成 `<name>.html`（浏览器打开 → **Ctrl+A → Ctrl+C → 粘贴**）和
`<name>_fragment.html`（仅 body，给要填 HTML 源码的字段用）。

### 在真实编辑器里验证（可选）
```bash
npx --yes playwright@1.61 install chromium
PWPATH=$(find "$(npm config get cache)/_npx" -maxdepth 3 -name playwright -type d -path '*node_modules*' | head -1)
NODE_PATH=$(dirname "$PWPATH") node "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/validate_paste.js" \
  "<编辑器URL>" "C:/路径/服务协议.html"
```
会弹出浏览器，登录一次；逐个粘贴并输出 `PASS`/`FAIL`（FAIL = 塌成纯文本）。

### 为什么从 Word/HTML 直接粘贴通常会失败
| 现象 | 原因 | 本技能的修复 |
|---|---|---|
| 粘进去很乱 | Word 带入大量垃圾内联样式 | 只输出干净语义标签 |
| 标题/加粗消失、像纯文本 | wangEditor 剥离内联样式、只保留标签 | 用真正的 `<h*>`/`<strong>` 标签（由编辑器 CSS 渲染） |
| **整篇变成一坨纯文本** | wangEditor 自动给 `http(s)://` 网址加链接导致 `insertHTML` 崩溃 | **给 URL 去 scheme**（不带 `http(s)://`、不包 `<a>`） |
| 全文居中、改不动 | 居中的首块 + 上面的塌陷 | 全部左对齐；消除塌陷根因 |

---

## License
MIT
