# docx-to-wangeditor-html

> 把 Word(.docx)协议/政策文档转成"粘进 **wangEditor** 富文本编辑框后格式不丢"的 HTML。
> Convert Word (.docx) docs into HTML that survives a paste into a **wangEditor** rich-text editor.

这是一个 Claude Code 插件。完整的功能说明、问题背景、根因分析、使用方法与中英文文档，见：
This repo is a Claude Code plugin. For the full write-up (what it's for, the problem it solves,
root cause, usage) see the plugin README:

➡️ **[plugins/docx-to-wangeditor-html/README.md](plugins/docx-to-wangeditor-html/README.md)**

## 安装 / Install
```text
/plugin marketplace add naisi-alibaba/docx-to-wangeditor-html
/plugin install docx-to-wangeditor-html@docx-to-wangeditor
/reload-plugins
```
（也可本地安装 / or add a local path: `/plugin marketplace add E:/step工作坊/docx-to-wangeditor-html`）

## 它解决什么 / What it solves（30 秒版）
把 Word 文档粘进基于 **wangEditor** 的后台编辑框时，常常排版乱、标题与加粗丢失、甚至**整篇塌成纯文本**。
根因：wangEditor 粘贴时**只认标签不认内联样式**，且会被内容里的 **`http(s)://` 网址自动链接搞崩**、把整篇降级成纯文本。
本工具把 `.docx` 转成**干净语义化 HTML 并给网址去 scheme**，从而粘贴后格式完整保留。

Pasting Word into a **wangEditor** box often loses formatting or flattens the whole doc to plain text.
Why: wangEditor keeps tags but strips inline styles, and **chokes on `http(s)://` auto-linking**.
This tool emits **clean semantic HTML with de-schemed URLs**, so formatting survives the paste.

## License
MIT
