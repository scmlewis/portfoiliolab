# Task 6: Form Elements & Inputs — Report

**Status:** DONE

**Commits:**
- `e14d07c` — feat: add form elements with glass styling and button-in-button pattern

## What I Implemented

### Step 1: Form element styles (CSS)
Appended to `static/style.css`:
- `.field-label` — uppercase muted labels
- `.text-input` — glass-styled inputs with hover/focus states, `--sm` variant
- `.select-input` — custom dropdown arrow via SVG background
- `.btn` — full-width pill buttons with primary/outline/lg/sm variants
- `.btn-icon` — button-in-button trailing icon with hover lift
- `.btn-row` — flex row for button groups

### Step 2: Backtest button (HTML)
Updated `#backtestBtn` in `templates/index.html`:
- Added `group` class for hover targeting
- Replaced Material icon with SVG arrow inside `.btn-icon` wrapper
- Implements button-in-button pattern per task spec

## Self-Review

- All CSS uses design tokens (spacing, colors, radius, motion) — no hardcoded values
- Button transitions match `--duration-fast` + `--ease-out-expo` from Task 1 tokens
- `.select-input` extends `.text-input` (class added in HTML, not CSS override)
- `.btn--sm` sets `width: auto` to prevent full-width in button rows
- Dark mode works automatically via CSS custom properties
- No CSS conflicts with existing styles

## Files Changed

| File | Change |
|------|--------|
| `static/style.css` | +138 lines (form elements + buttons) |
| `templates/index.html` | Updated backtest button markup |
