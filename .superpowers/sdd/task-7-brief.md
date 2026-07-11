# Task 7: Asymmetrical Bento Layout

**Files:**
- Modify: `static/style.css` (update grid layout)
- Modify: `templates/index.html` (restructure grid)

**Interfaces:**
- Consumes: Task 3 layout, Task 5 cards
- Produces: Asymmetrical bento grid for desktop

## Steps

- [ ] **Step 1: Update grid layout for asymmetrical bento**

Replace the existing `.grid` styles in `static/style.css` with:

```css
/* === ASYMMETRICAL BENTO GRID === */
.grid {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: auto;
  gap: var(--space-xl);
  height: 100%;
}

@media (min-width: 1024px) {
  .grid {
    grid-template-columns: 380px 1fr;
    grid-template-rows: auto 1fr;
    gap: var(--space-2xl);
  }

  .input-panel {
    grid-row: 1 / -1;
  }

  .result-panel {
    grid-column: 2;
    grid-row: 1 / -1;
  }
}

/* === RESULT GRID (Internal Bento) === */
.result-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-lg);
}

@media (min-width: 768px) {
  .result-grid {
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: auto auto;
  }

  .result-grid__metrics {
    grid-column: 1 / -1;
  }

  .result-grid__chart {
    grid-column: 1 / -1;
  }

  .result-grid__details {
    grid-column: 1 / span(2);
  }

  .result-grid__actions {
    grid-column: 3 / span(2);
  }
}
```

- [ ] **Step 2: Update result panel HTML to use bento grid**

Replace the result panel HTML in `templates/index.html` with the bento grid structure:

```html
<div class="panel result-panel">
  <div class="result-header">
    <h2 class="result-header__title">Results</h2>
  </div>

  <div class="tabs">
    <button class="tab active" data-tab="backtest">Backtest</button>
    <button class="tab" data-tab="optimization">Optimization</button>
  </div>

  <div id="status" class="status hidden"></div>

  <div id="backtest-tab" class="tab-panel active">
    <div id="singleResults" class="hidden">
      <div class="result-grid">
        <div class="result-grid__metrics">
          <div class="metrics">
            <!-- metric cards -->
          </div>
        </div>
        <div class="result-grid__chart">
          <div class="chart-box">
            <canvas id="equityChart"></canvas>
          </div>
        </div>
        <div class="result-grid__details">
          <div class="detail-card">
            <!-- detail rows -->
          </div>
        </div>
        <div class="result-grid__actions">
          <div class="export-row">
            <!-- export buttons -->
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

- [ ] **Step 3: Verify bento layout renders**

Open browser at 1024px+ width, confirm asymmetrical layout with varying card sizes.

- [ ] **Step 4: Commit**

```bash
git add static/style.css templates/index.html
git commit -m "feat: add asymmetrical bento grid layout"
```

## Report

Write your report to: `.superpowers/sdd/task-7-report.md`

Report should include:
- Status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
- Commits made
- Any concerns or observations
