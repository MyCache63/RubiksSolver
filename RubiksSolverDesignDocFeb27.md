# Rubik's Solver Design Document
**Date:** February 27, 2026
**Status:** Interim Analysis — Pre-Implementation

---

## Executive Summary

We're building a web-based 3D Rubik's Cube that's more fun, more beautiful, and smarter than anything currently available. After researching the top 10+ existing implementations, we've identified what works, what doesn't, and where the gaps are. This document captures those findings and lays out our approach.

---

## Competitive Landscape

### What's Out There (Ranked)

#### Tier 1 — Best in Class
| App | Strengths | Weaknesses |
|-----|-----------|------------|
| **Ruwix** (ruwix.com) | Most feature-rich solver. Kociemba algorithm (20 moves max). Camera scanning, 3D + unfolded views. | Cluttered UI, dated visuals, not mobile-first |
| **cubing.js / Twizzle** (js.cubing.net) | Most sophisticated open-source library. Drop-in web component. Supports many puzzle types. | Developer-focused, not consumer-friendly |
| **Cuber / iamthecu.be** (Google Doodle) | Beautiful CSS3D rendering. Clean state/visual separation. Console API. | No solver built in. Aging codebase. |

#### Tier 2 — Solid but Limited
| App | Strengths | Weaknesses |
|-----|-----------|------------|
| **Grubiks** | Great beginner UX. Step-by-step guided solving. Supports 2x2 to 7x7. | No 3D interaction beyond rotation. Basic visuals. |
| **Cubzor** | Teaches multiple methods (CFOP, Roux, ZZ). Practice modes. | Limited solver capability |
| **AnimCubeJS** | 46 configurable parameters. Lightweight, zero dependencies. | Not interactive — it's an animation engine, not a simulator |

#### Tier 3 — Notable GitHub Projects
- **dejwi/rubiks-app** — Next.js + Three.js + camera scanning. Modern stack but incomplete.
- **Aaron-Bird/rubiks-cube** — Three.js + TypeScript. Clean code, limited features.
- **Edd Mann's Rust/WASM solver** — Clever architecture (Rust for speed, Three.js for visuals). Proves WASM approach works.

### Key Takeaway
Nobody has combined **stunning visuals + intuitive controls + smart solving + teaching + fun** in one package. That's our lane.

---

## What Users Hate About Existing Apps

1. **Color input is painful** — Painting 54 stickers one by one is the #1 complaint
2. **"Invalid scramble" with no explanation** — Solvers reject input without saying why
3. **Solutions are just move dumps** — "R U R' U'" means nothing to beginners
4. **Touch controls are imprecise** — Hard to tell "rotate face" from "rotate cube" on mobile
5. **Solver takes forever to initialize** — Kociemba needs 2-5 seconds of setup with no feedback
6. **Memory hogs** — Web solvers average 182 MB RAM vs 47 MB for native apps
7. **Ad-infested** — Free solvers are buried in ads
8. **No offline support** — Most require internet

---

## Our Approach

### Technology Stack

| Layer | Choice | Why |
|-------|--------|-----|
| **Rendering** | Three.js (vanilla, no React) | Single HTML file requirement. Three.js is the gold standard for WebGL. Smaller bundle than React Three Fiber. |
| **3D Features** | RoundedBoxGeometry, proper lighting, shadows | Realistic beveled cubelets, depth, polish |
| **Solving Engine** | Custom Kociemba two-phase (in Web Worker) | Non-blocking solve. 20-move optimal solutions. |
| **Animation** | Built-in Three.js + custom easing | Smooth rotation with natural-feeling easing curves |
| **UI Framework** | Vanilla HTML/CSS/JS | Zero dependencies beyond Three.js. Single file deployment. Fast loading. |

### Why a Single HTML File?
The user asked for "an HTML program." We're delivering one file that works by opening it in any browser. No build step, no npm install, no server needed. Three.js loaded from CDN.

---

## Feature Design

### 1. 3D Cube Rendering
- **Rounded cubelets** with beveled edges (not sharp boxes)
- **Ambient + directional lighting** with subtle shadows between pieces
- **Anti-aliased WebGL** rendering
- **Stickerless look** (colored plastic) as default, with stickered option
- **Gap between cubelets** for realism

### 2. Camera Controls
- **Left-click drag on empty space** → rotate entire cube
- **Scroll wheel** → zoom in/out
- **Pinch gesture** → zoom on mobile
- Right-click or two-finger drag → pan (optional)

