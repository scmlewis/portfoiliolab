# Task 4: Floating Glass Navigation

**Files:**
- Modify: `templates/index.html` (replace header with floating nav)
- Modify: `static/style.css` (add nav styles)
- Modify: `static/app.js` (add hamburger toggle JavaScript)

**Interfaces:**
- Consumes: Task 1 tokens, Task 3 layout
- Produces: Navigation component with hamburger menu

## Steps

- [ ] **Step 1: Replace header HTML in index.html**

Replace the `<header class="header">...</header>` section with:

```html
<!-- Floating Glass Nav -->
<nav class="nav" id="mainNav">
  <div class="nav__inner">
    <div class="nav__brand">
      <svg class="nav__icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span class="nav__title">PortfolioLab</span>
    </div>
    <div class="nav__links" id="navLinks">
      <a href="#" class="nav__link" data-section="strategies">Strategies</a>
      <a href="#" class="nav__link" data-section="help">Help</a>
      <button id="darkModeToggle" class="nav__link nav__link--icon" aria-label="Toggle dark mode">
        <svg class="icon-sun" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
        </svg>
        <svg class="icon-moon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="display:none">
          <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
        </svg>
      </button>
    </div>
    <button class="nav__hamburger" id="navHamburger" aria-label="Toggle menu">
      <span class="nav__hamburger-line"></span>
      <span class="nav__hamburger-line"></span>
    </button>
  </div>
</nav>

<!-- Mobile Menu Overlay -->
<div class="nav-overlay hidden" id="navOverlay">
  <div class="nav-overlay__content">
    <a href="#" class="nav-overlay__link" data-section="strategies">Strategies</a>
    <a href="#" class="nav-overlay__link" data-section="help">Help</a>
    <button id="darkModeToggleMobile" class="nav-overlay__link" aria-label="Toggle dark mode">Toggle Theme</button>
  </div>
</div>
```

- [ ] **Step 2: Add floating nav styles to style.css**

Append these styles to `static/style.css`:

```css
/* === FLOATING GLASS NAV === */
.nav {
  position: fixed;
  top: var(--space-xl);
  left: 50%;
  transform: translateX(-50%);
  z-index: var(--z-nav);
  width: calc(100% - var(--space-3xl));
  max-width: 600px;
}

.nav__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-lg);
  padding: var(--space-md) var(--space-xl);
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-lg);
}

.nav__brand {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.nav__icon { color: var(--primary); }

.nav__title {
  font-size: var(--text-body);
  font-weight: 600;
  color: var(--text);
}

.nav__links {
  display: none;
  align-items: center;
  gap: var(--space-sm);
}

@media (min-width: 768px) {
  .nav__links { display: flex; }
  .nav__hamburger { display: none; }
}

.nav__link {
  padding: var(--space-sm) var(--space-md);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  border-radius: var(--radius-full);
  transition: all var(--duration-fast) var(--ease-out-expo);
  cursor: pointer;
  background: none;
  border: none;
  font-family: inherit;
}

.nav__link:hover {
  color: var(--text);
  background: var(--primary-container);
}

.nav__link--icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
}

/* Hamburger */
.nav__hamburger {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: var(--space-sm);
  background: none;
  border: none;
  cursor: pointer;
}

@media (min-width: 768px) {
  .nav__hamburger { display: none; }
}

.nav__hamburger-line {
  width: 20px;
  height: 1.5px;
  background: var(--text);
  transition: all var(--duration-normal) var(--ease-spring);
  transform-origin: center;
}

.nav__hamburger.active .nav__hamburger-line:first-child {
  transform: translateY(3.25px) rotate(45deg);
}

.nav__hamburger.active .nav__hamburger-line:last-child {
  transform: translateY(-3.25px) rotate(-45deg);
}

/* Mobile Overlay */
.nav-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.8);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  opacity: 1;
  transition: opacity var(--duration-normal) var(--ease-out-expo);
}

.nav-overlay.hidden {
  display: none;
  opacity: 0;
  pointer-events: none;
}

.nav-overlay__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xl);
}

.nav-overlay__link {
  font-size: var(--text-h2);
  font-weight: 600;
  color: var(--text);
  opacity: 0;
  transform: translateY(24px);
  transition: all var(--duration-slow) var(--ease-out-expo);
}

.nav-overlay:not(.hidden) .nav-overlay__link {
  opacity: 1;
  transform: translateY(0);
}

.nav-overlay:not(.hidden) .nav-overlay__link:nth-child(1) { transition-delay: 100ms; }
.nav-overlay:not(.hidden) .nav-overlay__link:nth-child(2) { transition-delay: 150ms; }
.nav-overlay:not(.hidden) .nav-overlay__link:nth-child(3) { transition-delay: 200ms; }
```

- [ ] **Step 3: Add hamburger toggle JavaScript to app.js**

Append these lines to `static/app.js`:

```javascript
// Mobile nav toggle
const navHamburger = document.getElementById('navHamburger');
const navOverlay = document.getElementById('navOverlay');

if (navHamburger && navOverlay) {
  navHamburger.addEventListener('click', () => {
    navHamburger.classList.toggle('active');
    navOverlay.classList.toggle('hidden');
    document.body.style.overflow = navOverlay.classList.contains('hidden') ? '' : 'hidden';
  });

  navOverlay.querySelectorAll('.nav-overlay__link').forEach(link => {
    link.addEventListener('click', () => {
      navHamburger.classList.remove('active');
      navOverlay.classList.add('hidden');
      document.body.style.overflow = '';
    });
  });
}
```

- [ ] **Step 4: Verify navigation renders**

Open browser, confirm floating glass pill appears. Test hamburger on mobile viewport.

- [ ] **Step 5: Commit**

```bash
git add templates/index.html static/style.css static/app.js
git commit -m "feat: add floating glass navigation with hamburger morph"
```

## Report

Write your report to: `.superpowers/sdd/task-4-report.md`

Report should include:
- Status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
- Commits made
- Any concerns or observations
