#!/usr/bin/env python3
"""
crawler_extended.py — Extended crawler generator definitions + verification.

Defines 4 new "same-direction spin" moves where both opposite faces rotate
in the SAME direction (instead of opposite directions like crawl moves).

New generators:
  FB_SPIN   = F·B   (front and back both CW)
  FB_SPIN_P = F'·B' (both CCW)
  LR_SPIN   = L·R   (left and right both CW)
  LR_SPIN_P = L'·R' (both CCW)

Key result: composing a crawl move with a same-direction spin yields a
double (half-turn) of a single face:
  CRAWL_PX · FB_SPIN = (F·B') · (F·B) = F²·(B'·B) = F²
  etc.

This gives us F², B², L², R² in exactly 2 crawler moves each.
"""

import sys
sys.path.insert(0, '.')
from crawler_macros import (
    IDENTITY, SOLVED, apply_perm, compose, invert,
    U, U_prime, D, D_prime, R, R_prime, L, L_prime,
    F, F_prime, B, B_prime, E, E_prime,
    CRAWL_PX, CRAWL_MX, CRAWL_PZ, CRAWL_MZ,
    SPIN1, SPIN1_P, SPIN2, SPIN2_P,
)

def log(msg):
    print(msg, flush=True)

# ─── New same-direction spin generators ───

FB_SPIN   = compose(F, B)           # F·B: front CW + back CW
FB_SPIN_P = compose(F_prime, B_prime)  # F'·B': front CCW + back CCW
LR_SPIN   = compose(L, R)           # L·R: left CW + right CW
LR_SPIN_P = compose(L_prime, R_prime)  # L'·R': left CCW + right CCW

# ─── Half-turn definitions ───

F_squared = compose(F, F)
B_squared = compose(B, B)
R_squared = compose(R, R)
L_squared = compose(L, L)
U_squared = compose(U, U)
D_squared = compose(D, D)

# ─── All 10 extended generators ───

EXTENDED_GENERATORS = {
    '+x':       CRAWL_PX,    # F·B'
    '-x':       CRAWL_MX,    # F'·B
    '+z':       CRAWL_PZ,    # R'·L
    '-z':       CRAWL_MZ,    # R·L'
    'spin1':    SPIN1,       # U
    "spin1'":   SPIN1_P,     # U'
    'fb_spin':  FB_SPIN,     # F·B
    "fb_spin'": FB_SPIN_P,   # F'·B'
    'lr_spin':  LR_SPIN,     # L·R
    "lr_spin'": LR_SPIN_P,   # L'·R'
}

# Inverses for all extended generators
EXTENDED_INVERSES = {
    '+x': '-x', '-x': '+x',
    '+z': '-z', '-z': '+z',
    'spin1': "spin1'", "spin1'": 'spin1',
    'fb_spin': "fb_spin'", "fb_spin'": 'fb_spin',
    'lr_spin': "lr_spin'", "lr_spin'": 'lr_spin',
}


