#!/usr/bin/env python3
"""
tilt_analysis.py — Feasibility check on tilt (whole-cube rotation) moves.

If we allow the cube to tilt (whole-cube X or Z rotation), we can
conjugate spin moves to get isolated single-face quarter-turns:
  tilt · spin · tilt_back = isolated face move

This is a backup approach if commutator mining doesn't yield short macros.
The tradeoff: tilts change which face is "down" (resting on the floor),
which requires different game physics.

Builds whole-cube rotations by composing face moves (guaranteed correct),
rather than trying to hand-build the sticker mappings.
"""

import sys
sys.path.insert(0, '.')
from crawler_macros import (
    IDENTITY, compose, invert, apply_perm,
    U, U_prime, D, D_prime, R, R_prime, L, L_prime,
    F, F_prime, B, B_prime, E, E_prime,
    CRAWL_PX, CRAWL_MX, CRAWL_PZ, CRAWL_MZ,
    SPIN1, SPIN1_P, SPIN2, SPIN2_P,
)

def log(msg):
    print(msg, flush=True)

# ─── Build whole-cube rotations from face moves ───
# These are correct by construction since they compose known-good permutations.
#
# Standard definitions:
#   y = U · E' · D'  (rotate whole cube CW looking from top)
#     SPIN2 = U · E', so y = compose(D_prime, SPIN2) = "apply SPIN2 then D'"
#     But compose(a, b) = "apply b first then a"
#     So y = compose(D_prime, SPIN2)  ... wait.
#
# Let me be very careful with compose.
# compose(a, b)[i] = a[b[i]]: means "apply b first, then a to the result"
#
# SPIN2 = compose(U, E_prime) means "apply E' first, then U"
# We want y = "apply E' first, then U, then D'" (all three layers CW from top)
# = compose(D_prime, compose(U, E_prime))
# = compose(D_prime, SPIN2)

# But wait: D_prime rotates D face CCW (looking at D from below) = CW from above.
# For y rotation (CW from top): U layer CW + middle layer CW + D layer CW-from-above = D'

WHOLE_Y = compose(D_prime, SPIN2)
WHOLE_Y_P = invert(WHOLE_Y)

# x = R · M' · L'  (rotate whole cube CW looking from right side)
# M is the middle slice between R and L, following L's rotation direction.
# M' = inverse of M = rotates the middle slice in R's direction.
# We don't have M directly, but:
#   x = R · L' · (middle slice in R direction)
# Alternatively: x² = (R · L')² plus middle adjustment... this gets complicated.
#
# Better approach: x maps U→F, F→D, D→B, B→U
# We know that:
#   R CW from right: the R column goes U→F→D→B→U
#   L' CCW from left = CW from right: the L column goes U→F→D→B→U
#   Middle slice in R direction: middle column goes U→F→D→B→U
# So x = R · L' · M_R where M_R is the middle slice moving in R direction.
#
# Since CRAWL_MZ = compose(R, L_prime) = R·L' (apply L' first, then R),
# x = CRAWL_MZ · M_R
# And M_R can be extracted as: M_R = x · (R · L')⁻¹
#
# Alternative: define x via y and z.
# We know x = z' · y · z (or some combination). Actually:
#   x = y' · z · y (no, these don't compose simply)
#
# Simplest correct approach: define x via its effect on solved state and verify.
# Or: use the relationship x = z · y · z' (conjugation).
#
# Actually, the cleanest way: build M_R (middle slice, R direction) explicitly.
# Under R: positions 2,5,8 (U right col) → 20,23,26 (F right col)
# Under M_R: positions 1,4,7 (U middle col) → 19,22,25 (F middle col)
# The pattern is the same as R but shifted one column left.

