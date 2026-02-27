# Rubik's Solver — Handover

**Last updated:** Feb 27, 2026
**Branch:** main
**Build status:** Single HTML file, opens in any browser, no build step

---

## Current State

Phase 1 + Phase 2A implemented in `index.html` (~1833 lines). Single HTML file with:

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

### UI Layout
- Top bar: logo + Controls toggle + Help button
- Center: 3D cube (full screen behind UI)
- Bottom bar: Undo/Redo/Reset + Scramble/Speed/Solve/Flip buttons + solution bar (when solving) + toggleable face controls
- Solver status overlay: centered messages that auto-hide

---

## What's Next (Phase 2B — Solving Enhancements)

1. **Beginner method with explanations** — layer-by-layer with plain English
2. **CFOP method** — advanced solver option
3. **"Solve My Cube" input** — Paint stickers on 3D cube or unfolded net
4. **Assisted solve / hints** — show next move suggestions
5. **Web Worker for solver init** — avoid blocking main thread

## What's After That (Phase 3 — Polish)

6. Sound effects + confetti on solve
7. Timer mode
8. Pattern library (checkerboard, etc.)
9. Color palette switching
10. Mobile optimization
11. Offline support

---

## Known Issues / Notes

- cubejs solver init takes ~4-5 seconds — button shows "Solve (loading...)" until ready
- Solver runs on main thread — may cause brief freeze on complex solves (Web Worker planned for 2B)
- Dynamic face mapping uses `camera.up` vector — works correctly with OrbitControls but if camera flips upside-down the mapping may be unexpected
- Up/Down arrow keys tilt 30° (not 90°) to avoid camera flip issues
- Cube state tracking and 3D visual state are maintained separately — both update on each move, but no sync-check exists yet
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
| `handover.md` | This file |

---

## Git Tags

- `before-initial-build-feb27` — Before any code was written
- `before-dynamic-controls-feb27` — Before adding dynamic controls, speed selector, arrow keys, snap view
- `before-phase2a-feb27` — Before Phase 2A (solver + whole-cube rotation)
