# step-skills — Claude Code marketplace

A small marketplace of Claude Code skills for document & rich-text-editor workflows.
文档与富文本编辑器相关的 Claude Code 技能集。

## Add this marketplace / 添加本市场
```text
/plugin marketplace add <this-repo-git-url-or-path>
```
e.g. `/plugin marketplace add yourname/step-skills` (GitHub shorthand) or a local path.

## Plugins / 插件

| Plugin | What it does | 用途 |
|---|---|---|
| [`docx-to-wangeditor-html`](plugins/docx-to-wangeditor-html/) | Convert Word `.docx` into clean HTML that pastes correctly into a **wangEditor** rich-text editor (preserves headings/bold/tables; de-schemes URLs to avoid the paste-flatten bug). | 把 Word 转成可直接粘进 **wangEditor** 富文本编辑框的干净 HTML。 |

Install a plugin / 安装：
```text
/plugin install docx-to-wangeditor-html@step-skills
/reload-plugins
```

## Before publishing / 发布前
1. Edit `owner.name`/`owner.email` in `.claude-plugin/marketplace.json` and the `author`
   fields in each plugin's `.claude-plugin/plugin.json`. 改成你自己的署名/邮箱。
2. Validate: `claude plugin validate .` 校验清单。
3. Push to a git host (GitHub/GitLab). Users then run `/plugin marketplace add <repo>`.
   推到 git 仓库后，别人即可 `/plugin marketplace add <仓库>` 安装。

## License
MIT
