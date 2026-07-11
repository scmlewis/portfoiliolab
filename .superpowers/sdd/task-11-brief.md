# Task 11: Magnetic Button Effects

**Files:**
- Modify: `static/app.js` (add magnetic button logic)

**Interfaces:**
- Consumes: Task 6 button styles
- Produces: Magnetic hover effects on buttons

## Steps

- [ ] **Step 1: Add magnetic button JavaScript**

Add this function to `static/app.js`:

```javascript
// Magnetic button hover effects
function initMagneticButtons() {
  const buttons = document.querySelectorAll('.btn--primary, .btn--lg');

  buttons.forEach(btn => {
    btn.addEventListener('mouseenter', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
    });

    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
    });

    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'translate(0, 0)';
    });
  });
}

// Initialize
document.addEventListener('DOMContentLoaded', initMagneticButtons);
```

- [ ] **Step 2: Verify magnetic effect works**

Open browser, hover over primary buttons, confirm subtle magnetic pull effect.

- [ ] **Step 3: Commit**

```bash
git add static/app.js
git commit -m "feat: add magnetic button hover effects"
```

## Report

Write your report to: `.superpowers/sdd/task-11-report.md`

Report should include:
- Status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
- Commits made
- Any concerns or observations
