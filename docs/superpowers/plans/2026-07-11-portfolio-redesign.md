# PortfolioLab UI Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform PortfolioLab from Material 3 to Ethereal Glass aesthetic with asymmetrical bento layout, double-bezel cards, custom motion system, and premium typography.

**Architecture:** Systematic refactor of CSS layer by layer (tokens → layout → components → motion), then DOM restructuring for double-bezel cards and floating nav, then JavaScript for scroll animations and interactions.

**Tech Stack:** Vanilla CSS (no frameworks), vanilla JavaScript, Geist Sans font, Phosphor Icons SVGs, Chart.js (existing)

## Global Constraints

- No banned fonts: Inter, Roboto, Arial, Open Sans, Helvetica
- No banned icons: Standard thick-stroked Lucide, FontAwesome, Material Icons
- No banned borders: 1px solid gray
- No banned shadows: rgba(0,0,0,0.3)
- No banned motion: linear or ease-in-out
- No banned layouts: Edge-to-edge sticky navbars, symmetrical Bootstrap grids
- All animations use only transform and opacity (GPU-safe)
- backdrop-blur only on fixed/sticky elements
- Section padding minimum py-24
- All transitions use custom cubic-bezier curves
- Respect prefers-reduced-motion

---

## File Structure

| File | Responsibility |
|---|---|
| `templates/index.html` | Font imports, Phosphor SVG icons, floating nav DOM, double-bezel card structure, eyebrow tags |
| `static/style.css` | Complete rewrite: tokens, layout, components, motion, responsive |
| `static/app.js` | Scroll entry animations (IntersectionObserver), hamburger toggle, magnetic button effects, density toggle |
| `docs/superpowers/specs/2026-07-11-portfolio-redesign-design.md` | Design spec (read-only reference) |

---

## Task 1: Design Tokens & CSS Custom Properties

**Files:**
- Modify: `static/style.css` (complete rewrite of :root and html.dark variables)

**Interfaces:**
- Consumes: Design spec section 2 (tokens)
- Produces: CSS custom properties used by all subsequent tasks

- [ ] **Step 1: Clear existing style.css and write base reset + token system**

```css
/* ===================================================================
   PORTFOLIO LAB — Ethereal Glass Design System
   =================================================================== */

/* === RESET === */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* === TOKENS (Light) === */
:root {
  /* Colors */
  --bg: #FAFAFA;
  --surface: rgba(255,255,255,0.7);
  --surface-card: rgba(255,255,255,0.5);
  --surface-elevated: rgba(255,255,255,0.9);
  --primary: #6366F1;
  --primary-container: rgba(99,102,241,0.1);
  --accent: #8B5CF6;
  --accent-container: rgba(139,92,246,0.1);
  --text: #0F172A;
  --text-secondary: #334155;
  --muted: #64748B;
  --border: rgba(0,0,0,0.06);
  --border-strong: rgba(0,0,0,0.12);
  --success: #10B981;
  --success-container: rgba(16,185,129,0.1);
  --error: #EF4444;
  --error-container: rgba(239,68,68,0.1);
  --warning: #F59E0B;
  --warning-container: rgba(245,158,11,0.1);

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.06);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.08);
  --shadow-xl: 0 16px 48px rgba(0,0,0,0.1);
  --shadow-inner: inset 0 1px 1px rgba(255,255,255,0.15);

  /* Glass */
  --glass-bg: rgba(255,255,255,0.7);
  --glass-border: rgba(0,0,0,0.06);
  --glass-blur: blur(20px);

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 12px;
  --space-lg: 16px;
  --space-xl: 24px;
  --space-2xl: 32px;
  --space-3xl: 48px;
  --space-4xl: 64px;
  --space-5xl: 96px;
  --space-6xl: 128px;

  /* Radius */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-2xl: 32px;
  --radius-full: 9999px;

  /* Typography */
  --font-sans: 'Geist', system-ui, -apple-system, sans-serif;
  --text-display: 72px;
  --text-h1: 48px;
  --text-h2: 32px;
  --text-h3: 24px;
  --text-body: 16px;
  --text-caption: 12px;
  --leading-display: 80px;
  --leading-h1: 56px;
  --leading-h2: 40px;
  --leading-h3: 32px;
  --leading-body: 24px;
  --leading-caption: 16px;
  --tracking-display: -0.02em;
  --tracking-h1: -0.01em;
  --tracking-h2: -0.005em;
  --tracking-body: 0;
  --tracking-caption: 0.02em;

  /* Motion */
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
  --ease-spring: cubic-bezier(0.32, 0.72, 0, 1);
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --duration-slower: 700ms;

  /* Z-index */
  --z-base: 1;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-nav: 300;
  --z-modal: 1000;
  --z-tooltip: 1100;
  --z-overlay: 1200;
}

/* === TOKENS (Dark) === */
html.dark {
  color-scheme: dark;
  --bg: #050505;
  --surface: rgba(255,255,255,0.03);
  --surface-card: rgba(255,255,255,0.05);
  --surface-elevated: rgba(255,255,255,0.08);
  --primary: #818CF8;
  --primary-container: rgba(129,140,248,0.15);
  --accent: #A78BFA;
  --accent-container: rgba(167,139,250,0.15);
  --text: #F8FAFC;
  --text-secondary: #CBD5E1;
  --muted: #94A3B8;
  --border: rgba(255,255,255,0.06);
  --border-strong: rgba(255,255,255,0.12);
  --success: #34D399;
  --success-container: rgba(52,211,153,0.15);
  --error: #F87171;
  --error-container: rgba(248,113,113,0.15);
  --warning: #FBBF24;
  --warning-container: rgba(251,191,36,0.15);

  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.3);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.4);
  --shadow-xl: 0 16px 48px rgba(0,0,0,0.5);
  --shadow-inner: inset 0 1px 1px rgba(255,255,255,0.05);

  --glass-bg: rgba(255,255,255,0.05);
  --glass-border: rgba(255,255,255,0.08);
}
```