def main():
    log("=" * 60)
    log("Crawler Extended Generators — Verification Report")
    log("=" * 60)

    # ─── 1. Verify new generators are valid permutations ───
    log("\n--- Permutation Validity ---")
    for name, perm in EXTENDED_GENERATORS.items():
        assert sorted(perm) == list(range(54)), f"{name} is not a valid permutation!"
        assert compose(perm, invert(perm)) == IDENTITY, f"{name} · {name}⁻¹ ≠ identity!"
    log("All 10 extended generators: valid permutations, inverses correct ✓")

    # ─── 2. Verify same-direction spin definitions ───
    log("\n--- Same-Direction Spin Definitions ---")
    assert FB_SPIN == compose(F, B), "FB_SPIN should be F·B"
    assert FB_SPIN_P == compose(F_prime, B_prime), "FB_SPIN_P should be F'·B'"
    assert LR_SPIN == compose(L, R), "LR_SPIN should be L·R"
    assert LR_SPIN_P == compose(L_prime, R_prime), "LR_SPIN_P should be L'·R'"
    log("FB_SPIN  = F·B  ✓")
    log("FB_SPIN' = F'·B' ✓")
    log("LR_SPIN  = L·R  ✓")
    log("LR_SPIN' = L'·R' ✓")

    # ─── 3. Verify half-turn compositions ───
    log("\n--- Half-Turn Compositions (the key result) ---")

    # F²: CRAWL_PX · FB_SPIN = (F·B') · (F·B) = F²·I = F²
    # compose(a, b) applies b first then a, so compose(CRAWL_PX, FB_SPIN) = CRAWL_PX(FB_SPIN(x))
    # FB_SPIN = F·B, then CRAWL_PX = F·B'
    # Result: F·B' applied after F·B = F·(B'·(F·B)) ... wait, let's be careful.
    #
    # Our compose(a, b)[i] = a[b[i]], meaning: apply b first, then a.
    # FB_SPIN = compose(F, B) = "apply B first, then F"
    # CRAWL_PX = compose(F, B_prime) = "apply B' first, then F"
    #
    # compose(CRAWL_PX, FB_SPIN) = "apply FB_SPIN first, then CRAWL_PX"
    #   = "apply B then F, then apply B' then F"
    #   = F · B' · F · B
    # That's NOT F². Let me think again...
    #
    # Actually, we want: crawl_px THEN fb_spin (as sequence of moves)
    # In our notation: compose(fb_spin, crawl_px) = fb_spin(crawl_px(x))
    # = "apply crawl_px first (F·B'), then fb_spin (F·B)"
    # = compose(F,B) after compose(F,B')
    # = F·B · F·B' (reading right to left in group theory)
    # Hmm, this is getting confusing. Let me just test all combinations.

    log("\nTesting all crawl + spin combinations for half-turns:")
    log("(Testing both orderings: spin·crawl and crawl·spin)")

    half_turn_recipes = {}  # maps face_squared name -> (move1, move2) crawler recipe

    crawls_fb = [('+x', CRAWL_PX), ('-x', CRAWL_MX)]
    spins_fb = [('fb_spin', FB_SPIN), ("fb_spin'", FB_SPIN_P)]
    crawls_lr = [('+z', CRAWL_PZ), ('-z', CRAWL_MZ)]
    spins_lr = [('lr_spin', LR_SPIN), ("lr_spin'", LR_SPIN_P)]

    targets = {
        'F²': F_squared, 'B²': B_squared,
        'R²': R_squared, 'L²': L_squared,
    }

    for cname, cperm in crawls_fb + crawls_lr:
        for sname, sperm in spins_fb + spins_lr:
            # Try both orderings
            for order, result in [
                (f"{cname} then {sname}", compose(sperm, cperm)),
                (f"{sname} then {cname}", compose(cperm, sperm)),
            ]:
                for tname, tperm in targets.items():
                    if result == tperm:
                        log(f"  {order} = {tname} ✓")
                        half_turn_recipes[tname] = order

    if len(half_turn_recipes) >= 4:
        log("\nAll 4 half-turns found! ✓")
    else:
        missing = set(targets.keys()) - set(half_turn_recipes.keys())
        log(f"\nMissing half-turns: {missing}")
        log("Trying extended search...")

        # Also try composing same-type pairs
        all_gens = list(EXTENDED_GENERATORS.items())
        for i, (n1, p1) in enumerate(all_gens):
            for j, (n2, p2) in enumerate(all_gens):
                result = compose(p2, p1)  # apply p1 first, then p2
                for tname, tperm in targets.items():
                    if tname not in half_turn_recipes and result == tperm:
                        log(f"  {n1} then {n2} = {tname} ✓")
                        half_turn_recipes[tname] = f"{n1} then {n2}"

    log("\n--- Half-Turn Recipe Summary ---")
    for tname in ['F²', 'B²', 'R²', 'L²']:
        if tname in half_turn_recipes:
            log(f"  {tname} = {half_turn_recipes[tname]} (2 crawler moves)")
        else:
            log(f"  {tname} = NOT FOUND in 2 moves")

    # ─── 4. Verify center invariance ───
    log("\n--- Center Invariance Check ---")
    # Positions 4 (U center) and 31 (D center) should be fixed
    # Also check all 6 centers: 4(U), 13(R), 22(F), 31(D), 40(L), 49(B)
    centers = [4, 13, 22, 31, 40, 49]
    center_names = ['U(4)', 'R(13)', 'F(22)', 'D(31)', 'L(40)', 'B(49)']

    all_fixed = True
    for name, perm in EXTENDED_GENERATORS.items():
        fixed = [perm[c] == c for c in centers]
        if not all(fixed):
            moved = [center_names[i] for i, f in enumerate(fixed) if not f]
            log(f"  {name}: moves centers {moved}")
            all_fixed = False
        else:
            log(f"  {name}: all centers fixed ✓")

    if all_fixed:
        log("\nAll generators fix all 6 centers ✓")
    else:
        log("\nSome generators move centers (expected for crawl/spin moves)")
        log("U center (4) and D center (31) specifically:")
        for name, perm in EXTENDED_GENERATORS.items():
            u_fixed = perm[4] == 4
            d_fixed = perm[31] == 31
            log(f"  {name}: U_center={'fixed' if u_fixed else 'MOVES'}, D_center={'fixed' if d_fixed else 'MOVES'}")

    # ─── 5. Generator orders ───
    log("\n--- Generator Orders ---")
    for name, perm in EXTENDED_GENERATORS.items():
        state = IDENTITY
        for k in range(1, 1000):
            state = compose(perm, state)
            if state == IDENTITY:
                log(f"  {name}: order {k}")
                break

    # ─── 6. Summary of what we now have ───
    log("\n" + "=" * 60)
    log("SUMMARY: Extended Crawler Move Set")
    log("=" * 60)
    log("")
    log("Original 6 crawler moves (from the game):")
    log("  +x (F·B'), -x (F'·B)    — roll forward/backward")
    log("  +z (R'·L), -z (R·L')    — roll left/right")
    log("  spin1 (U), spin1' (U')  — top layer rotation")
    log("")
    log("4 NEW same-direction spin moves:")
    log("  fb_spin (F·B), fb_spin' (F'·B')  — front+back same direction")
    log("  lr_spin (L·R), lr_spin' (L'·R')  — left+right same direction")
    log("")
    log("Derived half-turns (2 crawler moves each):")
    for tname in ['F²', 'B²', 'R²', 'L²']:
        recipe = half_turn_recipes.get(tname, "NOT FOUND")
        log(f"  {tname} = {recipe}")
    log("")
    log("Effective move vocabulary:")
    log("  U, U' (1 move each) — from spin1")
    log("  F², B², R², L² (2 moves each) — from crawl+spin combos")
    log("  D, D' (unknown length) — to be determined by group analysis")


if __name__ == '__main__':
    main()
