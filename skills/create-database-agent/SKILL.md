---
name: create-database-agent
version: 1.0.0
description: Investigates the project, asks about database needs, and generates a professional Database Expert agent in the native format of the current tool
---

# Create Database Agent — Generate a Specialized Database Expert Agent

## Overview
Investigates the project, inventories available skills/plugins, asks targeted questions about database needs, and generates a complete Database Expert agent in the native agent format of the current tool.

## When to use
- Need a dedicated Database expert agent for schema design, optimization, and migrations
- Project has complex data modeling or performance requirements
- Want enforcement of database best practices and query optimization

## When NOT to use
- No project code exists yet → use project-init first
- Database is simple and well-understood → use create-backend-agent instead

## Output
- An agent file in the native format of the current tool, saved in the per-project agents directory

## Full Prompt

# CREATE DATABASE AGENT — Generate a Database Expert Agent

## RULE: This skill generates an agent. No application code changes.

---

## Phase 1 — Preflight

### 1.1 Inventory installed skills/plugins
```bash
ls -d skills/*/ 2>/dev/null | sed 's|skills/||;s|/||'
```
Read any skill files relevant to databases or data.

Check MCP servers:
```bash
cat opencode.json 2>/dev/null | grep -i "plugin\|mcp" || true
cat .claude/settings.json 2>/dev/null | grep -i "mcp\|plugin" || true
ls .mcp.json 2>/dev/null && head -50 .mcp.json || true
```

### 1.2 Scan project tech stack
```bash
# Database configs
ls prisma/ schema.prisma sequelize* typeorm* drizzle* 2>/dev/null
ls alembic.ini migrations/ 2>/dev/null
ls database.yml *.sql 2>/dev/null | head -10
# ORM imports
grep -r "from\|import\|require" package.json pyproject.toml 2>/dev/null | grep -i "prisma\|typeorm\|sequelize\|drizzle\|sqlalchemy\|django\|mongoose\|knex" | head -5
```

### 1.3 Build context profile
Synthesize: database type, ORM, migration tool, seed data approach, available plugins.

---

## Phase 2 — Domain Research: Database

```bash
# Migration files
find . -path "*migration*" -name "*.sql" -o -path "*migration*" -name "*.ts" -o -path "*migration*" -name "*.py" 2>/dev/null | head -15
# Schema files
find . -name "schema*" -o -name "model*" 2>/dev/null | head -10
# Seed data
find . -name "seed*" 2>/dev/null | head -5
# Raw queries
grep -r "SELECT\|INSERT\|UPDATE\|DELETE" --include="*.ts" --include="*.py" --include="*.js" 2>/dev/null | grep -v node_modules | grep -v ".venv" | head -20
```

Read the schema definition and a sample migration.

---

## Phase 3 — Domain Questions

Ask the user one at a time:

1. **What database system?** (PostgreSQL, MySQL, SQLite, MongoDB, Redis, other)
2. **What ORM or query approach?** (Prisma, TypeORM, SQLAlchemy, raw SQL, Drizzle, other)
3. **Migration strategy?** (auto-generated, manual SQL, CI/CD applied, no migrations yet)
4. **Performance concerns?** (slow queries, large datasets, high concurrency, not yet)
5. **Backup and recovery plan?** (automated, manual, none yet)

---

## Phase 4 — Generate Agent

Create a **Database Expert agent** in the native format of the current tool.

The agent should include:
- Role: Database Expert for this project
- Available DB-relevant skills/plugins from Phase 1
- Full prompt covering: schema design, query optimization, migration management, indexing strategies, backup procedures, performance monitoring
- Permission: read access to all code, write access to DB-related files only
- Temperature: 0.2 (precision-critical domain)
- Model: capable for complex query analysis

---

## Rules
- Generate in native format of the current tool.
- Save per-project.
- All questions in English unless user prefers otherwise.
