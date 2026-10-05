---
name: deep-research-auto
description: 自动组织多代理跨来源取证、裁决关键冲突并保存深度研究报告与笔记；用于独立深度调研或作为 stock-research 的研究后端。
---

# Claude 兼容入口

本技能的完整指令维护在仓库根目录下的 `.agents/skills/deep-research-auto/SKILL.md`。先定位包含 `framework/` 和 `research/` 的仓库根目录，读取并执行该文件及其引用的必要 reference；相对 reference 路径按目标技能目录解析。

本文件仅负责 Claude 技能发现，不维护独立规则或 JSON schema。使用当前环境实际可用的代理与检索工具；无需调用名为 `Skill` 的工具才能执行被引用技能。