def make_middle_R():
    """Middle slice rotation in R direction (U→F→D→B→U for middle column)"""
    perm = list(IDENTITY)
    # U middle column: 1,4,7 → F middle column: 19,22,25
    # F middle column: 19,22,25 → D middle column: 28,31,34
    # D middle column: 28,31,34 → B middle column: 52,49,46 (reversed!)
    # B middle column: 52,49,46 → U middle column: 7,4,1 (reversed!)

    # Actually let me look at R's pattern to match:
    # R: u=[2,5,8]; f=[20,23,26]; d=[29,32,35]; b=[51,48,45]
    # perm[u[i]]=f[i]; perm[b[i]]=u[i]; perm[d[i]]=b[i]; perm[f[i]]=d[i]
    # That means: u←f, f←d, d←b, b←u? No, perm is pulls-from:
    # perm[u[i]]=f[i] means "position u[i] gets sticker from position f[i]"
    # So U-right ← F-right, B-right ← U-right, D-right ← B-right, F-right ← D-right
    # In cycle notation (where sticker goes): F→U, U→B, B→D, D→F
    # That's... backwards from what I expected. Let me recheck.
    #
    # Actually, for "CW from right side": U→F, F→D, D→B, B→U
    # In pulls-from notation: U ← B (U position gets sticker that was at B)
    # perm[u] = b, perm[f] = u, perm[d] = f, perm[b] = d
    # But the R code says perm[u[i]]=f[i], meaning U position pulls from F.
    # So R does: U←F, F←D, D←B, B←U
    # In "where does the sticker go" terms: F→U, D→F, B→D, U→B
    # That's actually CCW from the right... or CW from the left? Hmm.
    #
    # Standard R move CW: looking at R face from outside (right side),
    # the URF corner goes to URB. In sticker terms, U-right-col goes to B-right-col.
    # In pulls-from: U-right gets what was at F-right (piece moves U→B, so B gets U,
    # which means B pulls from the position that used to be at... )
    #
    # OK I'm going in circles. Let me just mimic R's pattern for the middle column.

    u = [1, 4, 7]
    f = [19, 22, 25]
    d = [28, 31, 34]
    b = [52, 49, 46]  # reversed, same as R pattern

    for i in range(3):
        perm[u[i]] = f[i]
        perm[b[i]] = u[i]
        perm[d[i]] = b[i]
        perm[f[i]] = d[i]
    return tuple(perm)

MR = make_middle_R()

# x = R · L' · M_R (all three "columns" rotating in R direction)
# In compose notation: compose(a, b) = "apply b first, then a"
# We want to apply all three simultaneously, which is just their composition.
# Since they act on disjoint sets of stickers, order doesn't matter.
WHOLE_X = compose(R, compose(invert(L), MR))
WHOLE_X_P = invert(WHOLE_X)

# z = F · B' · M_F (all three "slices" rotating in F direction)
# For z: looking at F face CW: U→R, R→D, D→L, L→U
# This is the same pattern as F but for the middle slice.
def make_middle_F():
    """Middle slice rotation in F direction (U→R→D→L→U for middle slice)"""
    perm = list(IDENTITY)
    # F moves: u=[6,7,8]; r=[9,12,15]; d=[29,28,27]; l=[44,41,38]
    # Middle slice (between F and B):
    u = [3, 4, 5]
    r = [10, 13, 16]
    d = [32, 31, 30]  # reversed, same pattern as F
    l = [43, 40, 37]  # reversed, same pattern as F

    for i in range(3):
        perm[r[i]] = u[i]
        perm[d[i]] = r[i]
        perm[l[i]] = d[i]
        perm[u[i]] = l[i]
    return tuple(perm)

MF = make_middle_F()
WHOLE_Z = compose(F, compose(invert(B), MF))
WHOLE_Z_P = invert(WHOLE_Z)


