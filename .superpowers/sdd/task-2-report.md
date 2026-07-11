# Task 2: Base Typography & Body Styles — Report

**Status:** DONE

## What I Implemented

Replaced the Roboto font import with Geist Sans in `index.html` and added base typography styles to `style.css` after the token system.

## Files Changed

- **`templates/index.html`** — Replaced Roboto font link with Geist Sans (`Geist:wght@400;500;600;700`)
- **`static/style.css`** — Added base styles section (lines 135-170) with `html`, `body`, heading, link, and `::selection` rules

## Self-Review Findings

No issues found. All CSS variables referenced in the base styles (`--font-sans`, `--text-body`, `--leading-body`, `--text-h1/h2/h3`, `--leading-h1/h2/h3`, `--tracking-h1/h2`, `--primary`, `--primary-container`, `--bg`, `--text`) are properly defined in the Task 1 token system.

## Commits

- `99aa156` — feat: add Geist Sans typography and base styles
