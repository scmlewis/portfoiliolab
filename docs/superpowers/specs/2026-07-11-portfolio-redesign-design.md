# PortfolioLab UI Redesign — Design Spec

**Date:** 2026-07-11
**Status:** Approved
**Scope:** Full redesign of PortfolioLab frontend (HTML, CSS, minimal JS for animations)

---

## 1. Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Vibe Archetype | Ethereal Glass | Best for AI/fintech/SaaS tools; deep OLED blacks, radial mesh gradients, vantablack cards |
| Layout Archetype | Asymmetrical Bento | Breaks visual monotony; masonry-like grid with varying card sizes |
| Implementation | Systematic Refactor | Lower risk; preserves working JS, incremental validation per layer |
| Target Audience | Hybrid (Retail + Pro) | Adaptive density: simplified by default, expandable on demand |
| Navigation | Floating Glass Nav | Distinctive premium look; floating pill with staggered mask reveal |

---

## 2. Design Tokens & Typography

### 2.1 Color System

**Light Mode:**
```css
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
```

**Dark Mode:**
```css
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
```

### 2.2 Typography

- **Font:** Geist Sans (Vercel, free, geometric grotesk)
- **Weights:** 400 (body), 500 (medium), 600 (semibold), 700 (bold)
- **Font loading:** Google Fonts CDN with `display=swap`

### 2.3 Icon System

