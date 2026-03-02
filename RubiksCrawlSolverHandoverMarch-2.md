# Rubik's Crawler Solver Research — Handover March 2, 2026

## TL;DR

The 10 extended crawler generators generate the **entire Rubik's cube group** (43,252,003,274,489,856,000 states). Every standard face move (R, L, F, B, D) is theoretically expressible as a crawler sequence — but the sequences are impractically long. **History reversal remains the best solver** for the game.

---

## The 12 Crawler Moves (Game v1.0.14)

### Original 8 (from v1.0.6)
| Move | Key | Effect | Notation |
|------|-----|--------|----------|
| `+x` | Right arrow | Roll forward (F CW + B CCW) | F·B' |
| `-x` | Left arrow | Roll backward (F CCW + B CW) | F'·B |
| `+z` | Up arrow | Roll right (R CCW + L CW) | R'·L |
| `-z` | Down arrow | Roll left (R CW + L CCW) | R·L' |
| `spin2` | Space | Lazy susan CW (U + middle layer) | U·E' |
| `spin2'` | Shift+Space | Lazy susan CCW | U'·E |
| `spin1` | Tab | Top layer only CW | U |
| `spin1'` | Shift+Tab | Top layer only CCW | U' |

### 4 New Same-Direction Spins (v1.0.14)
| Move | Key | Effect | Notation |
|------|-----|--------|----------|
| `fb_spin` | Q | Front+Back both CW (from their own perspective) | F·B |
| `fb_spin'` | Shift+Q | Front+Back both CCW | F'·B' |
| `lr_spin` | E | Left+Right both CW (from their own perspective) | L·R |
| `lr_spin'` | Shift+E | Left+Right both CCW | L'·R' |

All 12 moves: Shift reverses direction. All are self-contained (no grid translation for spins).

---

## Macro Discovery Results

### What We Found

| Standard Move | Crawler Macro | Length | How Found |
|---------------|---------------|--------|-----------|
| **U** | `spin1` | 1 move | Direct generator |
| **U'** | `spin1'` | 1 move | Direct generator |
| **F²** | `fb_spin'` then `-x` | 2 moves | Algebraic: F'B' · FB' = F² |
| **B²** | `fb_spin` then `-x` | 2 moves | Algebraic: FB · FB' = B² |
| **R²** | `lr_spin` then `-z` | 2 moves | Algebraic: LR · RL' = R² |
| **L²** | `lr_spin'` then `-z` | 2 moves | Algebraic: L'R' · RL' = L² |
| **D** | Not found | >28 moves | BFS to depth 14 in half-turn metric exhausted |
| **D'** | Not found | >28 moves | Same |
| **R, R'** | Not found | Very long | MITM to depth 7+7=14 exhausted |
| **L, L', F, F', B, B'** | Not found | Very long | Same reasoning as R |

### Why Individual Quarter-Turns Are Hard

