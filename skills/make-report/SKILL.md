---
name: make-report
version: 1.1.0
description: Generates structured markdown reports optimized for ClickUp Docs — teaches the model how to structure documents, what questions to ask, and which formatting elements (tables, diagrams, content blocks) ClickUp supports natively
category: document
---

# Make Report — Generate ClickUp-Optimized Documents in Markdown

## Overview
Guides the model to produce well-structured markdown documents designed to be pasted or imported into **ClickUp Docs**. Covers document anatomy, ClickUp's supported formatting (tables, content blocks, embeds, diagrams), pre-writing questions, and output conventions so the result looks native in ClickUp with minimal reformatting.

## When to use
- User asks "create a report" / "write documentation" / "make a doc"
- Generating SOPs, runbooks, architecture docs, meeting notes, project proposals, decision records (ADRs), changelogs, API docs, onboarding guides
- Any document destined for ClickUp Docs that should use ClickUp-native formatting
- The model needs guidance on what markdown ClickUp actually supports vs. what breaks

## When NOT to use
- The document is for a different platform (Notion, Confluence, GitHub Wiki, Google Docs) — each has different formatting support
- Single-line or trivial output that doesn't need structure
- The user just wants code or raw data, not a formatted document

## Output
- A complete markdown document ready to paste into ClickUp Docs (or save as `.md` and import)
- The document uses only formatting that ClickUp supports natively
- Includes a brief "ClickUp paste notes" section if there are caveats for specific blocks

---

## Full Prompt

## Phase 0 — Pre-flight: Ask These Questions First

Before writing a single line, gather context. **Always ask the user** (or infer from the conversation) these questions:

