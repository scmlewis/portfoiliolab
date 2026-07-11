# Task 5: Double-Bezel Card Architecture

**Files:**
- Modify: `static/style.css` (add card component styles)
- Modify: `templates/index.html` (wrap sections in Double-Bezel structure)

**Interfaces:**
- Consumes: Task 1 tokens
- Produces: Reusable card components for all sections

## Steps

- [ ] **Step 1: Add Double-Bezel card styles**

Append these styles to `static/style.css`:

```css
/* === DOUBLE-BEZEL CARDS === */
.card-outer {
  background: var(--surface-card);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-2xl);
  padding: var(--space-lg);
  transition: all var(--duration-normal) var(--ease-out-expo);
}

.card-inner {
  background: var(--surface);
  border-radius: calc(var(--radius-2xl) - 6px);
  box-shadow: var(--shadow-inner);
  padding: var(--space-xl);
}

/* === SECTIONS === */
.section {
  margin-bottom: var(--space-xl);
}

.section:last-child {
  margin-bottom: 0;
}

.section__head {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.section__title {
  font-size: var(--text-body);
  font-weight: 600;
  line-height: var(--leading-body);
}

.section__desc {
  font-size: var(--text-caption);
  color: var(--muted);
  margin-top: 2px;
}

.section__body {
  padding-left: 0;
}

/* === EYEBROW TAGS === */
.eyebrow {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  padding: 0 var(--space-sm);
  background: var(--primary);
  color: white;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
}

.eyebrow--outline {
  background: transparent;
  color: var(--muted);
  border: 1px solid var(--border-strong);
}
```

- [ ] **Step 2: Apply card classes to existing HTML sections**

Update `index.html` to wrap each section in Double-Bezel structure:

```html
<section class="section">
  <div class="card-outer">
    <div class="card-inner">
      <div class="section__head">
        <span class="eyebrow">1</span>
        <div>
          <h2 class="section__title">Portfolio Setup</h2>
          <p class="section__desc">Choose assets and time period</p>
        </div>
      </div>
      <div class="section__body">
        <!-- existing content -->
      </div>
    </div>
  </div>
</section>
```

Do this for all sections (Portfolio Setup, Strategy, Advanced).

- [ ] **Step 3: Verify cards render with nested bezel effect**

Open browser, confirm cards show outer shell + inner core with glass effect.

- [ ] **Step 4: Commit**

```bash
git add static/style.css templates/index.html
git commit -m "feat: add Double-Bezel card architecture"
```

## Report

Write your report to: `.superpowers/sdd/task-5-report.md`

Report should include:
- Status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
- Commits made
- Any concerns or observations
