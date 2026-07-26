---
name: kaixin-3d-anime-cover
description: 开心3d动漫封面。Create publish-ready Chinese 3D anime-style AI/tool/cloud/B2B covers for Xiaohongshu, Douyin, and WeChat Channels. Use when a user wants a finished cover or redesign and provides content, a topic, or a cover title; a title-only input must be researched before design. For a long title, propose a layout-safe short title and ask the user to choose it or retain the original before design. Generate only with built-in image generation, integrate the selected title as a 3D sign in the scene, and confirm visual assets before creating a character or scene. Not for logo design, title ideation without cover production, or prompt-only requests.
---

# 开心3d动漫封面

交付可发布封面，不把生图提示词当最终交付。

## 工作流

1. 识别任务输入。脚本、文章、链接、产品话题和“要做封面的标题”都可触发；仅要求想标题且明确不要制作封面时不触发。若只给标题或标题缺少产品/事件上下文，先用 `aihot` 搜索标题所指的近期 AI 产品或事件；若没有可靠结果，向用户索要链接、脚本或一句背景说明。不得凭空补全事实。
2. 锁定标题，未锁定前不得设计场景。先判断标题是否超过排版安全长度：中文主标题超过 8 个字、或在手机缩略图中无法舒适排进两行，都算长标题。长标题即使由用户明确给出，也必须先基于原题和文案提炼 1 个推荐封面短标题，建议 3–6 个汉字、最多 8 个，然后明确询问用户“保留原标题”还是“使用提炼标题”；用户选择前不得进入素材确认、场景、提示词或出图。用户选保留原标题后，逐字保留完整标题，不得缩写、改写或漏字；用户选提炼标题后，必须使用被确认的短标题。未给标题时，基于内容给 3 个候选，并询问用户是否满意、是否要继续改。
3. 标题确认后，先确认人物、产品/网页截图、真实 Logo、品牌色和满意样张；这些素材未确认前，不得进入角色、场景、提示词或出图。用户提供人物照片时，只将其用于当前任务的身份一致性参考；不得将照片保存、复用或当作其他用户的默认素材。用户要求“用真人”但未提供照片时，说明需要其上传参考照片；仍须确认截图、Logo、品牌色和样张。真实 Logo、产品图、UI 必须后期合成，不能让模型重绘。
4. 用户明确没有人物真实照片时，说明无法保证真人身份相似；若用户也未指定人物设定，可用非特定角色作保底。不得在用户尚未答复素材问题时，擅自默认特定脸型、眼镜或其他身份特征。
5. 仅在“标题已确认 + 素材已确认或明确缺失”后，读取 [风格指南](references/style-guide.md)、[人物与字体系统](references/typography-and-portrait.md) 与 [当前设计流程](references/design-flow.md)；若目标是大头短视频爆款图，读取 [爆款大头标准](references/viral-avatar-thumbnail.md)，并参考 `assets/approved-typography/` 中的已确认正确排版样张。再定“产品功能 + 角色职业 + 世界场景 + 一秒剧情”、构图系统、字体角色、颜色和文字-人物关系。
6. 人像先保身份，再做角色化与商业化处理；爆款大头模式必须真实脸部 + 非写实小身体 + 强表情 + 荒诞剧情，并直接生成“图文一体”的同款 3D 招牌字封面。每版先写出“角色职业 + 世界场景 + 可见转化事件 + 最终结果”四项；缺任一项不得生成。
7. 普通商单封面可用 `scripts/compose_cover.py` 后期叠加中文、证据数字、kicker、副标题和真实 Logo；爆款大头封面不得用脚本 `--treatment blast` 的后期标题当成品，必须按已确认满意样张生成顶部一体化大标题。
8. 以手机缩略图检查标题、眼神、手部、Logo、事实准确性、版式安全区与平台裁切；失败就重做。默认交付 3 张构图、主色、动作和标题版式均有明显区别的成品。

## 生成引擎与标题验收

- 只用内置 `image_gen` 生成或编辑封面。不得调用 `bl`、Bailian CLI、百炼模型或其他外部生图请求；内置生成失败时如实报告，不换引擎绕过。
- 用户选择的最终封面标题必须逐字进入每张正式成品；生成后逐张核对每个汉字和标点。标题有漏字、错字、乱码、被裁切或没有按用户选项使用时，直接判失败并重做。
- 标题必须是场景内的 3D 招牌物件，而非平贴在顶部：写清它与门洞、透视、道具、人物或主光的物理关系，并要求环境光、投影、遮挡和透视同时作用于标题。不得生成孤立的平面大字或独立标题条。
- 场景必须让用户一眼看懂“输入是什么、发生了什么、结果是什么”。禁止只给玩具工厂、扫描室、3D 打印机或手办做静态陈列；必须加入明确的转化动作、冲突或结果瞬间。

