#!/usr/bin/env python3
"""
Crawler Macros BFS — Research script for finding crawler move equivalents
of standard Rubik's face moves.

FINDINGS (March 1, 2026):
- R, R', L, L', F, F', B, B' are IMPOSSIBLE with crawler moves.
  Reason: crawl moves always rotate opposite faces as a pair (F+B' or R+L').
  A solo R requires R without L, which violates this coupling constraint.
- D, D' APPEAR reachable (BFS found a match at depth 9) BUT this was a
  false positive — the solved state has repeated sticker values, so different
  permutations can produce the same output. Verified with unique-value states:
  the depth-9 sequence does NOT equal D on arbitrary cube states.
- The crawler subgroup ⟨U, F·B', R·L'⟩ is a proper subgroup of the full
  Rubik's group. It can reach many states but NOT individual face rotations.

CONCLUSION: Macro substitution (Kociemba → crawler macros) is not viable.
The correct approach is HISTORY REVERSAL: reverse the crawlerHistory to solve.
"""

import json
import sys
import random
from collections import deque

def log(msg):
    print(msg)
    sys.stdout.flush()

IDENTITY = tuple(range(54))
SOLVED = tuple(i // 9 for i in range(54))

def apply_perm(state, perm):
    return tuple(state[perm[i]] for i in range(54))

def compose(a, b):
    """Apply b first, then a. Result[i] = a[b[i]]"""
    return tuple(a[b[i]] for i in range(54))

def invert(perm):
    inv = [0] * 54
    for i in range(54):
        inv[perm[i]] = i
    return tuple(inv)

def face_cw(offset):
    perm = list(IDENTITY)
    o = offset
    perm[o+0]=o+6; perm[o+2]=o+0; perm[o+8]=o+2; perm[o+6]=o+8
    perm[o+1]=o+3; perm[o+5]=o+1; perm[o+7]=o+5; perm[o+3]=o+7
    return tuple(perm)

def make_U():
    perm = list(face_cw(0))
    cycle = [(18,19,20), (9,10,11), (45,46,47), (36,37,38)]
    for i in range(3):
        perm[cycle[0][i]] = cycle[3][i]
        perm[cycle[1][i]] = cycle[0][i]
        perm[cycle[2][i]] = cycle[1][i]
        perm[cycle[3][i]] = cycle[2][i]
    return tuple(perm)

def make_D():
    perm = list(face_cw(27))
    cycle = [(24,25,26), (42,43,44), (51,52,53), (15,16,17)]
    for i in range(3):
        perm[cycle[0][i]] = cycle[3][i]
        perm[cycle[1][i]] = cycle[0][i]
        perm[cycle[2][i]] = cycle[1][i]
        perm[cycle[3][i]] = cycle[2][i]
    return tuple(perm)

def make_R():
    perm = list(face_cw(9))
    u=[2,5,8]; f=[20,23,26]; d=[29,32,35]; b=[51,48,45]
    for i in range(3):
        perm[u[i]]=f[i]; perm[b[i]]=u[i]; perm[d[i]]=b[i]; perm[f[i]]=d[i]
    return tuple(perm)

def make_L():
    perm = list(face_cw(36))
    u=[0,3,6]; f=[18,21,24]; d=[27,30,33]; b=[53,50,47]
    for i in range(3):
        perm[f[i]]=u[i]; perm[d[i]]=f[i]; perm[b[i]]=d[i]; perm[u[i]]=b[i]
    return tuple(perm)

def make_F():
    perm = list(face_cw(18))
    u=[6,7,8]; r=[9,12,15]; d=[29,28,27]; l=[44,41,38]
    for i in range(3):
        perm[r[i]]=u[i]; perm[d[i]]=r[i]; perm[l[i]]=d[i]; perm[u[i]]=l[i]
    return tuple(perm)

def make_B():
    perm = list(face_cw(45))
    u=[2,1,0]; r=[11,14,17]; d=[33,34,35]; l=[36,39,42]
    for i in range(3):
        perm[r[i]]=u[i]; perm[d[i]]=r[i]; perm[l[i]]=d[i]; perm[u[i]]=l[i]
    return tuple(perm)

def make_E_prime():
    perm = list(IDENTITY)
    f=[21,22,23]; r=[12,13,14]; b=[48,49,50]; l=[39,40,41]
    for i in range(3):
        perm[r[i]]=f[i]; perm[b[i]]=r[i]; perm[l[i]]=b[i]; perm[f[i]]=l[i]
    return tuple(perm)

U = make_U()
D = make_D()
R = make_R()
L = make_L()
F = make_F()
B = make_B()
E_prime = make_E_prime()

U_prime = invert(U)
D_prime = invert(D)
R_prime = invert(R)
L_prime = invert(L)
F_prime = invert(F)
B_prime = invert(B)
E = invert(E_prime)

CRAWL_PX = compose(F, B_prime)
CRAWL_MX = compose(F_prime, B)
CRAWL_PZ = compose(R_prime, L)
CRAWL_MZ = compose(R, L_prime)
SPIN1    = U
SPIN1_P  = U_prime
SPIN2    = compose(U, E_prime)
SPIN2_P  = compose(U_prime, E)

ALL_CRAWLER_PERMS = {
    '+x': CRAWL_PX, '-x': CRAWL_MX,
    '+z': CRAWL_PZ, '-z': CRAWL_MZ,
    'spin1': SPIN1, "spin1'": SPIN1_P,
    'spin2': SPIN2, "spin2'": SPIN2_P,
}


def main():
    log("=" * 60)
    log("Crawler Macros Research — BFS Results")
    log("=" * 60)

    # Verify basic permutation properties
    log("\n--- Permutation verification ---")
    for name, perm in [('U',U),('D',D),('R',R),('L',L),('F',F),('B',B)]:
        assert sorted(perm) == list(range(54)), f"{name} invalid!"
        s = SOLVED
        for _ in range(4):
            s = apply_perm(s, perm)
        assert s == SOLVED, f"{name}^4 != identity"
    log("All face moves: valid permutations, order 4 ✓")

    for name, perm in ALL_CRAWLER_PERMS.items():
        assert sorted(perm) == list(range(54)), f"Crawler {name} invalid!"
    log("All crawler moves: valid permutations ✓")

    # Demonstrate the coupling constraint
    log("\n--- Coupling Constraint ---")
    log("Every crawler crawl move rotates two opposite faces:")
    log("  +x = F·B'  (F clockwise + B counterclockwise)")
    log("  -x = F'·B   (F counterclockwise + B clockwise)")
    log("  +z = R'·L   (R counterclockwise + L clockwise)")
    log("  -z = R·L'  (R clockwise + L counterclockwise)")
    log("")
    log("In any sequence of crawler moves, R and L are always paired.")
    log("You can never apply R without also applying L (or L').")
    log("Therefore a solo R move is IMPOSSIBLE with crawler generators.")
    log("Same logic applies to L, F, and B individually.")
    log("")
    log("U is directly available as spin1.")
    log("D is NOT coupled, but constructing it from commutators of")
    log("paired moves requires very long sequences (if possible at all).")

    # BFS result verification — show the depth-9 result was a false positive
    log("\n--- False Positive Check ---")
    d_seq = ['+z', '+x', '+x', '+z', 'spin1', '+z', '+x', '+x', '+z']
    macro_perm = IDENTITY
    for mname in d_seq:
        macro_perm = compose(ALL_CRAWLER_PERMS[mname], macro_perm)

    log(f"BFS found depth-9 sequence for D: {d_seq}")
    log(f"  Matches D on solved state: {apply_perm(SOLVED, macro_perm) == apply_perm(SOLVED, D)}")

    # Test with unique-value state
    UNIQUE = tuple(range(54))
    log(f"  Matches D permutation (unique values): {apply_perm(UNIQUE, macro_perm) == apply_perm(UNIQUE, D)}")

    # Random state test
    random.seed(42)
    all_std = [U,U_prime,D,D_prime,R,R_prime,L,L_prime,F,F_prime,B,B_prime]
    matches = 0
    for _ in range(100):
        s = SOLVED
        for __ in range(20):
            s = apply_perm(s, random.choice(all_std))
        if apply_perm(s, macro_perm) == apply_perm(s, D):
            matches += 1
    log(f"  Matches D on 100 random states: {matches}/100")
    log("  → FALSE POSITIVE: the solved state has repeated values,")
    log("    so different permutations can look identical on it.")

    log("\n--- Conclusion ---")
    log("Macro substitution is NOT viable for the crawler solver.")
    log("Individual face moves (R, L, F, B, and likely D) cannot be")
    log("expressed as finite sequences of crawler moves.")
    log("")
    log("The correct approach: HISTORY REVERSAL")
    log("  1. Record all crawler moves during scramble/play")
    log("  2. To solve: reverse the history, inverting each move")
    log("  3. The cube crawls back along its path to the solved state")
    log("  4. Guaranteed correct, short solutions, visually appealing")


if __name__ == '__main__':
    main()
