# Task 6: Form Elements & Inputs

**Files:**
- Modify: `static/style.css` (add form element styles)
- Modify: `templates/index.html` (update button HTML for button-in-button pattern)

**Interfaces:**
- Consumes: Task 1 tokens, Task 5 cards
- Produces: Styled form inputs, buttons, selects

## Steps

- [ ] **Step 1: Add form element styles**

Append these styles to `static/style.css`:

```css
/* === FORM ELEMENTS === */
.field-label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--muted);
  margin-bottom: var(--space-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.text-input {
  display: block;
  width: 100%;
  padding: var(--space-md) var(--space-lg);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text);
  font-size: var(--text-body);
  font-family: inherit;
  line-height: var(--leading-body);
  outline: none;
  transition: all var(--duration-fast) var(--ease-out-expo);
}

.text-input:hover {
  border-color: var(--border-strong);
}

.text-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-container);
}

.text-input--sm {
  padding: var(--space-sm) var(--space-md);
  font-size: 14px;
}

.select-input {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.5'%3E%3Cpath d='M7 10l5 5 5-5'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 40px;
  cursor: pointer;
}

/* === BUTTONS === */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-xl);
  border: none;
  border-radius: var(--radius-full);
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out-expo);
  min-height: 44px;
  width: 100%;
  position: relative;
  overflow: hidden;
}

.btn--primary {
  background: var(--primary);
  color: white;
  box-shadow: var(--shadow-md);
}

.btn--primary:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-1px);
}

.btn--primary:active {
  transform: scale(0.98) translateY(0);
}

.btn--outline {
  background: transparent;
  color: var(--primary);
  border: 1px solid var(--border);
}

.btn--outline:hover {
  background: var(--primary-container);
  border-color: var(--primary);
}

.btn--lg {
  padding: var(--space-lg) var(--space-2xl);
  font-size: var(--text-body);
  min-height: 52px;
}

.btn--sm {
  padding: var(--space-sm) var(--space-lg);
  font-size: 12px;
  min-height: 36px;
  width: auto;
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

/* Button-in-Button trailing icon */
.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(255,255,255,0.15);
  border-radius: var(--radius-full);
  transition: all var(--duration-fast) var(--ease-out-expo);
}

.group:hover .btn-icon {
  transform: translate(2px, -2px) scale(1.05);
}

.btn-row {
  display: flex;
  gap: var(--space-sm);
}

.btn-row .btn { flex: 1; }
```

- [ ] **Step 2: Update button HTML to include icon wrapper**

Update the backtest button in `index.html` to use the button-in-button pattern:

```html
<button type="button" id="backtestBtn" class="btn btn--primary btn--lg group">
  Run Backtest
  <span class="btn-icon">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M5 12h14M12 5l7 7-7 7"/>
    </svg>
  </span>
</button>
```

- [ ] **Step 3: Verify form elements render correctly**

Open browser, confirm inputs, buttons, and selects display with glass styling.

- [ ] **Step 4: Commit**

```bash
git add static/style.css templates/index.html
git commit -m "feat: add form elements with glass styling and button-in-button pattern"
```

## Report

Write your report to: `.superpowers/sdd/task-6-report.md`

Report should include:
- Status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
- Commits made
- Any concerns or observations