- [ ] **Step 2: Verify tokens render correctly**

Open `index.html` in browser, inspect `:root` in DevTools. Confirm all variables are accessible.

- [ ] **Step 3: Commit**

```bash
git add static/style.css
git commit -m "feat: add Ethereal Glass design token system"
```

---

## Task 2: Base Typography & Body Styles

**Files:**
- Modify: `static/style.css` (add after tokens)

**Interfaces:**
- Consumes: Task 1 tokens
- Produces: Base typography used by all components

- [ ] **Step 1: Add Geist Sans font import to index.html**

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap" rel="stylesheet">
```

- [ ] **Step 2: Add base typography styles to style.css**

```css
/* === BASE === */
html {
  font-family: var(--font-sans);
  background: var(--bg);
  color: var(--text);
  font-size: var(--text-body);
  line-height: var(--leading-body);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow: hidden;
  height: 100%;
}

body {
  height: 100%;
  overflow: hidden;
  background: var(--bg);
}

h1, h2, h3, h4, h5, h6 {
  color: var(--text);
  font-weight: 600;
  letter-spacing: var(--tracking-h2);
}

h1 { font-size: var(--text-h1); line-height: var(--leading-h1); letter-spacing: var(--tracking-h1); }
h2 { font-size: var(--text-h2); line-height: var(--leading-h2); letter-spacing: var(--tracking-h2); }
h3 { font-size: var(--text-h3); line-height: var(--leading-h3); }

a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }

::selection {
  background: var(--primary-container);
  color: var(--primary);
}
```

- [ ] **Step 3: Verify typography renders**

Open browser, confirm Geist font loads, headings display correctly.

- [ ] **Step 4: Commit**

```bash
git add static/style.css templates/index.html
git commit -m "feat: add Geist Sans typography and base styles"
```

---

## Task 3: App Shell & Layout Foundation

**Files:**
- Modify: `static/style.css` (add layout styles)

**Interfaces:**
- Consumes: Task 1 tokens, Task 2 typography
- Produces: App shell structure for navigation and content

- [ ] **Step 1: Add app shell and layout styles**

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

---

## Task 4: Floating Glass Navigation

**Files:**
- Modify: `templates/index.html` (replace header with floating nav)
- Modify: `static/style.css` (add nav styles)

**Interfaces:**
- Consumes: Task 1 tokens, Task 3 layout
- Produces: Navigation component with hamburger menu

- [ ] **Step 1: Replace header HTML in index.html**

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

---

## Task 5: Double-Bezel Card Architecture

**Files:**
- Modify: `static/style.css` (add card component styles)

**Interfaces:**
- Consumes: Task 1 tokens
- Produces: Reusable card components for all sections

- [ ] **Step 1: Add Double-Bezel card styles**

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

Update `index.html` to wrap sections in Double-Bezel structure:

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

- [ ] **Step 3: Verify cards render with nested bezel effect**

Open browser, confirm cards show outer shell + inner core with glass effect.

- [ ] **Step 4: Commit**

```bash
git add static/style.css templates/index.html
git commit -m "feat: add Double-Bezel card architecture"
```

---

## Task 6: Form Elements & Inputs

**Files:**
- Modify: `static/style.css` (add form element styles)

**Interfaces:**
- Consumes: Task 1 tokens, Task 5 cards
- Produces: Styled form inputs, buttons, selects

- [ ] **Step 1: Add form element styles**

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

---

## Task 7: Asymmetrical Bento Layout

**Files:**
- Modify: `static/style.css` (update grid layout)
- Modify: `templates/index.html` (restructure grid)

**Interfaces:**
- Consumes: Task 3 layout, Task 5 cards
- Produces: Asymmetrical bento grid for desktop

- [ ] **Step 1: Update grid layout for asymmetrical bento**

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
git commit -m "feat: add asymmetrical bento layout for desktop"
```

