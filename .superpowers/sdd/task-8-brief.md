# Task 8: Metric Cards & Data Display

**Files:**
- Modify: `static/style.css` (add metric card styles)
- Modify: `templates/index.html` (update metric card HTML)

**Interfaces:**
- Consumes: Task 1 tokens, Task 5 cards
- Produces: Metric cards, detail cards, chips

## Steps

- [ ] **Step 1: Add metric card and data display styles**

Append these styles to `static/style.css`:

```css
/* === METRIC CARDS === */
.metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

@media (min-width: 768px) {
  .metrics {
    grid-template-columns: repeat(4, 1fr);
  }
}

.metric-card {
  background: var(--surface-card);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  transition: all var(--duration-normal) var(--ease-out-expo);
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.metric-card__icon {
  font-size: 20px;
  color: var(--primary);
  margin-bottom: var(--space-xs);
}

.metric-card__label {
  font-size: 11px;
  font-weight: 500;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.metric-card__value {
  font-size: var(--text-h3);
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.02em;
}

.metric-card--success {
  background: var(--success-container);
  border-color: var(--success);
}

.metric-card--success .metric-card__icon { color: var(--success); }
.metric-card--success .metric-card__value { color: var(--success); }

.metric-card--error {
  background: var(--error-container);
  border-color: var(--error);
}

.metric-card--error .metric-card__icon { color: var(--error); }
.metric-card--error .metric-card__value { color: var(--error); }

.metric-card--accent {
  background: var(--accent-container);
  border-color: var(--accent);
}

.metric-card--accent .metric-card__icon { color: var(--accent); }
.metric-card--accent .metric-card__value { color: var(--accent); }

/* === DETAIL CARD === */
.detail-card {
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  margin-bottom: var(--space-lg);
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-sm) 0;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
}

.detail-row:last-child { border-bottom: none; }
.detail-row span { color: var(--muted); }
.detail-row strong { color: var(--text); font-weight: 500; }

/* === CHIPS === */
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  background: var(--surface-card);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
}

.chip svg { color: var(--primary); }
```

- [ ] **Step 2: Update metric card HTML to use new classes**

Update the metric cards in `templates/index.html` to use the new structure:

```html
<div class="metric-card metric-card--success">
  <svg class="metric-card__icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
    <path d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941"/>
  </svg>
  <span class="metric-card__label">Total Return</span>
  <span class="metric-card__value" id="totalReturn">-</span>
</div>
```

Do this for all metric cards (Total Return, Sharpe Ratio, Win Rate, Max Drawdown).

- [ ] **Step 3: Verify metric cards render with glass effect**

Open browser, confirm metric cards show double-bezel effect with proper colors.

- [ ] **Step 4: Commit**

```bash
git add static/style.css templates/index.html
git commit -m "feat: add metric cards and data display components"
```

## Report

Write your report to: `.superpowers/sdd/task-8-report.md`

Report should include:
- Status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
- Commits made
- Any concerns or observations
