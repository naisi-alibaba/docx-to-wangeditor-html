---
name: convert
description: Convert Word (.docx) documents into clean semantic HTML that pastes correctly into a wangEditor v4 rich-text editor (contenteditable .w-e-text). Use when a user wants to put a Word doc (privacy policy / service agreement / any policy or list) into a wangEditor-based admin editor — e.g. the stepos OMS protocol editor — or complains that pasting loses formatting / headings vanish / bold disappears / the whole text flattens to plain text / everything becomes centered. 把 Word 文档转成可直接粘进 wangEditor 富文本编辑器的干净 HTML；当用户要把 Word（隐私政策/服务协议/各类清单）放进基于 wangEditor 的后台编辑框（如 stepos OMS 协议编辑器），或抱怨粘贴后格式丢失/标题不见/加粗没了/整篇变纯文本/全文居中时使用。
---

# Word (.docx) → wangEditor-safe HTML

Convert Word documents into HTML that survives a copy-paste into a **wangEditor**
rich-text editor without losing formatting.

## The target framework: wangEditor (not any specific product)

The editor is **wangEditor v4** — a `contenteditable` `<div class="w-e-text">` rich
text editor used by many Chinese SaaS admin panels. (The stepos OMS protocol editor
at `oms.stepos.com/protocolMange/appVersionLayout` is one instance; this skill is
not tied to it.) Its paste pipeline has two behaviors that define what input it needs:

1. **It strips inline `style` attributes but keeps tags**, then renders
   `h1/h2/h3/strong/table` with its own CSS. → So the required input is **clean
   SEMANTIC HTML**: headings as `<h1>/<h2>/<h3>`, emphasis as `<strong>`, tables as
   `<table>`. Produce that, open it in a browser, **Ctrl+A → Ctrl+C → paste**; tags
   survive and render styled.

2. **Any `http(s)://` URL crashes the paste.** wangEditor auto-links URLs; when a URL
   is glued to following CJK text (common in Word, e.g. `访问https://x.com/完成…` with
   no space) the auto-link mangles, `insertHTML` fails, and the **entire document
   collapses into one `<p>` + many `<br>`** (all headings/bold lost). A space does NOT
   help. → Required fix: render URLs **without the `http(s)://` scheme** and **without
   `<a>`** (e.g. `x.com/…`). The converter does this automatically.

> A document with no URLs never triggers #2 — that's why URL-free docs always paste fine.

## Usage

Conversion (pure-stdlib Python, no python-docx needed):

```bash
# single file
py "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/docx2wangeditor.py" "C:/path/服务协议.docx"
# a whole folder (skips ~$ Word lock files)
py "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/docx2wangeditor.py" "C:/path/to/folder"
```

Outputs, next to each `.docx`:
- `<name>.html` — full page. **Open in browser → Ctrl+A → Ctrl+C → paste into the editor** (primary).
- `<name>_fragment.html` — body-only HTML (for fields that take raw HTML source).

Conversion rules: headings by Word outline level → h1/h2/h3; `版本：`/`发布时间：` → small
meta lines; bold → `<strong>`; Word tables → `<table>`; URLs de-schemed; everything
left-aligned by default (`--center-title` centers the title — wangEditor accepts both).
**Preserve the source structure faithfully; do NOT restructure lists into tables unless asked.**

## Validate (optional, but do it whenever output is doubted)

You cannot tell from the HTML alone whether it will paste cleanly — verify against a real
editor with `scripts/validate_paste.js` (Playwright):

```bash
npx --yes playwright@1.61 install chromium                       # once
PWPATH=$(find "$(npm config get cache)/_npx" -maxdepth 3 -name playwright -type d -path '*node_modules*' | head -1)
NODE_PATH=$(dirname "$PWPATH") node "${CLAUDE_PLUGIN_ROOT}/skills/convert/scripts/validate_paste.js" \
  "<editor-url>" "C:/path/服务协议.html" "C:/path/其他.html"
```

A headed Chromium opens; **log in once** (session persists in `C:/tmp/oms_profile`, override
with `OMS_PROFILE`). It pastes each file into the editor and prints `PASS` (`br<5` and
headings/bold present) or `FAIL` (flattened). To locate a trigger, bisect the body by
blocks and paste each subset — the offender is usually a paragraph containing a URL.