### 3. Face Rotation (The Hard UX Problem)
After researching how the best apps handle this, our approach:

**Option A — Click + Drag on Face (Primary)**
- Click a sticker, drag in the direction you want to rotate
- System detects which layer and axis from the drag vector
- Visual arrow hint appears during drag
- Works on both desktop and mobile

**Option B — Button Controls (Accessibility Fallback)**
- Panel showing all 6 faces (U, D, L, R, F, B)
- Each face has clockwise and counterclockwise buttons
- Clear visual labels ("Top →" "Top ←")
- Great for beginners who aren't comfortable with drag gestures

**Option C — Keyboard (Power Users)**
- Standard notation: R, L, U, D, F, B for clockwise
- Shift+key for counterclockwise
- Shown in a small help overlay

### 4. Color Palettes
- **Classic** — Standard Rubik's colors (white, yellow, red, orange, blue, green)
- **Neon** — Bright fluorescent colors on dark background
- **Pastel** — Soft, muted tones
- **Monochrome** — Grayscale with pattern/texture differentiation
- **High Contrast** — Accessibility-focused, colorblind-safe
- **Custom** — User picks 6 colors with a color picker

### 5. Scramble
- **Visual scramble animation** at adjustable speed (slow, medium, fast, instant)
- Each move saved to an undo stack
- Random scramble uses WCA-standard scramble generation (not just random moves)
- Scramble depth selector (number of moves: 5, 10, 15, 20, 25)
- **"Movie mode"** — scramble with dramatic camera angles and sound effects

### 6. Undo System
- Every move (user or scramble) pushed to a history stack
- **Undo button** pops last move and animates the reverse
- **Redo button** for moves that were undone
- **Full history timeline** — scrubber bar showing all moves, click to jump to any point
- **Reset** — return to solved state (with confirmation)

### 7. Solving Modes

#### A. Auto-Solve (Computer Solves It)
- **Smart Solve** — Kociemba algorithm finds near-optimal solution (≤20 moves)
- **Beginner Method** — Layer-by-layer, more moves but easier to follow
- **CFOP** — Cross → F2L → OLL → PLL (speedcuber method)
- Animated step-by-step with:
  - Plain English explanation of each step ("Now we're matching the white corners")
  - Move notation shown alongside
  - Highlighting of relevant pieces
  - Play/pause/step controls
  - Speed adjustment

#### B. Assisted Solve (Hints)
- User makes moves manually
- "Hint" button suggests the next move
- Shows which pieces to focus on
- Gentle teaching mode — explains the strategy, not just the move

#### C. Solve My Cube (Manual Input)
This is where most apps fail. Our approach:

**Input Methods (user picks one):**
1. **3D Painting** — Click a color from palette, click stickers on the 3D cube to paint them. Rotate cube to reach all faces.
2. **Unfolded Net** — All 6 faces shown flat in a cross layout. Paint all 54 stickers without rotating. Center stickers pre-filled (they define face identity).
3. **Click-to-Cycle** — Click any sticker to cycle through colors. No palette needed.

**Validation (the secret sauce):**
- Real-time validation as user paints:
  - Color counter shows "Red: 8/9" so they know what's missing
  - Impossible pieces highlighted immediately (e.g., two same colors on one edge)
  - Clear error messages: "You have 10 red stickers — a valid cube needs exactly 9 of each"
- Full mathematical validation before solving:
  - Edge/corner permutation parity check
  - Corner orientation sum (must be multiple of 3)
  - Edge flip parity (must be even)
  - All 12 edges and 8 corners must be unique valid pieces
- If invalid: explain WHAT's wrong and suggest the cube may have been reassembled incorrectly

### 8. Fun Extras
- **Patterns** — Apply known pretty patterns (checkerboard, snake, flowers, superflip)
- **Timer** — Speedcubing timer with scramble generation
- **Move counter** — Current moves, efficiency rating
- **Confetti animation** on solve completion
- **Sound effects** — Satisfying click sounds on rotation (toggle on/off)
- **Dark/Light theme** toggle

---

## Solving Algorithm Deep Dive

### Kociemba Two-Phase Algorithm
This is the industry standard. Here's how it works in plain English:

**Phase 1:** Get the cube into a "half-solved" state where only certain moves are needed (reduces the problem space from 43 quintillion positions to about 20 million)

**Phase 2:** From that restricted state, find the shortest path to solved

**Performance:** Typically finds solutions of 18-20 moves. God's Number (the mathematical maximum needed) is 20.

