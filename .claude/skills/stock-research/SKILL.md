---
name: stock-research
description: 按本仓股票框架研究或复评单只 A 股、港股，自动取证并计算价格地图，保存完整报告及轻量价格地图与监控变量 JSON。用于个股调研、价格地图和复评。
---

# Claude 兼容入口

自然语言“使用进行股票投研：<股票信息>”进入下述完整流程。本宿主生成端固定为 `claude`；执行共享技能时传 `--generator claude`，新报告和 JSON 使用 `-claude` 后缀，JSON 写入 `meta.generator="claude"`，latest 也按生成端独立保存。

本技能的完整指令维护在仓库根目录下的 `.agents/skills/stock-research/SKILL.md`。先定位包含 `framework/` 和 `research/` 的仓库根目录，读取并执行该文件及其引用的必要 reference；相对 reference 路径按目标技能目录解析。

本文件仅负责 Claude 技能发现，不维护独立规则或 JSON schema。使用当前环境实际可用的代理与检索工具；无需调用名为 `Skill` 的工具才能执行被引用技能。
