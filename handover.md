# Rubik's Solver — Handover

**Last updated:** Mar 01, 2026
**Branch:** main
**Build status:** Single HTML file, opens in any browser, no build step

---

## Current State

Phase 1 + Phase 2A + Show Off Mode + Cube Crawler implemented in `index.html` (~4183 lines). Single HTML file with:

### Working Features
- **3D rendering** — Three.js with rounded cubelets, proper lighting, shadows, dark theme
- **Camera controls** — Orbit (drag empty space), zoom (scroll wheel)
- **Arrow key camera rotation** — Left/Right rotate view 90° horizontally, Up/Down tilt 30° vertically
- **Spacebar snap** — Snaps camera to nearest clean 3-face viewing angle (8 corner positions)
- **Face rotation via drag** — Click and drag on a cube face to rotate that layer
- **Dynamic face mapping** — Keyboard F/R/L/U/D/B are camera-relative (F = the face you're looking at)
- **Button panel** — Toggle with "Controls" button, buttons use relative labels (Front, Back, etc.)
- **Speed selector** — Dropdown next to Scramble: Slow (400ms), Medium (200ms), Fast (80ms), Instant (1ms)
- **Internal state tracking** — Full 54-sticker state management
- **Scramble** — 20-move random scramble, speed controlled by dropdown
- **Undo/Redo** — Full move history, Ctrl+Z / Ctrl+Shift+Z
- **Move counter** — Displays in top-right
- **Loading screen** — Spinner while Three.js loads
- **Whole-cube rotation** — X/Y/Z keys rotate entire cube (Shift for reverse)
- **Flip button** — Flips cube upside-down (x2 rotation) — quick way to get yellow on top
- **Kociemba solver** — cubejs library loaded from CDN, initializes on page load (~4-5 sec)
- **Solution playback** — Step forward/back, play/pause auto-advance, move token display with highlighting
- **Guard rails** — Manual moves blocked during solution playback
- **Debug log toggle** — "Log" button in top bar shows/hides debug panel (hidden by default)
- **Show Off Mode** — Multi-cube grid display (1×1 to 5×5) with:
  - Grid preset buttons (1, 2×2, 3×3, 4×4, 5×5)
  - Scramble All — synchronized turn-by-turn scrambling across all cubes
  - Solve All — synchronized solving with Kociemba algorithm
  - Confetti — particle physics burst from all cube faces on solve completion
  - Continuous play — each cube independently cycles scramble → solve → confetti on a shared beat (v1.0.5)
  - Own speed selector (Medium/Fast/Instant)
  - Camera auto-zooms to fit grid
  - Normal mode completely isolated — enter/exit cleanly
- **Cube Crawler Mode** (v1.0.6, enhanced v1.0.9) — Game mode where cube crawls across a tile floor:
  - Cube moves by spinning two opposing face layers simultaneously (like wheels)
  - Arrow keys steer: Right=F+B', Left=F'+B, Up=R'+L, Down=R+L'
  - Space bar does lazy-susan spin (top 2 layers rotate, bottom stays put)
  - Tab key does spin1 (top layer only, U face rotation)
  - **Resizable grid** — 3×3, 5×5, 8×8 (default) with grid size buttons
  - **Wood chess board floor** — burlywood/saddle brown tiles, semi-transparent (see cube underside)
  - **Visited tiles glow gold** (FFD700/DAA520) with increased opacity
  - **Move counter** — tracks all moves, resets on Reset/Scramble
  - Demo button runs autonomous snake-zigzag covering all tiles
  - **Scramble button** — moves cube to center, applies scaled random moves (3×3→8, 5×5→10, 8×8→26)
  - **Solve button** — history reversal solver (cube crawls back along its path to solved state)
  - **Step mode** — Speed=Step enters step-through solving with forward/back buttons + arrow keys
  - Switching Step→Slow/Medium/Fast mid-solve auto-continues remaining moves
  - Speed selector (Slow/Medium/Fast/Step)
  - Reset puts cube back at start with fresh floor
  - Fog reduced in crawler mode so far tiles are visible
  - Mode conflicts prevented (can't enter Show Off while in Crawler and vice versa)

### UI Layout
- Top bar: logo + Controls toggle + Show Off button + Crawler button + Log toggle + Help button
- Center: 3D cube (full screen behind UI)
- Bottom bar: Undo/Redo/Reset + Scramble/Speed/Solve/Flip buttons + solution bar (when solving) + toggleable face controls
- Show-off bar (replaces bottom bar in show-off mode): Grid buttons + Scramble All/Speed/Solve All + Continuous toggle + Exit
- Crawler bar (replaces bottom bar in crawler mode): Demo/Scramble/Solve/Speed/Reset/Exit + status text
- Solver status overlay: centered messages that auto-hide

---

## What's Next

1. **IDA* direct crawler solver** — search for optimal (shorter) crawler solutions instead of history reversal
2. **Beginner method with explanations** — layer-by-layer with plain English
3. **CFOP method** — advanced solver option
4. **"Solve My Cube" input** — Paint stickers on 3D cube or unfolded net
5. **Assisted solve / hints** — show next move suggestions
6. **Web Worker for solver init** — avoid blocking main thread

## What's After That (Phase 3 — Polish)

6. Sound effects on moves/solve
7. Timer mode
8. Pattern library (checkerboard, etc.)
9. Color palette switching
10. Mobile optimization
11. Offline support

---

## Known Issues / Notes

- cubejs solver init takes ~1 second — button shows "Solve (loading...)" until ready
- **Solver uses move strings, not facelets** — v1.0.4 fix: our cubeState→facelet conversion had bugs (invalid permutations). Now we send the move history (e.g. "R U F' D2 B") to the worker and let cubejs reconstruct the state via Cube.move(). Guaranteed valid.
- Show Off mode uses Web Worker for solver (main thread stays responsive)
- Show Off animations centralized in main tick() loop — all cubes animated from single rAF, no per-cube callbacks
- Show Off with 5×5 (25 cubes, 675 cubies) may be slow on older phones — needs device testing
- Crawler mode: CrawlerCube class has its own animation system (dual-pivot for crawl, single-pivot for spin)
- Crawler mode reduces fog density from 0.02 to 0.005, restores on exit
- Dynamic face mapping uses `camera.up` vector — works correctly with OrbitControls but if camera flips upside-down the mapping may be unexpected
- Up/Down arrow keys tilt 30° (not 90°) to avoid camera flip issues
- Cube state tracking and 3D visual state are maintained separately — cubeState used for display, moveHistory used for solver
- Main cube solver uses move strings (cubeState→facelet had bugs); Crawler solver uses history reversal (v1.0.13)
- **Crawler solver approach**: Reverses crawlerHistory (inverting each move) to solve. BFS research proved that individual face moves (R,L,F,B) are impossible with crawler generators due to the opposite-face coupling constraint. History reversal is guaranteed correct and shorter than macro substitution would have been.
- Touch drag on mobile may need tuning (works but sensitivity may need adjustment)
- No service worker yet (requires server for offline)
- Whole-cube rotation NOT recorded in undo history (it's orientation, not a solve move)
- Solution playback moves NOT recorded in undo history

---

## Deployment

- **GitHub Pages:** Enable at https://github.com/MyCache63/RubiksSolver/settings/pages → Deploy from main branch
- **URL:** https://mycache63.github.io/RubiksSolver/
- **Local testing:** `python3 -m http.server 8000` then open on phone via local IP

---

## Key Files

| File | Purpose |
|------|---------|
| `index.html` | The entire app — single file |
| `RubiksSolverDesignDocFeb27.md` | Full design document |
| `start_rubikssolver.sh` | Launch local dev server (or just open index.html) |
| `run_next_rubikssolver.sh` | Utility commands (open, size, validate) |
| `crawler_macros.py` | BFS research — proved crawler macro substitution impossible |
| `SolutionForConvertingRubiksMovesToCrawlerNotationMarch12026.md` | Research paper on crawler ↔ standard notation |
| `handover.md` | This file |

---

## Git Tags

- `before-initial-build-feb27` — Before any code was written
- `before-dynamic-controls-feb27` — Before adding dynamic controls, speed selector, arrow keys, snap view
- `before-phase2a-feb27` — Before Phase 2A (solver + whole-cube rotation)
- `before-showoff-mode-feb27` — Before Show Off mode implementation
- `before-solver-move-fix-feb28` — Before v1.0.4 solver move-string fix
- `before-continuous-pipeline-feb28` — Before v1.0.5 independent cube pipelines
- `before-crawler-feb28` — Before v1.0.6 Cube Crawler mode
- `before-crawler-autosolve-feb28` — Before v1.0.8 Crawler auto-solve
- `before-crawler-enhancements-feb28` — Before v1.0.9 Crawler enhancements (step mode, chess board, resizable grid, counter)
- `before-facelet-solver-mar01` — Before v1.0.12 facelet-based Kociemba solver for Crawler
- `before-crawler-bfs-macros-mar01` — Before v1.0.13 crawler BFS research + history reversal solver
