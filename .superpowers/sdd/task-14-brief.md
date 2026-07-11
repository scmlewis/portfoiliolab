# Task 14: Icon System Migration

**Files:**
- Modify: `templates/index.html` (replace Material Icons with Phosphor SVGs)

**Interfaces:**
- Consumes: Design spec section 2.3 (icon system)
- Produces: Phosphor SVG icons throughout

## Steps

- [ ] **Step 1: Replace Material Icons with inline Phosphor SVGs**

Replace all `<span class="material-symbols-rounded">icon_name</span>` with inline SVGs:

```html
<!-- Example replacements -->
<!-- Before: <span class="material-symbols-rounded">trending_up</span> -->
<!-- After: -->
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
  <path d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

Common Phosphor replacements:
- `trending_up` → ArrowUpRight
- `show_chart` → ChartLine
- `speed` → Gauge
- `shield` → Shield
- `play_arrow` → Play
- `download` → Download
- `help` → Question
- `close` → X
- `expand_more` → ChevronDown
- `auto_awesome` → Sparkle

- [ ] **Step 2: Remove Material Icons font import from index.html**

```html
<!-- Remove this line -->
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
```

- [ ] **Step 3: Verify icons render correctly**

Open browser, confirm all icons display as thin-stroke Phosphor style.

- [ ] **Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat: migrate from Material Icons to Phosphor SVGs"
```

## Report

Write your report to: `.superpowers/sdd/task-14-report.md`

Report should include:
- Status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
- Commits made
- Any concerns or observations