### Implementation Plan
- Use the `cubejs` npm library (MIT licensed) as our solving engine
- Run it in a **Web Worker** so the UI never freezes
- Show a progress indicator during the 2-3 second initialization
- Cache the solver tables in localStorage after first init (instant subsequent loads)

### For Teaching Methods (CFOP, Beginner)
- Implement step-by-step solving as a series of sub-goals
- Each sub-goal solved independently with its own algorithm set
- Annotate each step with plain-English explanation

---

## Visual Design Direction

### Look and Feel
- **Dark background** (deep charcoal/navy) with the cube as the hero
- **Soft ambient glow** around the cube
- **Glass-morphism** UI panels (frosted glass effect)
- **Smooth animations** everywhere — no jarring transitions
- **Micro-interactions** — buttons respond to hover/press with subtle animations
- **Typography** — Clean, modern sans-serif (Inter or similar from Google Fonts)

### Layout
```
┌─────────────────────────────────────────────┐
│  Logo    [Theme] [Palette] [Settings]  [?]  │
├─────────────────────────────────────────────┤
│                                             │
│                                             │
│              ┌───────────┐                  │
│              │           │                  │
│              │   3D CUBE │                  │
│              │           │                  │
│              └───────────┘                  │
│                                             │
│  [Undo] [Redo]  ▶ ━━━━━━━━━━━━  [Reset]   │
│                   move timeline              │
├─────────────────────────────────────────────┤
│  [Scramble ▾] [Solve ▾] [My Cube] [Timer]  │
│                                             │
│  Face Controls:  U↻ U↺  D↻ D↺  ...        │
└─────────────────────────────────────────────┘
```

### Mobile Layout
- Cube fills most of the screen
- Controls in a collapsible bottom drawer
- Swipe up for more options
- Face rotation via direct touch on cube

---

## What Makes Ours Better

| Feature | Best Existing | Ours |
|---------|---------------|------|
| **Visuals** | Functional but dated | Stunning — rounded cubelets, glow, glass UI, dark theme |
| **Face Rotation** | Drag only (confusing on mobile) | Drag + button panel + keyboard — user picks their preference |
| **Color Input** | Paint one sticker at a time, bad error messages | Real-time validation, color counter, multiple input methods |
| **Solving** | Dump a move sequence | Animated step-by-step with plain English explanations |
| **Teaching** | Separate tutorial pages | Built-in hint system that teaches as you solve |
| **Fun Factor** | None — purely utilitarian | Confetti, sounds, speed modes, patterns, timer |
| **Deployment** | npm install, build, serve | Open one HTML file in a browser. Done. |
| **Offline** | Usually requires internet | Works completely offline after first load |

---

## Implementation Plan

### Phase 1 — Core (Build First)
1. 3D cube rendering with Three.js (rounded cubelets, lighting, shadows)
2. Camera controls (orbit, zoom)
3. Face rotation with animation (drag + buttons + keyboard)
4. Internal state management (track all 54 stickers)
5. Scramble with undo history
6. Color palette system

### Phase 2 — Solving
7. Kociemba solver in Web Worker
8. Animated step-by-step playback
9. Beginner method with explanations
10. "Solve My Cube" input interface with validation

### Phase 3 — Polish
11. Sound effects and confetti
12. Timer mode
13. Pattern library
14. Dark/light theme
15. Mobile optimization
16. Offline support (service worker)

---

## Open Questions

1. **Should we support cubes larger than 3x3?** (2x2, 4x4, etc.) — Could add later but increases complexity significantly
2. **Camera scanning for "Solve My Cube"?** — Would be amazing but webcam color detection is unreliable. Could be a stretch goal.
3. **Multiplayer/sharing?** — Share a scramble with a friend, race to solve. Fun but adds server requirements.
4. **Sound design** — Record real cube sounds or use synthesized clicks?

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Three.js CDN goes down | Bundle a local fallback copy |
| Kociemba solver too slow on old phones | Provide "quick solve" option with simpler algorithm |
| Single HTML file gets too large | Acceptable up to ~500KB. Three.js loaded from CDN keeps our file small. |
| Touch controls feel wrong | Extensive testing on real devices. Button fallback always available. |

---

## Next Steps

1. Build Phase 1 core (3D cube + controls + scramble)
2. Test on desktop and mobile browsers
3. Add solving engine
4. Polish and ship to GitHub

---

*This is a living document. Will be updated as implementation progresses.*
