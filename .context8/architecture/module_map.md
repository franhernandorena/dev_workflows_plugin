# Module Map

```
┌──────────────────────────────────────────────────┐
│                  dev-workflows                    │
├──────────────────────────────────────────────────┤
│                                                  │
|  install.py ──── reads ───── skills/<name>/     │
│       │                       ├── SKILL.md       │
│       │                       └── prompt.md      │
│       │                                          │
│       ├──→ Claude Code:  ~/.claude/skills/       │
│       ├──→ Codex:        ~/.agents/skills/       │
│       ├──→ Cursor:       ~/.cursor/skills/       │
│       ├──→ Gemini CLI:   ~/.gemini/skills/       │
│       ├──→ OpenCode:     ~/.config/opencode/     │
│       └──→ Hermes Agent: ~/.hermes/skills/       │
│                                                  │
├── Plugin manifests                               │
│   .claude-plugin/plugin.json                     │
│   .codex-plugin/plugin.json                      │
│   .cursor-plugin/plugin.json                     │
│   gemini-extension.json                          │
│                                                  │
├── Source prompts                                 │
│   workflows/  →  skills/workflow-*/              │
│   projects/   →  skills/project-*/               │
│   tasks/      →  skills/task-*/                  │
│                                                  │
└──────────────────────────────────────────────────┘
```

## Skill categories

```
Workflows (multi-repo)
├── workflow-init
├── workflow-continue
├── workflow-add-repo
└── workflow-status

Projects (single repo)
├── project-init
├── project-continue
├── project-handoff
├── project-audit
└── project-review

Tasks
├── task-plan
├── task-do
├── task-continue
├── task-review
└── task-hotfix

Analysis
├── change-impact
└── dependency-audit

Pull Requests
└── pr-description

Deployments
├── deploy-plan
└── release

Agent Generators
├── create-architect-agent
├── create-backend-agent
├── create-cloud-agent
├── create-database-agent
├── create-devops-agent
├── create-frontend-agent
├── create-mobile-agent
├── create-qa-agent
└── create-security-agent
```
