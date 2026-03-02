#!/usr/bin/env python3
"""
group_analysis.py — Settle the subgroup question using SymPy.

Computes exact group orders for:
  1. Full Rubik's group ⟨U, D, R, L, F, B⟩ (sanity check)
  2. Original 6 crawler generators ⟨+x, -x, +z, -z, spin1, spin1'⟩
  3. Extended 10 generators (original + 4 same-direction spins)
  4. Effective half-turn set {U, U', F², B², L², R²}
  5. Full effective set {U, U', D, D', F², B², L², R²}

Also tests membership: is R in our extended group? Is D?
"""

import sys
import time
sys.path.insert(0, '.')

from sympy.combinatorics import Permutation, PermutationGroup

from crawler_macros import (
    IDENTITY, compose, invert,
    U, U_prime, D, D_prime, R, R_prime, L, L_prime,
    F, F_prime, B, B_prime, E, E_prime,
    CRAWL_PX, CRAWL_MX, CRAWL_PZ, CRAWL_MZ,
    SPIN1, SPIN1_P, SPIN2, SPIN2_P,
)
from crawler_extended import (
    FB_SPIN, FB_SPIN_P, LR_SPIN, LR_SPIN_P,
    F_squared, B_squared, R_squared, L_squared,
    U_squared, D_squared,
)

def log(msg):
    print(msg, flush=True)

def our_perm_to_sympy(perm):
    """Convert our 'pulls from' permutation to sympy's 'maps to' format."""
    inv = [0] * len(perm)
    for i in range(len(perm)):
        inv[perm[i]] = i
    return Permutation(inv)


def timed_order(group, label):
    """Compute group order with timing."""
    t0 = time.time()
    order = group.order()
    dt = time.time() - t0
    log(f"  {label}: order = {order:,}  ({dt:.1f}s)")
    return order


log("=" * 60)
log("Group Analysis — Subgroup Orders and Membership")
log("=" * 60)

# Convert all permutations to sympy format
log("\nConverting permutations to SymPy format...")
sU = our_perm_to_sympy(U)
sU_prime = our_perm_to_sympy(U_prime)
sD = our_perm_to_sympy(D)
sD_prime = our_perm_to_sympy(D_prime)
sR = our_perm_to_sympy(R)
sR_prime = our_perm_to_sympy(R_prime)
sL = our_perm_to_sympy(L)
sL_prime = our_perm_to_sympy(L_prime)
sF = our_perm_to_sympy(F)
sF_prime = our_perm_to_sympy(F_prime)
sB = our_perm_to_sympy(B)
sB_prime = our_perm_to_sympy(B_prime)

sCRAWL_PX = our_perm_to_sympy(CRAWL_PX)
sCRAWL_MX = our_perm_to_sympy(CRAWL_MX)
sCRAWL_PZ = our_perm_to_sympy(CRAWL_PZ)
sCRAWL_MZ = our_perm_to_sympy(CRAWL_MZ)
sSPIN1 = our_perm_to_sympy(SPIN1)
sSPIN1_P = our_perm_to_sympy(SPIN1_P)
sSPIN2 = our_perm_to_sympy(SPIN2)
sSPIN2_P = our_perm_to_sympy(SPIN2_P)

sFB_SPIN = our_perm_to_sympy(FB_SPIN)
sFB_SPIN_P = our_perm_to_sympy(FB_SPIN_P)
sLR_SPIN = our_perm_to_sympy(LR_SPIN)
sLR_SPIN_P = our_perm_to_sympy(LR_SPIN_P)

sF2 = our_perm_to_sympy(F_squared)
sB2 = our_perm_to_sympy(B_squared)
sR2 = our_perm_to_sympy(R_squared)
sL2 = our_perm_to_sympy(L_squared)
sU2 = our_perm_to_sympy(U_squared)
sD2 = our_perm_to_sympy(D_squared)
log("Done.\n")

# ─── Sanity checks ───
log("--- Sanity Checks ---")
log(f"U order:  {sU.order()}")    # 4
log(f"R order:  {sR.order()}")    # 4
log(f"F² order: {sF2.order()}")   # 2
log(f"+x order: {sCRAWL_PX.order()}")  # 4
log(f"fb_spin order: {sFB_SPIN.order()}")  # 4
log("")

# ─── Group order computations ───
log("--- Group Order Computations ---")
log("(Each may take 10-60 seconds...)\n")

# 1. Full Rubik's group
G_full = PermutationGroup(sU, sD, sR, sL, sF, sB)
order_full = timed_order(G_full, "Full ⟨U,D,R,L,F,B⟩")
# On 54-sticker model: this will be larger than the standard 43 quintillion
# because the 54-sticker model allows "impossible" center permutations to be tracked.
# Actually no — our face moves FIX centers, so the group acts on the 48 non-center stickers.
# But SymPy sees 54 positions. The centers are always fixed, so the group order should
# match the standard Rubik's group order for the positions it acts on.

# 2. Original crawler group (no spin2, just the game moves without lazy susan)
G_crawler_no_spin2 = PermutationGroup(sSPIN1, sCRAWL_PX, sCRAWL_PZ)
order_no_spin2 = timed_order(G_crawler_no_spin2, "Crawler (no spin2) ⟨spin1, +x, +z⟩")

