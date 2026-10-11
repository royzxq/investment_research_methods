# 期货 v3 配套流程同步

日期：2026-10-11（Asia/Shanghai）；generator=codex。性质：用户已授权 T / V 重构的配套维护，不是当期市场研究、执行审计或收益验证。

## 实际修改

- 三阶段项目说明改用 T（trend）/ V（economic_reversion）及 G1–G6；五品种扫描、M/RB 双向重点、SR/CF 常驻次级。移除旧 A–H 独立机制、加权评分、隔夜分数、旧 B 窗口与 D8 必查链；参数与风控公式仍只引用 canonical。
- 执行诊断明确 T 不设 TP/净R门，V 须经济锚与收敛机制；账户后置、必要 unknown 与已核 fail 分列。历史 schema 3 不改写为新模型结果，旧影子引擎仅处理兼容历史计划，新 T / V 前瞻登记与人工轨迹审计分开记录。
- [futures-weekly-review](../../../../.agents/skills/futures-weekly-review/SKILL.md) 增加 direct 入口。用户明确要求设计实施时直接保存 maintenance 实施记录并完成必要联动，无需伪造周报或 update_needed；单阶段与发布边界保留。行情未重跑就不宣称已有当前信号。
- [framework-condense](../../../../.agents/skills/framework-condense/SKILL.md) 按新 canonical 与迁移记录核对新 compact；已退休规则不因旧编号或解除条件被重新补回。股票的评分、编号及保真要求不变。
- 原“维持最近一至两周方向”的反摇摆措辞改为方法稳定性：按既定模型正常触发、退出或出现反向候选不要求先改框架，不用上周观点覆盖本周信号。

本说明涉及 10 份项目/技能文档。canonical、compact、数据协议、审计模板、数值工具与迁移登记由同一重构任务的其他部分同步，本文不保存其第二套定义。

## 验证

以下均已实际运行并通过：

```text
python3 /Users/xinquanzhou/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/futures-weekly-review
python3 /Users/xinquanzhou/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/framework-condense
git diff --check -- <本说明列出的项目和技能路径>
```

10 份文档的 6 条 Markdown 相对文件链接检查通过。人工顺序推演覆盖：只研究不写交易计划；compare 无更新仍留诊断；adapt 单阶段不自动发布；direct 两版重构可做必要同步但不伪造市场重评；T 缺 TP 不算缺项；历史 A–H 分类仅作背景、不恢复旧门；股票 compact 不套期货迁移例外。

以上是技能结构、链接与流程边界核验；未运行真实行情 API、策略回测或模拟成交，不证明经济假设有效，也不授予执行权限。未提交、推送或发布。