---

## Task 8: Metric Cards & Data Display

**Files:**
- Modify: `static/style.css` (add metric card styles)

**Interfaces:**
- Consumes: Task 1 tokens, Task 5 cards
- Produces: Metric cards, detail cards, chips

- [ ] **Step 1: Add metric card and data display styles**

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

```html
<div class="metric-card metric-card--success">
  <svg class="metric-card__icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
    <path d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941"/>
  </svg>
  <span class="metric-card__label">Total Return</span>
  <span class="metric-card__value" id="totalReturn">-</span>
</div>
```

- [ ] **Step 3: Verify metric cards render with glass effect**

Open browser, confirm metric cards show double-bezel effect with proper colors.

- [ ] **Step 4: Commit**

```bash
git add static/style.css templates/index.html
git commit -m "feat: add metric cards and data display components"
```

---

## Task 9: Chart & Table Styles

**Files:**
- Modify: `static/style.css` (add chart and table styles)

**Interfaces:**
- Consumes: Task 1 tokens, Task 5 cards
- Produces: Styled charts, tables, tabs

- [ ] **Step 1: Add chart, table, and tab styles**

```css
/* === CHARTS === */
.chart-box {
  position: relative;
  height: 280px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  margin-bottom: var(--space-lg);
}

@media (min-width: 768px) {
  .chart-box { height: 360px; }
}

/* === TABS === */
.tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  margin-bottom: var(--space-lg);
  gap: 0;
}

.tab {
  flex: 1;
  padding: var(--space-md) var(--space-lg);
  border: none;
  background: none;
  color: var(--muted);
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out-expo);
  position: relative;
}

.tab:hover { color: var(--text); }
.tab.active { color: var(--primary); }

.tab.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--primary);
  border-radius: 2px 2px 0 0;
}

.tab-panel { display: none; }
.tab-panel.active { display: block; }

/* === TABLES === */
.table-wrap {
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-lg);
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.table th {
  background: var(--surface-elevated);
  padding: var(--space-md) var(--space-lg);
  text-align: left;
  font-weight: 500;
  white-space: nowrap;
  border-bottom: 1px solid var(--border);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
}

.table td {
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid var(--border);
}

.table tbody tr:last-child td { border-bottom: none; }
.table tbody tr:hover { background: var(--surface); }
.table td:first-child { font-weight: 500; }
.table td.positive { color: var(--success); font-weight: 500; }
.table td.negative { color: var(--error); font-weight: 500; }

/* === STATUS === */
.status {
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-lg);
  font-size: 13px;
  font-weight: 500;
}

.status--success { background: var(--success-container); color: var(--success); }
.status--error { background: var(--error-container); color: var(--error); }
.status--loading { background: var(--primary-container); color: var(--primary); }

/* === EMPTY STATE === */
.empty-state {
  text-align: center;
  padding: var(--space-5xl) var(--space-xl);
  color: var(--muted);
}

.empty-state__icon {
  font-size: 56px;
  color: var(--border-strong);
  margin-bottom: var(--space-lg);
  display: block;
}

.empty-state p { font-size: var(--text-body); }
```

- [ ] **Step 2: Verify charts and tables render**

Open browser, confirm chart boxes, tables, and tabs display correctly.

- [ ] **Step 3: Commit**

```bash
git add static/style.css
git commit -m "feat: add chart, table, and tab styles"
```

---

## Task 10: Scroll Entry Animations

**Files:**
- Modify: `static/style.css` (add reveal animation styles)
- Modify: `static/app.js` (add IntersectionObserver logic)

**Interfaces:**
- Consumes: Task 1 tokens (motion)
- Produces: Scroll-triggered reveal animations

- [ ] **Step 1: Add reveal animation CSS**

```css
/* === SCROLL REVEAL ANIMATIONS === */
.reveal {
  opacity: 0;
  transform: translateY(20px);
  filter: blur(4px);
  transition: all 800ms var(--ease-out-expo);
}

.reveal.revealed {
  opacity: 1;
  transform: translateY(0);
  filter: blur(0);
}

.reveal-delay-1 { transition-delay: 100ms; }
.reveal-delay-2 { transition-delay: 150ms; }
.reveal-delay-3 { transition-delay: 200ms; }
.reveal-delay-4 { transition-delay: 250ms; }

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .reveal {
    opacity: 1;
    transform: none;
    filter: none;
    transition: none;
  }
}
```

