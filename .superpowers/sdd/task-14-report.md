# Task 14: Icon System Migration

## Status: DONE

## What I Implemented
Replaced all Material Icons with inline Phosphor SVG icons throughout `templates/index.html`. Removed the Google Fonts Material Icons import.

## Changes Made
- Removed Material Icons font import from `<head>`
- Replaced 25+ Material Icon spans with inline Phosphor SVGs:
  - `cloud_queue` → Cloud icon (data status)
  - `shield` → Shield (conservative preset, best DD)
  - `balance` → Scale (balanced preset)
  - `bolt` → Lightning (aggressive preset)
  - `rocket_launch` → Rocket (growth preset)
  - `expand_more` → ChevronDown (advanced section)
  - `compare_arrows` → ArrowsLeftRight (compare strategies)
  - `auto_awesome` → Sparkle (compare selected)
  - `scatter_plot` → PieChart (portfolio optimization, empty state)
  - `auto_graph` → TrendingUp (optimize button)
  - `show_chart` → ChartLine (frontier button, benchmark)
  - `casino` → Dice (Monte Carlo, 2 instances)
  - `save` → FloppyDisk (save/load config)
  - `monitoring` → ChartBar (results header)
  - `download` → ArrowDown (export buttons)
  - `picture_as_pdf` → FileText (export PDF)
  - `emoji_events` → Trophy (best return)
  - `speed` → Gauge (best sharpe)
  - `analytics` → TrendingUp (empty state)
  - `close` → X (close button)
  - `play_arrow` → Play (mobile FAB)

## Files Changed
- `templates/index.html` — 106 insertions, 27 deletions

## Self-Review Findings
- All Material Icons successfully replaced with Phosphor SVGs
- SVGs use consistent attributes: `width="20" height="20"`, `stroke="currentColor"`, `stroke-width="1.5"`
- All SVGs include `stroke-linecap="round"` and `stroke-linejoin="round"` for Phosphor style
- Empty state icons use larger `width="48" height="48"` for visual prominence
- No remaining `material-symbols-rounded` references found

## Commit
- `30256de` — feat: migrate from Material Icons to Phosphor SVGs