The original 4 crawl moves always rotate **opposite faces as a pair** (F+B' or R+L'). The new same-direction spins also pair opposite faces (F+B or L+R). You can never apply R without also applying L (or L'). So building an isolated R requires very long commutator sequences to cancel out the L component.

The half-turn F² works because F·B' · F·B = F²·B'·B = F²·I = F². The B components cancel. But for quarter-turns, there's no clean cancellation.

---

## Group Theory Results

### Group Orders (SymPy Verified)

| Generator Set | Group Order | Notes |
|---------------|-------------|-------|
| Original 6: {+x, -x, +z, -z, spin1, spin1'} | 43,252,003,274,489,856,000 | = Full Rubik's group! |
| Extended 10: (original + 4 same-dir spins) | 43,252,003,274,489,856,000 | Same (spins are redundant for group) |
| Half-turn: {U, U', F², B², R², L²} | 19,508,428,800 | Half-turn subgroup (index 2) |

### Key Finding
The **original 6 generators already generate the full Rubik's group**. The 4 new same-direction spins don't expand the group — they just provide shortcuts (F² in 2 moves instead of many).

### Membership Tests
- D ∈ ⟨U, F², B², R², L²⟩ — **YES** (confirmed by SymPy), but distance >14 in half-turn metric
- R, L, F, B ∈ ⟨all 10 generators⟩ — **YES** (confirmed), but impractically long sequences
- R, L, F, B ∈ ⟨U, F², B², R², L²⟩ — **NO** (quarter-turns not in half-turn subgroup)

---

## Corner BFS Solver (Working)

### What It Does
Phase 1 of a two-phase solver. BFS from solved corners through all 88,179,840 corner states using the original 6 generators.

### Results
- **All 88,179,840 corner states reachable** (0 unreachable)
- **God's number for corners = 26** (maximum moves needed)
- BFS build time: ~29 minutes in Python
- Memory: ~176 MB (2 bytes per state: depth + parent move)

### Verified Solutions
| Test Case | Corner Solution Length | Sequence |
|-----------|----------------------|----------|
| R applied | 3 moves | `-x spin1' +x` |
| D applied | 4 moves | `spin1' +x -z -x` |
| Random 20-move scramble | 12 moves | (varies) |

### Edge Solver Status: INCOMPLETE
After corners are solved, edges still need fixing. The edge-only commutators from commutator mining generate only **128 of 239,500,800** possible edge permutations — far too limited. A full edge solver would need:
- Longer commutator sequences (length 3+), or
- Corner-preserving IDA* search, or
- A completely different approach

The corner BFS table is still useful as a **heuristic** for future IDA* solvers.

---

## Commutator Mining Results

### Method
Generated all commutators [A, B] = A·B·A⁻¹·B⁻¹ where A and B are sequences of length 1-2 using all 10 extended generators. Also computed nested commutators [[A,B], C].

### Results
| Category | Count | Notes |
|----------|-------|-------|
| Total unique commutators | 4,050 direct + 42 nested | |
| Corner-only operations | 0 | None found at this depth |
| Edge-only operations | 13 | All are 2-cycle pairs, no orientation change |
| Edge 3-cycles | 64 | But they also move corners (not edge-only) |
| Pure corner twists | 0 | |
| Pure edge flips | 0 | |

### Edge-Only Operations (the 13)
All are products of 2-cycle pairs with zero orientation change. They generate a group of order 128 = 2⁷. Examples:
- `[fb_spin, +z+z]` (6 moves): swaps edges 0↔6, 2↔4, 8↔10, 9↔11
- `[lr_spin, +x+x]` (6 moves): swaps edges 1↔7, 3↔5, 8↔9, 10↔11
- `[spin1², fb_spin·lr_spin]` (8 moves): swaps edges 0↔2, 8↔11

Library saved to `commutator_library.json`.

---

## Bug Fixes Applied

### 1. make_U() and make_D() Side Sticker Cycles (crawler_macros.py)

**Problem:** The `face_cw()` function rotates face stickers CW on the 2D grid. For the U face, this corresponds to CW from above. But the OLD side sticker cycles went CCW from above (F→R→B→L instead of F→L→B→R). This caused corner pieces to be **split** — the U sticker of a corner went to one slot while the R and F stickers went to a different slot.

**Diagnosis:**
```
OLD make_U: face cycle = URF→ULF (CW), side cycle = URF→URB (CCW) → SPLIT!
NEW make_U: face cycle = URF→ULF (CW), side cycle = URF→ULF (CW) → INTACT!
```

**Fix:** Reversed the side sticker assignment in make_U and make_D:
```python
# OLD (broken):
perm[cycle[0][i]] = cycle[3][i]  # F←L
perm[cycle[1][i]] = cycle[0][i]  # R←F
perm[cycle[2][i]] = cycle[1][i]  # B←R
perm[cycle[3][i]] = cycle[2][i]  # L←B

# NEW (correct):
perm[cycle[0][i]] = cycle[1][i]  # F←R
perm[cycle[1][i]] = cycle[2][i]  # R←B
perm[cycle[2][i]] = cycle[3][i]  # B←L
perm[cycle[3][i]] = cycle[0][i]  # L←F
```

**Verification:** All 6 face moves now pass:
- Corner integrity test (all 3 stickers stay in same corner slot)
- Order 4 test (move⁴ = identity)
- Corner state extraction matches between abstract tracking and 54-sticker tracking

### 2. compose() Order Convention (phase_decompose.py)

**Problem:** Test code used `compose(gen, state)` instead of `compose(state, gen)`.

**The Convention:**
```python
compose(a, b)[i] = a[b[i]]
```
With `apply_perm`'s pulls-from convention:
```python
apply_perm(apply_perm(state, a), b) == apply_perm(state, compose(a, b))
```
So `compose(a, b)` = "apply a first, then b" in state-tracking terms.

**Fix:** Changed 4 lines in phase_decompose.py verification tests from `compose(EXTENDED_GENERATORS[m], state)` to `compose(state, EXTENDED_GENERATORS[m])`.

### 3. compose() Docstring (crawler_macros.py)

Updated from misleading "Apply b first, then a" to a clear explanation of both the mathematical and practical conventions.

---

## Tilt Analysis (Backup Approach)

### Concept
If we add whole-cube rotation (tilt) as a game mechanic, every face move becomes 3 moves:
```
face_move = tilt · U · tilt_back
```

### Results
All 12 face moves (R, R', L, L', F, F', B, B', D, D', U, U') achievable via tilt conjugation in exactly 3 game moves.

### Why We Didn't Use It
- Tilts move center stickers (they're NOT in the Rubik's cube group)
- Requires changing game physics (cube lifts off floor, rotates, sets back down)
- Changes the fundamental feel of the crawler game
- History reversal is simpler and already works

---

## File Inventory

### Game
| File | Purpose |
|------|---------|
| `index.html` | The entire game (v1.0.14, ~4300 lines) |

### Research Scripts (Python)
| File | Purpose | Status |
|------|---------|--------|
| `crawler_macros.py` | Base permutation definitions (U, D, R, L, F, B, crawl moves) | **Fixed** (make_U/make_D bug) |
| `crawler_extended.py` | Extended generators (same-direction spins) + verification | Complete |
| `group_analysis.py` | SymPy group order computation | Complete |
| `compute_corner_effects.py` | Corner/edge piece tracking from 54-sticker permutations | Complete |
| `commutator_mine.py` | Systematic commutator enumeration | Complete |
| `phase_decompose.py` | Corner BFS table (88M states) + corner solver | **Working** (edge solver incomplete) |
| `find_R_halfturn.py` | BFS/MITM search for D and R in half-turn metric | Complete (D not found at depth 14) |
| `tilt_analysis.py` | Whole-cube rotation feasibility analysis | Complete |
| `commutator_library.json` | Saved commutator catalog | Generated by commutator_mine.py |

### Other Research Scripts (earlier attempts, not actively used)
`find_macros*.py`, `find_R_*.py`, `decompose_*.py`, `verify_*.py`, `idastar_*.c`, etc. — Various BFS, IDA*, MITM, and algebraic approaches tried during the search for face move macros. None found practical results beyond what's documented above.

---

## Solver Strategy Summary

### Current (v1.0.14): History Reversal
1. Every crawler move is recorded in `crawlerHistory`
2. To solve: reverse the history, invert each move
3. Guaranteed correct, solution length = scramble length
4. Works for all 12 move types including the new same-direction spins

### Theoretical Future: Two-Phase + IDA*
1. **Phase 1:** Use corner BFS table (88M entries) to solve corners in ≤26 moves
2. **Phase 2:** Fix edges using corner-preserving operations (NOT YET SOLVED)
3. **Optimization:** The corner BFS table could serve as a heuristic for IDA* on the full state

### Why History Reversal Wins
- Always available (game records all moves)
- Solution length = scramble length (typically 20-60 moves)
- No precomputation needed
- Two-phase solver would give ~26+ moves for corners alone, plus unknown edge cost
- The math shows face moves exist but are too long to be practical

---

## Key Insight

The crawler's coupled-move constraint (opposite faces always paired) means the **generators are highly entangled**. While they DO generate the full group, the "disentangling" required to isolate a single face move takes exponentially many steps. This is fundamentally different from standard Rubik's cube solvers where each generator IS an isolated face move.

The same-direction spins help (giving us half-turns in 2 moves) but don't solve the quarter-turn problem. The gap between "mathematically possible" and "practically computable" is the core challenge of the crawler solver.
