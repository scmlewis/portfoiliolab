# Task 12: Dark Mode Toggle

**Files:**
- Modify: `static/app.js` (update dark mode logic)

**Interfaces:**
- Consumes: Task 1 tokens (dark mode)
- Produces: Persistent dark mode toggle

## Steps

- [ ] **Step 1: Update dark mode JavaScript**

Add this function to `static/app.js`:

```javascript
// Dark mode toggle
function initDarkMode() {
  const toggle = document.getElementById('darkModeToggle');
  const toggleMobile = document.getElementById('darkModeToggleMobile');
  const html = document.documentElement;
  const iconSun = toggle?.querySelector('.icon-sun');
  const iconMoon = toggle?.querySelector('.icon-moon');

  // Check for saved preference or system preference
  const savedTheme = localStorage.getItem('portfoliolab_theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    html.classList.add('dark');
    updateIcons(true);
  }

  function toggleDark() {
    html.classList.toggle('dark');
    const isDark = html.classList.contains('dark');
    localStorage.setItem('portfoliolab_theme', isDark ? 'dark' : 'light');
    updateIcons(isDark);
  }

  function updateIcons(isDark) {
    if (iconSun) iconSun.style.display = isDark ? 'none' : 'block';
    if (iconMoon) iconMoon.style.display = isDark ? 'block' : 'none';
  }

  toggle?.addEventListener('click', toggleDark);
  toggleMobile?.addEventListener('click', toggleDark);
}

document.addEventListener('DOMContentLoaded', initDarkMode);
```

- [ ] **Step 2: Verify dark mode toggle works**

Open browser, click sun/moon icon, confirm theme toggles and persists on reload.

- [ ] **Step 3: Commit**

```bash
git add static/app.js
git commit -m "feat: add persistent dark mode toggle"
```

## Report

Write your report to: `.superpowers/sdd/task-12-report.md`

Report should include:
- Status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
- Commits made
- Any concerns or observations
