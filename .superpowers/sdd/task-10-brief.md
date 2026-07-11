# Task 10: Scroll Entry Animations

**Files:**
- Modify: `static/style.css` (add reveal animation styles)
- Modify: `static/app.js` (add IntersectionObserver logic)
- Modify: `templates/index.html` (add reveal classes to sections)

**Interfaces:**
- Consumes: Task 1 tokens (motion)
- Produces: Scroll-triggered reveal animations

## Steps

- [ ] **Step 1: Add reveal animation CSS**

Append these styles to `static/style.css`:

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

Add this function to `static/app.js`:

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

Add `reveal` class to each section in `templates/index.html`:

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

## Report

Write your report to: `.superpowers/sdd/task-10-report.md`

Report should include:
- Status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
- Commits made
- Any concerns or observations
