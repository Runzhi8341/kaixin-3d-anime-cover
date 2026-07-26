# 开心 3D 动漫封面

> 把 AI、工具、云服务与 B2B 主题，做成一眼想点开的中文 3D 动漫视觉封面。

<p align="center">
  <img src="assets/approved-typography/01-Codex解锁-长城代码守关-v3-原图.png" width="18%" alt="Codex 封面示例" />
  <img src="assets/approved-typography/02-Mindwalk代码地图-金字塔考古-v3-原图.png" width="18%" alt="Mindwalk 封面示例" />
  <img src="assets/approved-typography/03-MeshLLM-GPU组队-山顶算力基站-v3-原图.png" width="18%" alt="MeshLLM 封面示例" />
  <img src="assets/approved-typography/04-Flint-AI画图表-魔法学院-v3-原图.png" width="18%" alt="Flint 封面示例" />
  <img src="assets/approved-typography/05-Perplexity额度看板-城市天台侦探-v3-原图.png" width="18%" alt="Perplexity 封面示例" />
</p>

<p align="center">
  <strong>适用于小红书 · 抖音 · 视频号</strong><br />
  从选题、标题提炼、画面构图到中文排版，一次完成可发布封面。
</p>

---

## 它能做什么

| 你想要的结果 | 这个技能会交付 |
| --- | --- |
| AI 产品、工具测评或行业热点封面 | 主题化 3D 动漫场景与高辨识度角色 |
| 看起来很长、很难排的中文标题 | 先给可读性更强的标题提炼方案，再按你的选择排版 |
| 使用人物照片制作封面 | 仅使用你为本次任务提供的照片，保持人物一致性 |
| 已有封面但不够吸睛 | 保留核心信息，重新设计视觉叙事、层级和标题冲击力 |

## 一句话开始

在 Codex 中直接说：

```text
使用 $kaixin-3d-anime-cover，做一张 3:4 的小红书封面。
标题：AI 时代，普通人如何把工作效率翻三倍？
```

也可以更自然地表达：

```text
帮我做一张开心风格的 3D 动漫封面，主题是「Claude Code 到底值不值得学？」
```

## 设计语言

- **3D 动漫叙事**：不做抽象的“科技背景”，而是为主题设计可讲故事的角色、动作与场景。
- **中文标题优先**：保证标题是画面的第一阅读入口，避免小字、乱码和无效堆砌。
- **强内容平台适配**：默认面向 3:4 竖版信息流，在小屏上依然有冲击力。
- **人物参考受控**：只有你在当前任务提供或明确授权的照片才会用于人物一致性参考，不保存为默认素材。

## 技能内容

| 目录 | 用途 |
| --- | --- |
| `SKILL.md` | 技能触发条件与完整制作流程 |
| `references/` | 画面、排版与设计流程指南 |
| `scripts/compose_cover.py` | 稳定生成中文标题排版的工具 |
| `assets/` | 已确认排版样张与可用字体资源 |
| `evals/` | 触发与交付质量的回归用例 |

## 使用边界

这个技能面向“完成一张可发布封面”或“重做现有封面”。它不用于纯 Logo、只有一句标题的简单文字需求，或仅输出提示词的场景。

---

<p align="center">
  <strong>让每个好选题，都有一张配得上的封面。</strong>
</p>
