# Rubik's Solver — Handover

**Last updated:** Feb 27, 2026
**Branch:** main
**Build status:** Single HTML file, opens in any browser, no build step

---

## Current State

Phase 1 core + controls enhancement in `index.html` (~1196 lines). Single HTML file with:

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

### UI Layout
- Top bar: logo + Controls toggle + Help button
- Center: 3D cube (full screen behind UI)
- Bottom bar: Undo/Redo/Reset + Scramble/Speed/Solve buttons + toggleable face controls

---

## What's Next (Phase 2 — Solving)

1. **Kociemba solver in Web Worker** — cubejs library, non-blocking
2. **Animated step-by-step solve playback** — play/pause/step controls
3. **Beginner method with explanations** — layer-by-layer with plain English
4. **"Solve My Cube" input** — Paint stickers on 3D cube or unfolded net

## What's After That (Phase 3 — Polish)

5. Sound effects + confetti on solve
6. Timer mode
7. Pattern library (checkerboard, etc.)
8. Color palette switching
9. Mobile optimization
10. Offline support

---

## Known Issues / Notes

- Solve button shows placeholder alert (solver not yet implemented)
- Dynamic face mapping uses `camera.up` vector — works correctly with OrbitControls but if camera flips upside-down the mapping may be unexpected
- Up/Down arrow keys tilt 30° (not 90°) to avoid camera flip issues
- Cube state tracking and 3D visual state are maintained separately — both update on each move, but no sync-check exists yet
- Touch drag on mobile may need tuning (works but sensitivity may need adjustment)
- No service worker yet (requires server for offline — fine for now since it's a local file)

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
