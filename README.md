# Machining Paper PDF Translator

面向机械加工、激光制造与先进制造论文的中文保版翻译 Skill。

它要求在翻译全文的同时尽量保持原 PDF 的页数、页面尺寸、单双栏结构、图表位置、公式、数据、比例尺和图内标注，并在交付前完成结构审计与逐页视觉检查。

## 主要能力

- 统一机械加工、激光加工和材料表征专业术语
- 按原页面坐标回填中文，保持图文一一对应
- 翻译图题、表题、表头、图例、坐标轴和可识别图内标签
- 保护公式、变量、数值、单位、样品编号、DOI 和引用编号
- 保留参考文献著录信息，确保论文仍可检索
- 检查字体嵌入、缺字、文本溢出和图表遮挡
- 自动比较源 PDF 与译文 PDF 的页数、页面几何、旋转和图片对象数量

## 安装

将本仓库克隆到 Codex 的 Skills 目录：

```bash
git clone https://github.com/ynshu832-del/machining-paper-pdf-translator.git \
  ~/.codex/skills/machining-paper-pdf-translator
```

重新打开会话后即可自动匹配相关任务，也可以显式调用：

```text
使用 $machining-paper-pdf-translator 将这篇英文机械加工论文翻译为中文，
保持原版式、图表、公式和图内标注位置，最终输出 PDF。
```

## 目录结构

```text
machining-paper-pdf-translator/
├── SKILL.md
├── agents/openai.yaml
├── assets/icon.svg
├── references/
│   ├── workflow.md
│   ├── terminology.md
│   └── qa-checklist.md
└── scripts/pdf_invariant_audit.py
```

## PDF 结构审计

审计脚本依赖 PyMuPDF：

```bash
python -m pip install -r requirements.txt
python scripts/pdf_invariant_audit.py original.pdf translated.pdf
```

脚本会把页面尺寸或旋转变化判定为错误，把图片对象数量变化、应有中文文本但未检测到中文等情况列为警告。警告必须结合逐页渲染结果人工核验。

## 说明

- 这是翻译与版面质量控制流程，不是绕过 PDF 密码、访问限制或版权限制的工具。
- 无法可靠识别的图内文字应保留原文并明确报告，不应猜译。
- 中文字数通常多于英文缩写形式，因此“保版”以保持页面几何、对象位置和阅读对应关系为目标；必要时可在可读范围内微调字号和行距。

## License

[MIT](LICENSE)

---

An open Codex Skill for translating machining, laser-manufacturing, and advanced-manufacturing papers into professional Chinese while preserving PDF page geometry, figures, tables, equations, numerical data, and in-figure labels. See `SKILL.md` for the operational specification.