# 3. Original crawler group WITH spin2
G_crawler_spin2 = PermutationGroup(sSPIN1, sSPIN2, sCRAWL_PX, sCRAWL_PZ)
order_spin2 = timed_order(G_crawler_spin2, "Crawler (spin2) ⟨spin1, spin2, +x, +z⟩")

# 4. Extended crawler group (original + same-direction spins)
G_extended = PermutationGroup(
    sSPIN1, sCRAWL_PX, sCRAWL_PZ, sFB_SPIN, sLR_SPIN
)
order_extended = timed_order(G_extended, "Extended ⟨spin1, +x, +z, fb_spin, lr_spin⟩")

# 5. Half-turn effective set {U, U', F², B², R², L²}
G_halfturn = PermutationGroup(sU, sF2, sB2, sR2, sL2)
order_halfturn = timed_order(G_halfturn, "Half-turn {U, F², B², R², L²}")

# 6. Full effective set with D
G_halfturn_D = PermutationGroup(sU, sD, sF2, sB2, sR2, sL2)
order_halfturn_D = timed_order(G_halfturn_D, "Half-turn+D {U, D, F², B², R², L²}")

# ─── Comparison ───
log("\n--- Group Order Comparison ---")
log(f"  Full Rubik's:            {order_full:,}")
log(f"  Crawler (no spin2):      {order_no_spin2:,}")
log(f"  Crawler (with spin2):    {order_spin2:,}")
log(f"  Extended (10 gens):      {order_extended:,}")
log(f"  Half-turn {{U,F2,B2,R2,L2}}:  {order_halfturn:,}")
log(f"  Half-turn+D {{U,D,F2,...}}:    {order_halfturn_D:,}")

for label, order in [
    ("Crawler (no spin2)", order_no_spin2),
    ("Crawler (with spin2)", order_spin2),
    ("Extended (10 gens)", order_extended),
    ("Half-turn effective", order_halfturn),
    ("Half-turn+D effective", order_halfturn_D),
]:
    if order == order_full:
        log(f"\n  {label} = FULL GROUP ★")
    else:
        ratio = order_full / order
        log(f"\n  {label}: index [{order_full}/{order}] = {ratio}")

# ─── Membership tests ───
log("\n--- Membership Tests ---")
log("Can we reach individual quarter-turns from our generators?\n")

# Test in the extended group
test_moves = [
    ('R', sR), ('L', sL), ('F', sF), ('B', sB), ('D', sD),
    ('R²', sR2), ('L²', sL2), ('F²', sF2), ('B²', sB2), ('D²', sD2),
]

for label, sperm in test_moves:
    in_extended = G_extended.contains(sperm)
    in_halfturn = G_halfturn.contains(sperm)
    log(f"  {label:3s} ∈ extended? {str(in_extended):5s}   ∈ half-turn? {str(in_halfturn):5s}")

# ─── D macro search ───
# If D is in the half-turn group, try to express it
log("\n--- D Macro Investigation ---")
if G_halfturn.contains(sD):
    log("D IS in {U, F², B², R², L²} — there exists a finite expression!")
    log("Attempting to find coset representative (may be slow)...")
    # SymPy can give us the Schreier vector representation
    try:
        # This finds the word expressing sD in terms of generators
        from sympy.combinatorics.util import _strip
        result = G_halfturn.contains(sD, strict=False)
        log(f"  Result: {result}")
    except Exception as e:
        log(f"  Could not compute word: {e}")
elif G_halfturn_D.contains(sD):
    log("D is NOT in {U, F², B², R², L²}")
    log("Adding D as an independent generator is necessary.")
else:
    log("D is not even in {U, D, F², B², R², L²} — something is wrong!")

# ─── Summary ───
log("\n" + "=" * 60)
log("SUMMARY")
log("=" * 60)

if order_extended == order_full:
    log("""
★ The extended crawler group (10 generators) IS the full Rubik's group!
  Every cube state is reachable.
  R, L, F, B all exist as (long) crawler sequences.
""")
elif order_halfturn == order_full:
    log("""
★ The half-turn set {U, U', F², B², R², L²} generates the full group!
  R can be found by BFS/MITM in this metric.
""")
elif order_halfturn_D == order_full:
    log("""
★ {U, U', D, D', F², B², R², L²} generates the full group!
  We need D as an independent generator.
  R can be found by BFS/MITM in this expanded metric.
""")
else:
    log(f"""
The extended group is a PROPER subgroup of the full Rubik's group.
Index = {order_full / order_extended}
Not every state is reachable from crawler moves.

Need to investigate further:
- Is the half-turn group the same as the extended group?
- What states are missing?
""")

# Also check: is the "half-turn group" a known group?
log("--- Additional: Half-Turn Subgroup Analysis ---")
# The half-turn metric group ⟨U, U', R², L², F², B²⟩ is studied in cubing theory.
# The "square subgroup" has index 2 (parity constraint: only even permutations of corners
# or edges from each other can be reached).
# But with U/U' included (quarter turns of one face), this is typically the full group.
log(f"Half-turn group order: {order_halfturn:,}")
log(f"Full group order:      {order_full:,}")
if order_halfturn == order_full:
    log("→ {U, F², B², R², L²} = full group")
else:
    log(f"→ Index = {order_full // order_halfturn}")
    log("  This means some states need quarter-turns of F/R/L/B to reach.")
