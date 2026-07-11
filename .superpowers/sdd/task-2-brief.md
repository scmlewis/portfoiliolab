# Task 2: Base Typography & Body Styles

**Files:**
- Modify: `templates/index.html` (add font import)
- Modify: `static/style.css` (add base typography styles)

**Interfaces:**
- Consumes: Task 1 tokens
- Produces: Base typography used by all components

## Steps

- [ ] **Step 1: Add Geist Sans font import to index.html**

Add these lines in the `<head>` section of `templates/index.html`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap" rel="stylesheet">
```

- [ ] **Step 2: Add base typography styles to style.css**

Append these styles to `static/style.css` (after the token system):

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

## Report

Write your report to: `.superpowers/sdd/task-2-report.md`

Report should include:
- Status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
- Commits made
- Any concerns or observations
