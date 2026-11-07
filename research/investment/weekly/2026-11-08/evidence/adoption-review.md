# 采纳、部署与纠错接续核验

研究日2026-11-08，generator=codex。独立工作区`/private/tmp/investment-weekly-automation-2-2026-11-08`，初始origin/main `842aa08`。原项目仅只读核查公司产物，不带入dev分支未发布提交。维护入口、meta/change新要求与scripts/investment_maintenance.py均已部署，deployment_pending=false。

R22由用户2026-11-06明确采纳，PR #61于2026-11-06T15:25:15Z合并，提交`949d020af04ba55e68cbeacada91099cc960d104`；当前main两份正文与11/6-r3冻结副本逐字哈希相同。实际方法`stock-two-price-controls-v2-etf-relative-v1`。本期生成前helper选择11/6-r3，并核验报告来源哈希、日期及双方法兼容性；旧报告单独自述不作采纳凭证。此前PR #58已合并。无需首次桥接。

- canonical sha256 `10a8cb94f5288b7340589a469d1f57c71bdf0fc07346a4d2b2ab0185227edab0`，method_sha256 `09a175947d764b73e4822d6be2af80020a392330b5ff1e5af845cd42359a50d4`。
- compact sha256 `071ab7d37d6d11b073cdbb0b5de3f6be9445af2ede5519a7264e1b7378831040`，method_sha256 `f78fc877aa3e3093727dc7b31786ffdcb6d61d6aacd5d5d02286a3ce16c740e8`。
- 上期市场完整报告11/1，SHA256 `ef4ebfa14638d9ebf68957d5a306905510ddda98fc38612973fd5180c732fb89`；方法变化完整报告11/6-r2，SHA256 `91aeeaf4c30a199c0d24df99e5f5f9c37e9b790abd5d97b6d2ee4bd9447d273a`。二者角色不同；无期货/ETF/公司报告混入市场基线。

## 纠错与撤回

本期直接对照11/1 calculations.latest_window、报告及旧handoff正文发现R21.window不一致：应为10/28—30，却写10/21—23；11/6-r2/r3沿袭。撤回这三个有错状态包作为后续可消费证据，用11/8 adopted handoff明确supersede。旧正文保留，旧方法真实采纳事实与不可变方法副本不撤回。纠错不把历史10/28—30改称本周窗口，也不改变当时退出未满足结论。其余旧有效规则和五项pending逐条带入，10/11错误变化报告的withdrawn_sources继续携带。继承的reviews.methods记录历史方法来源，与当前R22不同，已去除含混的“仅观测字节差”注记；不伪造公司兼容审查。

本次授权允许采用现行方法下的state_refresh/evidence_correction并发布main。当前canonical/compact原位观测块仍须单一PR人工审核；本期不提新方法，方法指纹相同也不绕过正文PR。若将来方法PR真正合并，须新adopted记录绑定实际正文；不得重写本记录。

## 待逐股复评

五证券保留原触发日及pending，completed=0，账户null。恒瑞11/5 Codex报告/JSON实际存在，见completion-inventory；已有研究不等于本事项及R22兼容验收完成。不得自动启动公司批次，不重置168小时冷却。新元研究只提供取证线索；事实足够可估值并给冻结观察P1/T1，买入限制按实际scope保持。
