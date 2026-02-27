# Rubik's Solver — Handover

**Last updated:** Feb 27, 2026
**Branch:** main
**Build status:** Single HTML file, opens in any browser, no build step

---

## Current State

Phase 1 core is complete in `index.html` (978 lines). It's a single HTML file with:

### Working Features
- **3D rendering** — Three.js with rounded cubelets, proper lighting, shadows, dark theme
- **Camera controls** — Orbit (drag empty space), zoom (scroll wheel)
- **Face rotation via drag** — Click and drag on a cube face to rotate that layer
- **Keyboard controls** — R/L/U/D/F/B keys (Shift for counter-clockwise)
- **Button panel** — Toggle with "Controls" button, shows CW/CCW for each face
- **Internal state tracking** — Full 54-sticker state management
- **Scramble** — 20-move random scramble with fast animation
- **Undo/Redo** — Full move history, Ctrl+Z / Ctrl+Shift+Z
- **Move counter** — Displays in top-right
- **Loading screen** — Spinner while Three.js loads

### UI Layout
- Top bar: logo + Controls toggle + Help button
- Center: 3D cube (full screen behind UI)
- Bottom bar: Undo/Redo/Reset + Scramble/Solve buttons + toggleable face controls

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