1. **Audience** — Who will read this? (Engineers / Ops / Leadership / Clients / New hires)
2. **Purpose** — What should the reader DO after reading? (Learn a process / Make a decision / Debug an issue / Onboard)
3. **Scope** — What is explicitly IN and OUT of this document?
4. **Tone** — Formal / Technical / Conversational / Step-by-step
5. **Length preference** — Quick reference (1-2 pages) / Detailed guide (3-10 pages) / Full spec (10+ pages)
6. **Existing structure** — Is there a template or existing doc to follow?
7. **Diagrams needed?** — Flowcharts, architecture diagrams, sequence diagrams (see Phase 4 for ClickUp's diagram support)

If the user provides a clear brief, you can skip some questions, but always confirm audience and purpose.

---

## Phase 1 — Document Anatomy (ClickUp-Optimized Structure)

ClickUp Docs support **nested pages** (parent → child hierarchy). Structure your markdown so headings map to pages:

```
# Document Title (H1)           → Parent Doc title
## Section (H2)                 → Can be a sub-page heading
### Sub-section (H3)            → Within-page sections
#### Detail (H4)                → Deep nesting within sections
```

### Recommended structure for most reports

```markdown
# [Document Title]

**Version**: 1.0
**Last updated**: YYYY-MM-DD
**Author**: [Name/Team]

---

## Table of Contents

<!-- ClickUp auto-generates a sticky TOC from headings when you use /toc -->

## 1. TL;DR — Executive Summary

[Summary of the report's conclusion. Written LAST, placed FIRST. See Phase 5.]

## 2. Context / Background

[Why this exists, what problem it solves]

## 3. Main Content

### 3.1 [Subtopic A]

### 3.2 [Subtopic B]

## 4. Action Items / Next Steps

| # | Action | Owner | Deadline | Status |
|---|--------|-------|----------|--------|
| 1 | Do X | @team | 2026-07-01 | 🔴 Not started |

## 5. References

- [Link title](URL)
- Related docs: [Doc Name](URL)

## Appendix

### A. Terminology

### B. Change Log
```

---

## Phase 2 — Markdown Formatting: What ClickUp Supports

ClickUp uses rich markdown shortcuts. Here's exactly what works and what doesn't.

### ✅ FULLY SUPPORTED (use freely)

| Element | Markdown Syntax | Notes |
|---------|----------------|-------|
| **Headings H1-H4** | `# ` `## ` `### ` `#### ` | Collapsible headings supported in Docs |
| **Bold** | `**text**` or `__text__` | |
| *Italic* | `*text*` or `_text_` | |
| ***Bold+Italic*** | `***text***` | |
| **Strikethrough** | `~~text~~` | |
| ~~Strikethrough~~ | `~~text~~` | |
| **Inline code** | `` `code` `` | |
| **Code block** | ```` ```language ```` | Syntax highlighting for 30+ languages |
| **Blockquote** | `> text` | |
| **Bulleted list** | `- item` or `* item` | |
| **Numbered list** | `1. item` | |
| **Checklist** | `- [ ] task` / `- [x] done` | ClickUp renders as interactive checkboxes |
| **Divider** | `---` or `***` | |
| **Links** | `[text](URL)` | Opens in-browser |
| **Image** | `![alt](URL)` | Supports pasting images directly |
| **Table of Contents** | Use `/toc` slash command | Auto-generated sticky TOC from headings |
| **Table** | `\| col1 \| col2 \|` or `/table` | Rich tables: merge cells, bg color, alignment |
| **Columns** | Use `/columns` slash command | Multi-column layouts (2-3+ columns) |

### ⚠️ SUPPORTED WITH CAVEATS

| Element | What to know |
|---------|-------------|
| **Nested lists** | ClickUp supports nested lists, but paste may flatten them. Use 2-space or 4-space indent. |
| **Toggle list** | Use `/toggle` slash command in ClickUp. Markdown `<details><summary>` is NOT supported — paste and reformat. |
| **Banner / Callout** | Use `/banner` or `/callout` slash command in ClickUp. There's no markdown syntax for these. |
| **Button** | Use `/button` in ClickUp. No markdown equivalent. |
| **Highlight** | Use text toolbar in ClickUp (`Ctrl+Shift+H`). No markdown syntax. |

### ❌ NOT SUPPORTED (avoid or use workaround)

| Element | Problem | Workaround |
|---------|---------|------------|
| **Mermaid diagrams** | ClickUp has NO native Mermaid rendering (feature request open since 2022) | Export as PNG from Mermaid Live Editor → paste image; or embed via `/embed` with Mermaid URL |
| **`<details><summary>`** | HTML tags are not rendered | Use `/toggle` in ClickUp after paste |
| **Footnotes** `[^1]` | Not supported | Use inline links or appendix |
| **Definition lists** | Not supported | Use a table or bullet list |
| **Math/LaTeX** `$$...$$` | Not supported | Paste as image or use dedicated tool |
| **HTML inline** (`<div>`, `<span>`, `<br>`) | Not rendered | Use pure markdown |
| **Task/Doc mentions** | `@user` or doc links need ClickUp-native `/link` | Paste doc title as plain link |
| **Meta / Frontmatter** `---` | ClickUp ignores YAML frontmatter | Remove before pasting, or keep as visual separator |
| **Table in table (nested tables)** | Not supported | Flatten into one table with merged cells |
| **Emoji shortcodes** `:smile:` | Plain text only, not rendered as emoji | Use the actual emoji character 😄 (copy-paste) |

---

## Phase 3 — Tables: ClickUp's Rich Table Features

ClickUp tables are **NOT standard markdown tables** under the hood — they are rich content blocks. However, **standard GFM (GitHub Flavored Markdown) tables paste correctly** and are converted to ClickUp native tables.

### What translates well

```markdown
| Column A | Column B | Column C |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
```

### ClickUp table capabilities (after paste, use the toolbar)

- **Merge cells** — select adjacent cells and merge
- **Background color** — per cell, row, or column
- **Text alignment** — left / center / right per column
- **Column resize** — drag column borders
- **Row/column add/delete** — via hover menu
- **Paste from Excel/CSV** — ClickUp auto-converts pasted spreadsheet data into a table

### Best practices for tables in reports

1. Keep tables **simple**: max 6-8 columns. ClickUp tables scroll horizontally beyond that.
2. Use **header row** with `---` separator — ClickUp treats first row as header.
3. **Avoid** merged cells in source markdown — paste first, then merge in ClickUp.
4. For **large datasets**, use `/table` or paste CSV, not manual markdown.
5. **Alignment**: standard `:---` (left), `:---:` (center), `---:` (right) work.

---

## Phase 4 — Diagrams: What ClickUp Supports and How

This is the most important section. ClickUp's diagram support is **limited compared to Notion or GitHub**.

### ❌ NOT supported natively

- **Mermaid.js** — NO native rendering. Feature request open for years, not on roadmap.
- **Embedded Whiteboards in Docs** — Whiteboards are separate; cannot embed them inline in Docs.
- **draw.io** — No native integration in Docs (only via `/embed` with public URL)

### ✅ Supported approaches

| Method | How it works | Best for |
|--------|-------------|----------|
| **Screenshot / Image paste** | Generate diagram → export as PNG/SVG → paste into Doc | All diagram types. Simple, reliable. |
| **`/embed` with public URL** | `/embed` or paste URL → ClickUp renders iframe. Supports: YouTube, Vimeo, Loom, Google Sheets, Miro (public boards), Figma (public), Google Docs, Google Maps, Airtable Bases, InVision, Twitter | When you have a hosted diagram (Miro, Figma) |
| **Mermaid Live Editor → Image** | https://mermaid.live/ → render → screenshot or export PNG → paste | Flowcharts, sequence diagrams, class diagrams, Gantt |
| **Draw.io → Export PNG** | Draw.io → save as local PNG → paste | Architecture diagrams, network topology, mind maps |
| **Excalidraw** | Excalidraw → export as PNG/SVG → paste | Hand-drawn style diagrams, wireframes |
| **ClickUp Whiteboards** | Create Whiteboard separately, take screenshot, paste into Doc | Quick brainstorming, process maps |

### Recommended approach for AI-generated reports

Since the AI generates text, not images:

1. **Write the diagram as a Mermaid code block** in the markdown:

    ````markdown
    ```mermaid
    graph TD
        A[Start] --> B{Decision}
        B -->|Yes| C[Process]
        B -->|No| D[End]
    ```
    ````

2. Add a **paste note** telling the user:

    > **📋 Paste note for ClickUp**: ClickUp doesn't render Mermaid natively. To add this diagram:
    > 1. Copy the Mermaid code above
    > 2. Go to https://mermaid.live/ and paste it
    > 3. Export as PNG
    > 4. Paste the PNG into this Doc

3. Alternatively, if the user prefers **ascii diagrams** that render as text:

    ```
    ┌─────────┐     ┌───────────┐     ┌──────────┐
    │  Input  │────▶│  Process  │────▶│  Output  │
    └─────────┘     └───────────┘     └──────────┘
    ```

### Mermaid diagram types useful for reports

| Type | ```` ```mermaid ```` | Use case |
|------|-------|----------|
| Flowchart | `graph TD` or `graph LR` | Processes, workflows |
| Sequence diagram | `sequenceDiagram` | API interactions, user flows |
| Class diagram | `classDiagram` | Architecture, data models |
| Gantt chart | `gantt` | Timelines, project plans |
| Pie chart | `pie` | Distributions, budgets |
| ER diagram | `erDiagram` | Database schemas |
| State diagram | `stateDiagram-v2` | State machines, status flows |
| Timeline | `timeline` | Roadmaps, release history |
| Gitgraph | `gitGraph` | Branch strategies, release flow |

---

## Phase 5 — Writing Guidelines for ClickUp Docs

### Executive Summary (TL;DR) — summary of the conclusion, placed FIRST

The report opens with a small executive summary so a PM or stakeholder can
grasp everything without reading the rest. Rules:

- **It is a summary of the report's conclusion**: what was done, what was
  found, the key decisions, and what's next. Write the body and the
  conclusion first, then condense that conclusion here.
- **As small as the content allows**: no filler, no "This report
  summarizes…", no repeated background. Every line must carry a fact, a
  number, or a decision. There is **no fixed bullet limit** — use as many as
  the conclusion genuinely needs, but make it the shortest faithful version.
- **Stand alone**: the reader who reads ONLY this understands the whole
  report. No "see below" or section-number references.
- **Include the numbers that matter**: key metrics, decisions, blockers.
- **Tone**: neutral, factual, present tense.

Example:

> **TL;DR**
> - Migración a Vite completada: build 3.2× más rápido (18s → 5.6s).
> - 2 bugs críticos de auth encontrados y fixeados; cobertura de tests 71% → 84%.
> - Próximo: QA de regresión en staging + release a prod el 2026-08-10.

### Content organization

- **Start with the TOC**: ClickUp auto-generates a sticky TOC from H1-H4. Place `<!-- TOC will go here -->` and remind the user to use `/toc`.
- **Use collapsible headings**: In ClickUp you can collapse H1-H4 sections. Structure heading depth logically.
- **Nested pages**: For documents longer than ~5 sections, suggest the user split into parent Doc + sub-pages (right-click → "Add sub-page").
- **Keep paragraphs short**: ClickUp docs render best with 3-5 sentence paragraphs separated by blank lines.

### Linking and references

- **Internal links**: ClickUp supports `[text](URL)`. For links to other ClickUp Docs, use the Doc URL.
- **Task references**: ClickUp renders task IDs (e.g. `TASK-123`) as clickable task links. **Use them.**
- **@mentions**: Not supported in plain markdown paste. Tell the user to use ClickUp's native `@mention` after paste.

### ClickUp-specific tips

- **Frontmatter**: Remove YAML frontmatter `---` before pasting into ClickUp, or it renders as a divider.
- **Emojis**: Use actual emoji characters (✅, 🚀, ⚠️, 📋, 🎯), not shortcodes.
- **Status indicators**: Use emoji conventions: ✅ Done, 🔴 Blocked, 🟡 In Progress, 🟢 Complete, ⚠️ Warning.
- **Checklists**: Markdown `- [ ]` / `- [x]` paste into ClickUp as interactive checkboxes. Use for action items.
- **Images**: If the report references external images, provide the URLs. ClickUp can fetch and embed them.

---

## Phase 6 — Output Template

Generate the final document using this template. **Always include paste notes** for ClickUp-specific features.

```markdown
# [Report Title]

**Version**: 1.0
**Last Updated**: YYYY-MM-DD
**Author**: [AI-generated / User]
**Status**: Draft / Review / Final

---

> **📋 ClickUp paste notes**
> - Paste this entire markdown block into a ClickUp Doc
> - Use `/toc` to insert an auto-generated Table of Contents at the top
> - Mermaid diagrams → render at https://mermaid.live/ and paste as PNG
> - Add @mentions and task links after paste using ClickUp's native formatting

---

## 1. TL;DR — Executive Summary

> **TL;DR**
> - [Conclusion point 1 — with the key number]
> - [Conclusion point 2]
> - [Conclusion point 3 — as many as the conclusion needs; no fixed limit; written LAST]

## 2. Context

[Background]

## 3. [Main Section]

### 3.1 [Subtopic]

[Content with tables, lists, code blocks as needed]

## 4. Action Items

| # | Action | Owner | Priority | Status |
|---|--------|-------|----------|--------|
| 1 | | | P0 | 🔴 |

## 5. References

- [Title](URL)

---

*Report generated with [tool info] on YYYY-MM-DD*
```

---

## Phase 7 — Verification Checklist

Before delivering the document:

- [ ] Audience and purpose confirmed (Phase 0 questions)
- [ ] TL;DR at the top: summary of the conclusion, written LAST, stands alone
- [ ] Only ClickUp-supported markdown elements used (no HTML, no Mermaid-as-code, no footnotes)
- [ ] Tables are GFM-standard with header row separator
- [ ] Any Mermaid/ASCII diagrams include a paste note for ClickUp
- [ ] Frontmatter removed or marked as "remove before paste"
- [ ] Emojis are actual characters, not shortcodes
- [ ] Action items use `- [ ]` checklist syntax if they're tasks
- [ ] Document has a clear TOC placeholder or `/toc` instruction
- [ ] Links are valid `[text](URL)` format
- [ ] Paste notes for ClickUp included at the top of the document

---

## Rules

- Always include ClickUp paste notes when the document contains diagrams, columns, or ClickUp-native features.
- Never use HTML tags, Mermaid-as-natively-rendered (ClickUp doesn't support it), footnotes, definition lists, or LaTeX math.
- Always confirm audience + purpose before writing. Do not skip Phase 0.
- If the user doesn't specify a platform, ask "Is this for ClickUp Docs?" before generating.
- All output in the user's conversation language unless explicitly overridden.
