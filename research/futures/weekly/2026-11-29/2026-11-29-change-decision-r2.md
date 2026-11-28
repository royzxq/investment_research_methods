# 期货变化判定 · 2026-11-29

**刷新状态，无新增证据纠错，无方法变更。** 比较基线由严格早于本期的 main handoff 取11/22市场r2。上期五T均未触发，本期RB收盘越过上沿。11/23旧空备选假设触及时间退出边界，期货价格反向并未改变它的原期限。本期判断与前期产业比较、风险覆盖及恢复条件见[市场周报](2026-11-29-market-research.md)。无规则定义缺陷或固定版本行为偏差需要适配。单周收益无法核实。

```json
{
  "AS_OF_DATE": "2026-11-29",
  "generator": "codex",
  "CHANGE_CLASSIFICATION": {
    "state_refresh_needed": "yes",
    "evidence_correction_needed": "no",
    "method_change_needed": "no"
  },
  "FRAMEWORK_UPDATE_DECISION": {
    "update_needed": "no",
    "update_level": "none",
    "reason": "已有规则区分短暂突破、弱产业支持和不可承受的单位压力，旧计划的日期边界亦可按真实日历复核。"
  },
  "KEY_VARIABLE_CHANGES": [
    "RB旧空两条时间上限均已过；11/27收盘产生独立新多信号。",
    "豆粕压榨回升，螺纹复产快于表需，甲醇港库增加，11/30旧糖仓单到期。"
  ],
  "STATE_REFRESH": [
    "四项旧案、五T、三V与两准备对、50个合约日风控。",
    "RB新观察留原钟至12/1，本次压力情景不新开。"
  ],
  "EVIDENCE_CORRECTIONS": {
    "new": [],
    "inherited_groups": 25,
    "source": "research/futures/weekly/2026-11-29/evidence/continuity-review.json"
  },
  "DATA_FEASIBILITY": {
    "available": [
      "五T、三当前V双腿结算、50行周度公开风控"
    ],
    "temporary_gap": [
      "MA准备对缺13日，大商所逐日官方原表，未来盘口、当日账户、MA/SR精确最后日冲突"
    ],
    "research_only": [
      "跨月全成本和可实现经济区间"
    ]
  },
  "UPDATE_FOCUS": [],
  "DO_NOT_OVERREACT_ITEMS": [
    "不以单周突破/放弃入场推断收益或调整参数。"
  ],
  "EXECUTION_AUDIT": {
    "path": "research/futures/weekly/2026-11-29/2026-11-29-execution-audit-r2.md",
    "coverage": "partial",
    "framework_version": "v3.0",
    "active_scope": [
      "五T，四旧处置"
    ],
    "research_only_scope": [
      "三V观察"
    ],
    "summary": "四T未触发；新RB多头压力超线；未评估市场总体机会数。"
  }
}
```