def main():
    log("=" * 60)
    log("Tilt Analysis — Whole-Cube Rotation Feasibility")
    log("=" * 60)

    # ─── Verify whole-cube rotations ───
    log("\n--- Validating whole-cube rotations ---")
    for name, perm in [('x', WHOLE_X), ('y', WHOLE_Y), ('z', WHOLE_Z)]:
        assert sorted(perm) == list(range(54)), f"{name} invalid perm!"
        state = IDENTITY
        for k in range(1, 100):
            state = compose(perm, state)
            if state == IDENTITY:
                log(f"  {name}: valid permutation, order {k}")
                assert k == 4, f"{name} should have order 4, got {k}!"
                break

    # Verify that whole-cube rotations move all 6 centers
    log("\n--- Center movement check ---")
    centers = {4: 'U', 13: 'R', 22: 'F', 31: 'D', 40: 'L', 49: 'B'}
    for name, perm in [('x', WHOLE_X), ('y', WHOLE_Y), ('z', WHOLE_Z)]:
        moves = []
        for c, cn in centers.items():
            if perm[c] != c:
                dest = centers.get(perm[c], '?')
                moves.append(f"{cn}→{dest}")
        log(f"  {name}: {', '.join(moves)}")

    # ─── Key conjugation: tilt + spin + tilt-back ───
    log("\n--- Conjugation: tilt · spin · tilt_back = face move ---")
    log("Testing all tilt-spin-tilt conjugations...\n")

    results = {}

    tilts = [
        ('x', WHOLE_X, WHOLE_X_P),
        ("x'", WHOLE_X_P, WHOLE_X),
        ('y', WHOLE_Y, WHOLE_Y_P),
        ("y'", WHOLE_Y_P, WHOLE_Y),
        ('z', WHOLE_Z, WHOLE_Z_P),
        ("z'", WHOLE_Z_P, WHOLE_Z),
        ('x2', compose(WHOLE_X, WHOLE_X), compose(WHOLE_X_P, WHOLE_X_P)),
        ('y2', compose(WHOLE_Y, WHOLE_Y), compose(WHOLE_Y_P, WHOLE_Y_P)),
        ('z2', compose(WHOLE_Z, WHOLE_Z), compose(WHOLE_Z_P, WHOLE_Z_P)),
    ]

    spins = [
        ('U', U),
        ("U'", U_prime),
    ]

    target_faces = {
        'U': U, "U'": U_prime,
        'D': D, "D'": D_prime,
        'R': R, "R'": R_prime,
        'L': L, "L'": L_prime,
        'F': F, "F'": F_prime,
        'B': B, "B'": B_prime,
    }

    for tilt_name, tilt, tilt_inv in tilts:
        for spin_name, spin in spins:
            # conjugation: tilt · spin · tilt_inv
            # = compose(tilt, compose(spin, tilt_inv))
            # This means: first apply tilt_inv, then spin, then tilt
            result = compose(tilt, compose(spin, tilt_inv))
            for face_name, face_perm in target_faces.items():
                if result == face_perm:
                    if tilt_name.endswith('2'):
                        inv_name = tilt_name
                    elif tilt_name.endswith("'"):
                        inv_name = tilt_name[:-1]
                    else:
                        inv_name = tilt_name + "'"
                    recipe = f"{tilt_name} · {spin_name} · {inv_name}"
                    log(f"  {recipe} = {face_name}")
                    if face_name not in results:
                        results[face_name] = recipe

    log("\n--- Face Move Recipes via Tilt ---")
    for face in ['U', "U'", 'D', "D'", 'R', "R'", 'L', "L'", 'F', "F'", 'B', "B'"]:
        if face in results:
            log(f"  {face:3s} = {results[face]} (3 game moves)")
        else:
            log(f"  {face:3s} = NOT achievable via single tilt conjugation")

    # ─── Can tilt be expressed in crawler moves? ───
    log("\n--- Can tilts be expressed as crawler moves? ---")
    log("Tilts move center stickers, so they're NOT in the Rubik's cube group.")
    log("Crawler moves (with centers fixed) cannot produce tilts.")
    log("")
    log("However, tilts COULD be added as a new physical game move:")
    log("  The cube lifts, rotates 90 degrees, and sets back down.")
    log("")

    found_count = sum(1 for f in target_faces if f in results)
    log(f"Found recipes for {found_count}/12 face moves via tilt conjugation.")

    if found_count == 12:
        log("\nWith tilts, EVERY face move = 3 game moves:")
        log("  Kociemba solution (~20 face moves) → ~60 game moves + tilt overhead")
        log("  This is the shortest possible approach but requires changing game physics.")
    elif found_count > 0:
        log("\nPartial coverage — some face moves need multi-tilt conjugation.")
    else:
        log("\nNo matches found — checking if rotation definitions are correct...")
        # Debug: show what the conjugation actually produces
        for tilt_name, tilt, tilt_inv in tilts[:3]:
            for spin_name, spin in spins[:1]:
                result = compose(tilt, compose(spin, tilt_inv))
                moved = sum(1 for i in range(54) if result[i] != i)
                log(f"  {tilt_name} · {spin_name} · {tilt_name}': moves {moved} stickers")
                # Check if it's a face move at all (should move exactly 20 stickers)
                # A single face CW move: 8 face stickers + 12 adjacent stickers = 20
                if moved == 20:
                    log(f"    → Moves 20 stickers (same as a face move)")
                    # Find which positions differ from each target
                    for face_name, face_perm in target_faces.items():
                        diffs = sum(1 for i in range(54) if result[i] != face_perm[i])
                        if diffs < 10:
                            log(f"    → Close to {face_name}: {diffs} positions differ")

    log("\n" + "=" * 60)
    log("SUMMARY")
    log("=" * 60)
    log("")
    log("Tilt feasibility analysis complete.")
    log("Tilts cannot be expressed as crawler moves (they move centers).")
    log("Adding tilt as a new game mechanic would give the shortest solutions")
    log("but fundamentally changes the game's physics and feel.")
    log("")
    log("Recommendation: Focus on commutator mining and direct search first.")
    log("Tilts are the nuclear option — use only if nothing else works.")


if __name__ == '__main__':
    main()