- [ ] **Step 2: Add IntersectionObserver to app.js**

```javascript
// Scroll reveal animations
function initScrollReveal() {
  const reveals = document.querySelectorAll('.reveal');

  if (!reveals.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  });

  reveals.forEach(el => observer.observe(el));
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initScrollReveal);
```

- [ ] **Step 3: Add reveal classes to HTML sections**

```html
<section class="section reveal">
  <div class="card-outer">
    <div class="card-inner">
      <!-- content -->
    </div>
  </div>
</section>
```

- [ ] **Step 4: Verify scroll animations work**

Open browser, scroll down, confirm elements fade up and blur in as they enter viewport.

- [ ] **Step 5: Commit**

```bash
git add static/style.css static/app.js templates/index.html
git commit -m "feat: add scroll entry animations with IntersectionObserver"
```

---

## Task 11: Magnetic Button Effects

**Files:**
- Modify: `static/app.js` (add magnetic button logic)

**Interfaces:**
- Consumes: Task 6 button styles
- Produces: Magnetic hover effects on buttons

- [ ] **Step 1: Add magnetic button JavaScript**

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

---

## Task 12: Dark Mode Toggle

**Files:**
- Modify: `static/app.js` (update dark mode logic)

**Interfaces:**
- Consumes: Task 1 tokens (dark mode)
- Produces: Persistent dark mode toggle

- [ ] **Step 1: Update dark mode JavaScript**

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

---

## Task 13: Responsive Mobile Styles

**Files:**
- Modify: `static/style.css` (add mobile overrides)

**Interfaces:**
- Consumes: All previous tasks
- Produces: Mobile-optimized responsive styles

- [ ] **Step 1: Add comprehensive mobile styles**

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

---

## Task 14: Icon System Migration

**Files:**
- Modify: `templates/index.html` (replace Material Icons with Phosphor SVGs)

**Interfaces:**
- Consumes: Design spec section 2.3 (icon system)
- Produces: Phosphor SVG icons throughout

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

---

## Task 15: Final Polish & Testing

**Files:**
- Modify: `static/style.css` (final adjustments)
- Modify: `static/app.js` (final adjustments)

**Interfaces:**
- Consumes: All previous tasks
- Produces: Production-ready redesign

- [ ] **Step 1: Add final polish styles**

```css
/* === FINAL POLISH === */

/* Smooth scroll for anchor links */
html { scroll-behavior: smooth; }

/* Focus visible for accessibility */
*:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Selection color */
::selection {
  background: var(--primary-container);
  color: var(--primary);
}

/* Loading spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn--loading {
  position: relative;
  color: transparent !important;
  pointer-events: none;
}

.btn--loading::after {
  content: '';
  position: absolute;
  width: 18px;
  height: 18px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Tooltip */
.tooltip-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--border-strong);
  color: var(--text);
  font-size: 10px;
  font-weight: 600;
  cursor: help;
  transition: background var(--duration-fast) var(--ease-out-expo);
}

.tooltip-trigger:hover {
  background: var(--primary);
  color: white;
}
```

- [ ] **Step 2: Run full visual test**

Test checklist:
- [ ] Light mode renders correctly
- [ ] Dark mode toggles and persists
- [ ] Floating glass nav appears
- [ ] Hamburger morphs on mobile
- [ ] Double-bezel cards show nested effect
- [ ] Buttons have button-in-button icon
- [ ] Scroll reveal animations work
- [ ] Magnetic button effect works
- [ ] Metric cards display correctly
- [ ] Charts render in glass containers
- [ ] Tables have proper styling
- [ ] Mobile layout is single-column
- [ ] iOS zoom prevention works
- [ ] All icons are Phosphor SVGs

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete Ethereal Glass UI redesign

- Replace Roboto with Geist Sans
- Replace Material Icons with Phosphor SVGs
- Add floating glass navigation
- Add asymmetrical bento layout
- Add double-bezel card architecture
- Add button-in-button CTA pattern
- Add scroll entry animations
- Add magnetic button effects
- Add persistent dark mode
- Add comprehensive mobile responsive styles"
```

---

## Success Criteria

After completing all tasks, verify:

- [ ] No banned fonts, icons, borders, shadows, or motion patterns
- [ ] All major cards use Double-Bezel architecture
- [ ] CTA buttons use Button-in-Button trailing icon pattern
- [ ] Section padding is minimum py-24
- [ ] All transitions use custom cubic-bezier curves
- [ ] Scroll entry animations present on all sections
- [ ] Layout collapses gracefully below 768px
- [ ] All animations use only transform and opacity
- [ ] backdrop-blur only on fixed/sticky elements
- [ ] Overall impression reads as "k agency build"
