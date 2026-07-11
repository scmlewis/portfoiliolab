# Task 3: App Shell & Layout Foundation

**Files:**
- Modify: `static/style.css` (add layout styles)

**Interfaces:**
- Consumes: Task 1 tokens, Task 2 typography
- Produces: App shell structure for navigation and content

## Steps

- [ ] **Step 1: Add app shell and layout styles**

Append these styles to `static/style.css`:

```css
/* === APP SHELL === */
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh;
  max-width: 1440px;
  margin: 0 auto;
  position: relative;
}

/* === MAIN LAYOUT === */
.main {
  flex: 1;
  overflow: hidden;
  padding: var(--space-xl);
}

.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-xl);
  height: 100%;
}

@media (min-width: 1024px) {
  .grid {
    grid-template-columns: 400px 1fr;
    gap: var(--space-2xl);
  }
}

/* === PANELS === */
.panel {
  background: var(--surface-card);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-2xl);
  overflow-y: auto;
  overflow-x: hidden;
}

.input-panel { padding: var(--space-xl); }
.result-panel { padding: var(--space-xl); }

/* === SCROLLBAR === */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }
```

- [ ] **Step 2: Verify layout renders**

Open browser, confirm app shell displays with panels.

- [ ] **Step 3: Commit**

```bash
git add static/style.css
git commit -m "feat: add app shell and layout foundation"
```

## Report

Write your report to: `.superpowers/sdd/task-3-report.md`

Report should include:
- Status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
- Commits made
- Any concerns or observations