## 人物规则

- 用户提供人物照片时，仅在当前任务中以其为身份锚点，核对脸型、五官比例、肤色、发型、眼镜和年龄感；可换表情、服装、姿势与光影，不得改身份。不得把照片保存为默认参考，也不得用于后续任务或其他用户。
- 人物必须参与叙事，不只是讲解员；短视频爆款模式必须真实脸部 + 非写实小身体 + 强表情 + 荒诞剧情。写实半身照直接判失败。
- 爆款大头模式的人物不能过度卡通化：有参考照片时脸要像该照片中的人物，保留照片可见的身份特征；身体才做 3D 软胶、纸雕、玩具、木偶等非写实角色。无照片时使用用户指定设定，或在用户明确无照片且未指定设定后，使用非特定角色。若“有趣”以牺牲已提供人脸的识别为代价，判失败并重做。

## 字体与版式规则

普通后期叠字只使用 `assets/fonts/` 中随 Skill 保存许可证的字体，或用户提供且授权明确的字体。爆款大头封面默认执行参考图同款生成式招牌字，不受本地字体限制；本地脚本标题只用于普通商单或临时草稿。具体选择与表现规则见 [人物与字体系统](references/typography-and-portrait.md)。

- 字体最多三种并严格分工：优设标题黑做主标题，思源黑体做信息层，得意黑做短标签。
- 有真实数据、数量、步骤或时长时，普通商单可用 `--metric` 做 1–4 字证据锤；爆款大头图的证据章也应融入生成式招牌字体系，不再使用脚本 `--treatment blast` 作为正式标题。

## 默认视觉规则

- 背景必须参与叙事；不要只做机房、渐变或粒子特效。连续三版不得同背景、同主色、同动作或同标题版式。
- 爆款大头封面不得连续停留在办公室、机房或数据面板。优先使用能形成记忆点的世界场景：户外、山顶、野地、太空、城市、长城、魔法学院、金字塔、学校、宇宙、竞技场、工厂、超市、片场、实验室等；场景必须服务产品功能隐喻，不能只是换背景。
- “玩具工厂”“扫描室”“3D 打印机”只能作为叙事道具，不得单独充当场景；每张还必须有独立的大世界、可见转化事件和明确结果。
- 小红书、抖音、视频号封面统一默认 3:4；不要因参考图是长竖版而生成 9:16。真实 Logo 预留位置后合成。

## 叠字命令

```bash
python3 scripts/compose_cover.py \
  --input /absolute/path/visual.png \
  --output /absolute/path/cover.png \
  --headline "流量费省18倍" \
  --subhead "AIGC出海成本" \
  --subhead-tracking 8 \
  --style editorial \
  --layout poster \
  --treatment outline \
  --kicker "成本优化" \
  --metric "18倍" \
  --metric-label "出网成本" \
  --metric-position right \
  --metric-color "#FF6B6B" \
  --accent-color "#40E0D0" \
  --platform xhs
```

字体角色：`variety`、`comic`、`tech`、`round`、`editorial`。版式：`top`、`split`、`side`、`ribbon`、`poster`。表现：`outline`、`sticker`、`blast`；其中 `blast` 仅可用于普通封面草稿或非爆款备选，不得用于爆款大头正式交付。`--font` 只能传入授权已核验的本地字体路径。
若有已抠好的透明人物 PNG，可追加 `--foreground /absolute/path/person.png --foreground-anchor right --foreground-scale 0.54`，让人物压在部分标题或证据数字前方。

## 交付标准

- 后续每一张同类爆款大头封面，质量不得低于已确认满意样张；若人物不够有趣、剧情不够秒懂、标题不够炸或脸部身份不稳，不能当成品交付，必须重做或标为备用。
- 正式交付前逐张放大核对：用户确认标题是否逐字完整、标题是否与透视/光影/道具融合、是否能在 1 秒内说出“输入、转化、结果”。任一项否定，必须重做。
- 默认交付 3 个明显不同的成品图和各自的最终标题；仅在用户要求时附生图提示词。
- 输出到用户指定目录；未指定时在当前工作目录创建 `cover-output/`。
- 最终答复展示成品图并给出绝对路径。
- 用 [触发边界用例](evals/trigger_cases.json) 和 [输出合同用例](evals/output/cases.jsonl) 做回归检查。