- **Library:** Phosphor Icons (https://phosphoricons.com/)
- **Weight:** `light` (1px stroke) — ultra-light, precise lines
- **Format:** SVG inline or CSS background (not icon font)
- **Sizes:** 16px (small), 20px (default), 24px (large), 32px (hero)

### 2.4 Type Scale

| Token | Size | Line Height | Tracking |
|---|---|---|---|
| Display | 72px | 80px | -0.02em |
| H1 | 48px | 56px | -0.01em |
| H2 | 32px | 40px | -0.005em |
| H3 | 24px | 32px | 0 |
| Body | 16px | 24px | 0 |
| Caption | 12px | 16px | 0.02em, uppercase |

### 2.5 Spacing Scale

Macro-whitespace: `py-24` to `py-40` for sections
Component spacing: 8, 12, 16, 24, 32, 48, 64, 96, 128px

### 2.6 Shadows & Borders

**Banned:**
- 1px solid gray borders
- Dark harsh shadows (`rgba(0,0,0,0.3)`)

**Use:**
- Diffused ambient shadows: `0 8px 32px rgba(0,0,0,0.08)`
- Inner highlights: `inset 0 1px 1px rgba(255,255,255,0.15)`
- Hairline rings: `ring-1 ring-black/5 dark:ring-white/10`

---

## 3. Layout & Components

### 3.1 Navigation (Floating Glass Nav)

- **Structure:** Floating pill detached from top
  - `mt-6 mx-auto w-max rounded-full`
  - `bg-white/70 dark:bg-white/5 backdrop-blur-xl`
  - `ring-1 ring-black/5 dark:ring-white/10`
- **Mobile:** Hamburger morphs to X, full-screen glass overlay
- **Menu links:** Staggered mask reveal (`translate-y-12 opacity-0` → `translate-y-0 opacity-100`)

### 3.2 Main Layout (Asymmetrical Bento)

```
Desktop (1024px+):
┌──────────────────────────────────────────────────────────┐
│  ┌──────────────┐  ┌────────────────────────────────┐   │
│  │   Portfolio  │  │          Results               │   │
│  │   Setup      │  │          (span-8)              │   │
│  │   (span-4)   │  └────────────────────────────────┘   │
│  ├──────────────┤  ┌──────────┐ ┌──────────────────┐   │
│  │   Strategy   │  │  Metrics │ │    Chart         │   │
│  │   (span-4)   │  │ (span-4) │ │   (span-4)       │   │
│  └──────────────┘  └──────────┘ └──────────────────┘   │
└──────────────────────────────────────────────────────────┘

Mobile (<768px):
- Single column, `w-full px-4 py-8`
- All `col-span-*` resets to `col-span-1`
- No rotations or negative-margin overlaps
```

### 3.3 Double-Bezel Card Architecture

Every major card uses nested enclosures:

```css
/* Outer Shell */
.card-outer {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 2rem;
  padding: 1.5rem;
}

/* Inner Core */
.card-inner {
  background: rgba(255,255,255,0.03);
  border-radius: calc(2rem - 0.375rem);
  box-shadow: inset 0 1px 1px rgba(255,255,255,0.15);
  padding: 1.5rem;
}
```

### 3.4 CTA Buttons (Button-in-Button)

```
┌─────────────────────────────────────┐
│  Run Backtest    ┌────────────┐     │
│                  │     →      │     │
│                  └────────────┘     │
└─────────────────────────────────────┘
```

- Primary: `rounded-full px-6 py-3 bg-indigo-500`
- Trailing icon: Nested in `w-8 h-8 rounded-full bg-white/10` wrapper
- Hover: `active:scale-[0.98]`, icon translates diagonally

### 3.5 Metric Cards (Double-Bezel)

```
┌─────────────────────────────────────┐
│  ┌─────────────────────────────────┐│
│  │  ↗ Total Return                 ││
│  │  +24.5%                         ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

### 3.6 Adaptive Density (Hybrid Audience)

- **Default view:** Clean, simplified layout with generous whitespace
- **Expanded view:** Toggle to show additional data columns, detailed metrics
- **Implementation:** CSS class `.expanded` on container toggles density
- **Persistence:** Remember user preference in `localStorage`

### 3.7 Eyebrow Tags

Precede major headings with pill-shaped badges:
```css
.eyebrow {
  rounded-full px-3 py-1
  text-[10px] uppercase tracking-[0.2em] font-medium
}
```

---

## 4. Motion & Animation

### 4.1 Custom Cubic-Beziers

```css
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
--ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
--ease-spring: cubic-bezier(0.32, 0.72, 0, 1);
```

### 4.2 Duration Scale

```css
--duration-fast: 150ms;
--duration-normal: 300ms;
--duration-slow: 500ms;
--duration-slower: 700ms;
```

### 4.3 Scroll Entry Animations

```css
.reveal {
  opacity: 0;
  transform: translateY(16px);
  filter: blur(4px);
}

.reveal.revealed {
  opacity: 1;
  transform: translateY(0);
  filter: blur(0);
  transition: all 800ms var(--ease-out-expo);
}
```

- Use `IntersectionObserver` (not scroll listeners)
- Stagger delays: `100ms`, `150ms`, `200ms` for sequential items
- Only animate `transform` and `opacity` (GPU-safe)

### 4.4 Magnetic Button Hover

```css
.btn:active { transform: scale(0.98); }

.group:hover .btn-icon {
  transform: translate(2px, -2px) scale(1.05);
}
```

### 4.5 Hamburger Morph (Mobile)

- Two horizontal lines rotate 45°/-45° to form X
- Menu expands as full-screen glass overlay (`backdrop-blur-3xl bg-black/80`)
- Nav links stagger in from `translate-y-12 opacity-0`

### 4.6 FAB Animation

- Entrance: `scale(0.8) translateY(12px)` → `scale(1) translateY(0)`
- Uses `--ease-spring` for bouncy feel
- Respects `prefers-reduced-motion`

---

## 5. Responsive & Accessibility

### 5.1 Breakpoints

```css
/* Tablet: 768px+ */
/* Desktop: 1024px+ */
/* Wide: 1280px+ */
```

### 5.2 Mobile Collapse Rules

- All asymmetric layouts → `w-full px-4 py-8` below `768px`
- `col-span-*` resets to `col-span-1`
- Remove all rotations and negative-margin overlaps
- Never `h-screen` — always `min-h-[100dvh]`
- Touch targets: Minimum 44px height

### 5.3 iOS Safari Fixes

```css
input, select, textarea { font-size: 16px !important; }
padding-bottom: calc(10px + env(safe-area-inset-bottom, 0px));
```

### 5.4 Accessibility

- `focus-visible` outlines on all interactive elements
- `@media (prefers-reduced-motion: reduce)` disables all animations
- WCAG AA color contrast minimum
- Proper `aria-labels`, semantic HTML, landmark regions
- All features accessible via Tab/Enter/Escape
- Z-index discipline: nav (100), modals (1000), tooltips (200)

### 5.5 Dark Mode

- Toggle in nav (sun/moon icon)
- Persisted in `localStorage`
- Respects `prefers-color-scheme` on first visit
- All tokens have dark variants via `html.dark` class

---

## 6. Files to Modify

| File | Changes |
|---|---|
| `templates/index.html` | Font imports (Geist Sans), icon system (Phosphor SVGs), DOM structure for Double-Bezel cards, floating nav HTML, eyebrow tags |
| `static/style.css` | Complete token overhaul (colors, typography, spacing), layout architecture (Asymmetrical Bento), component styles (Double-Bezel, Button-in-Button), motion system (custom cubic-beziers, scroll reveals) |
| `static/app.js` | Scroll entry animations (IntersectionObserver), hamburger toggle logic, magnetic button hover effects, adaptive density toggle |

---

## 7. Anti-Patterns to Avoid

- Banned fonts: Inter, Roboto, Arial, Open Sans, Helvetica
- Banned icons: Standard thick-stroked Lucide, FontAwesome, Material Icons
- Banned borders: 1px solid gray
- Banned shadows: `rgba(0,0,0,0.3)`
- Banned motion: `linear` or `ease-in-out`
- Banned layouts: Edge-to-edge sticky navbars, symmetrical Bootstrap grids

---

## 8. Success Criteria

- [ ] No banned fonts, icons, borders, shadows, or motion patterns
- [ ] All major cards use Double-Bezel architecture
- [ ] CTA buttons use Button-in-Button trailing icon pattern
- [ ] Section padding is minimum `py-24`
- [ ] All transitions use custom cubic-bezier curves
- [ ] Scroll entry animations present on all sections
- [ ] Layout collapses gracefully below `768px`
- [ ] All animations use only `transform` and `opacity`
- [ ] `backdrop-blur` only on fixed/sticky elements
- [ ] Overall impression reads as "k agency build"
