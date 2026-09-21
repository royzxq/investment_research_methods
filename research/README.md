# research/

流水线每周运行的留痕产出，按日期命名：

- `YYYY-MM-DD-market-research.md` — 阶段①（meta future analysis）产出的调研报告
- `YYYY-MM-DD-change-decision.md` — 阶段②（future change analysis）产出的判定结论（是否需要更新框架 + 理由）
- `YYYY-MM-DD-execution-audit.md` — 每周都产出的执行诊断，记录账户核验状态、候选覆盖范围、所有已知否决与缺口；有新版框架时在更新分支内重评并标明拟议版本，不伪装成历史成交。

阶段③（future adaption）的适配报告保存在 `YYYY-MM-DD-adaption-report.md`，其中只记录受影响内容、依据与验证，引用工作区 `framework/futures_framework.md` 的完整正文，不粘贴全文；框架局部修改与脚本/精简版一起走分支和 PR。修订历史由日期报告和 git 保存，不在框架累加历代标记。用户要求定向修复时，报告明确维护范围，不重写既有市场研究来制造更新依据。

股票轨道使用独立的 `investment-` 前缀：`investment-YYYY-MM-DD-market-research.md` 与 `investment-YYYY-MM-DD-change-decision.md` 保存研究与变化判定；需要更新框架时生成 `investment-YYYY-MM-DD-adaption-report.md`，记录局部变更、依据和验证，链接完整框架，不粘全文。当前状态在股票框架原有位置替换，历史脉络保存在这些日期报告和 git 中；变化检测按需回看，首次无历史基线的处理及原提交/PR边界不变。
