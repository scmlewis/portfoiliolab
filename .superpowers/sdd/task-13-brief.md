# Task 13: Responsive Mobile Styles

**Files:**
- Modify: `static/style.css` (add mobile overrides)

**Interfaces:**
- Consumes: All previous tasks
- Produces: Mobile-optimized responsive styles

## Steps

- [ ] **Step 1: Add comprehensive mobile styles**

Append these styles to `static/style.css`:

```css
/* === MOBILE (< 768px) === */
@media (max-width: 767px) {
  html, body { overflow: auto; height: auto; }

  .app {
    height: auto;
    min-height: 100vh;
    min-height: 100dvh;
  }

  .main {
    overflow: visible;
    padding: var(--space-lg);
    padding-top: 100px; /* Space for floating nav */
  }

  .grid {
    grid-template-columns: 1fr;
    height: auto;
    gap: var(--space-lg);
  }

  .panel {
    overflow: visible;
    border-radius: var(--radius-xl);
  }

  .input-panel,
  .result-panel {
    padding: var(--space-lg);
  }

  /* Cards stack on mobile */
  .card-outer {
    border-radius: var(--radius-xl);
    padding: var(--space-md);
  }

  .card-inner {
    border-radius: calc(var(--radius-xl) - 6px);
    padding: var(--space-lg);
  }

  /* Metrics 2-col on mobile */
  .metrics {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-sm);
  }

  .metric-card {
    padding: var(--space-md);
    border-radius: var(--radius-lg);
  }

  .metric-card__value {
    font-size: 20px;
  }

  /* Buttons full width */
  .btn-row {
    flex-direction: column;
    gap: var(--space-sm);
  }

  .btn-row .btn {
    width: 100%;
  }

  /* Export row */
  .export-row {
    flex-direction: column;
    gap: var(--space-sm);
  }

  .export-row .btn {
    width: 100%;
  }

  /* Tables */
  .table-wrap {
    max-height: 300px;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }

  .table {
    font-size: 12px;
  }

  .table th,
  .table td {
    padding: var(--space-sm) var(--space-md);
  }

  /* Tabs */
  .tab {
    padding: var(--space-sm) var(--space-md);
    font-size: 13px;
  }

  /* Chart */
  .chart-box {
    height: 200px;
    padding: var(--space-md);
  }

  /* Prevent iOS zoom */
  input, select, textarea {
    font-size: 16px !important;
  }

  /* Safe area */
  .footer {
    padding-bottom: calc(10px + env(safe-area-inset-bottom, 0px));
  }

  /* Onboarding */
  .onboarding__card {
    padding: var(--space-xl);
    width: 92%;
    border-radius: var(--radius-xl);
  }
}

/* === TINY SCREENS (< 400px) === */
@media (max-width: 400px) {
  .metrics {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 2: Verify mobile layout**

Open browser at 375px width, confirm single-column layout, proper spacing, no horizontal scroll.

- [ ] **Step 3: Commit**

```bash
git add static/style.css
git commit -m "feat: add comprehensive mobile responsive styles"
```

## Report

Write your report to: `.superpowers/sdd/task-13-report.md`

Report should include:
- Status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
- Commits made
- Any concerns or observations
