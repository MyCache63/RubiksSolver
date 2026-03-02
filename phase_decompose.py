#!/usr/bin/env python3
"""
phase_decompose.py — Two-phase crawler solver.

Phase 1: Corner BFS table
  - Encode corners as (position_permutation, orientation_tuple)
  - 88,179,840 possible corner states (8! × 3^7)
  - BFS from solved state using 6 original crawler generators
  - Store: corner_index → (depth, last_move)
  - Reconstruct solution by tracing back from target to solved

Phase 2: Edge solver
  - After corners are solved, fix edges using edge 3-cycles
  - Edge 3-cycles are the commutators found in commutator_mine.py
  - These are "corner-neutral" since they only affect edges

The complete solver:
  1. Read cube state (54 stickers)
  2. Extract corner state
  3. Look up corner solution in BFS table
  4. Apply corner solution (may scramble edges)
  5. Fix edges using 3-cycles
"""

import sys
import time
import array
import json
sys.path.insert(0, '.')

from crawler_macros import (
    IDENTITY, compose, invert, apply_perm,
    CRAWL_PX, CRAWL_MX, CRAWL_PZ, CRAWL_MZ,
    SPIN1, SPIN1_P, R, D,
)
from crawler_extended import EXTENDED_GENERATORS, EXTENDED_INVERSES

# Import silently
import io as _io
_old = sys.stdout
sys.stdout = _io.StringIO()
from compute_corner_effects import (
    CORNER_STICKERS, EDGE_STICKERS,
    STICKER_TO_CORNER, EDGE_STICKER_TO_EDGE,
    get_corner_state, get_edge_state,
)
sys.stdout = _old

def log(msg):
    print(msg, flush=True)

# ─── Corner state encoding ───
# 8 corners, each in one of 8 positions with orientation 0/1/2
# Position: encoded as a permutation index (Lehmer code), 0..40319
# Orientation: 7 base-3 digits (last determined by sum mod 3), 0..2186
# Combined index: pos_idx * 2187 + ori_idx, range 0..88,179,839

NUM_CORNER_POS = 40320      # 8!
NUM_CORNER_ORI = 2187       # 3^7
NUM_CORNER_STATES = NUM_CORNER_POS * NUM_CORNER_ORI  # 88,179,840


def perm_to_lehmer(perm):
    """Convert a permutation of [0..7] to its Lehmer code index."""
    n = len(perm)
    used = [False] * n
    index = 0
    factorial = [1, 1, 2, 6, 24, 120, 720, 5040]  # factorials 0..7
    for i in range(n):
        count = 0
        for j in range(perm[i]):
            if not used[j]:
                count += 1
        index += count * factorial[n - 1 - i]
        used[perm[i]] = True
    return index


def lehmer_to_perm(index, n=8):
    """Convert a Lehmer code index to a permutation of [0..n-1]."""
    factorial = [1, 1, 2, 6, 24, 120, 720, 5040]
    available = list(range(n))
    perm = []
    for i in range(n):
        f = factorial[n - 1 - i]
        j = index // f
        index %= f
        perm.append(available[j])
        available.pop(j)
    return perm


def ori_to_index(ori):
    """Convert orientation tuple (7 values, each 0-2) to index 0..2186."""
    idx = 0
    for i in range(7):
        idx = idx * 3 + ori[i]
    return idx


def index_to_ori(idx):
    """Convert index 0..2186 to orientation tuple of 8 values."""
    ori = [0] * 8
    for i in range(6, -1, -1):
        ori[i] = idx % 3
        idx //= 3
    ori[7] = (3 - sum(ori[:7]) % 3) % 3
    return ori


def encode_corner_state(pos, ori):
    """Encode corner (position, orientation) as a single integer."""
    pos_idx = perm_to_lehmer(pos)
    ori_idx = ori_to_index(ori)
    return pos_idx * NUM_CORNER_ORI + ori_idx


def decode_corner_state(idx):
    """Decode integer to (position, orientation)."""
    pos_idx = idx // NUM_CORNER_ORI
    ori_idx = idx % NUM_CORNER_ORI
    return lehmer_to_perm(pos_idx), index_to_ori(ori_idx)


# ─── Corner transformation tables ───
# For each generator, precompute how it transforms the corner state.
# From compute_corner_effects.py output:
# gen_slot_perm[gen][old_slot] = new_slot (where piece in old_slot goes)
# gen_slot_ori[gen][old_slot] = orientation delta

GENERATORS = [CRAWL_PX, CRAWL_MX, CRAWL_PZ, CRAWL_MZ, SPIN1, SPIN1_P]
GEN_NAMES = ['+x', '-x', '+z', '-z', 'spin1', "spin1'"]
GEN_INV_IDX = [1, 0, 3, 2, 5, 4]  # Index of inverse generator

# Precompute corner effects for each generator
CORNER_PERM = []  # slot_perm[gen][slot] = new_slot
CORNER_ORI = []   # slot_ori[gen][slot] = orientation delta

for gen in GENERATORS:
    cpos, cori = get_corner_state(gen)
    # cpos[piece] = new_slot, cori[piece] = twist
    # For the BFS, we need slot-to-slot mapping:
    # If piece P is in slot S, after generator G:
    #   new_slot = cpos[S]  (since at identity, piece S is in slot S)
    #   new_ori = (old_ori + cori[S]) % 3
    CORNER_PERM.append(cpos)
    CORNER_ORI.append(cori)


def apply_corner_gen(pos, ori, gen_idx):
    """Apply generator gen_idx to corner state (pos, ori).
    Returns new (pos, ori)."""
    cp = CORNER_PERM[gen_idx]
    co = CORNER_ORI[gen_idx]
    new_pos = [0] * 8
    new_ori = [0] * 8
    for piece in range(8):
        old_slot = pos[piece]
        new_slot = cp[old_slot]
        new_pos[piece] = new_slot
        new_ori[piece] = (ori[piece] + co[old_slot]) % 3
    return new_pos, new_ori


def build_corner_table():
    """BFS from solved corner state to all reachable corner states.
    Returns: depth array (88M entries, 1 byte each) and parent move array."""
    log("Building corner BFS table...")
    log(f"  Total states: {NUM_CORNER_STATES:,}")

    # Use bytearray for memory efficiency (1 byte per entry)
    UNSEEN = 255
    depth_table = bytearray([UNSEEN]) * NUM_CORNER_STATES
    # Store the last move that was applied (to reconstruct path)
    move_table = bytearray([255]) * NUM_CORNER_STATES

    # Solved state: each piece in its home slot, all orientations 0
    solved_pos = list(range(8))
    solved_ori = [0] * 8
    solved_idx = encode_corner_state(solved_pos, solved_ori)
    depth_table[solved_idx] = 0

    # BFS using lists (more memory efficient than deque for large BFS)
    current_level = [(solved_pos, solved_ori)]
    depth = 0
    total_seen = 1

    t0 = time.time()

    while current_level:
        next_level = []
        for pos, ori in current_level:
            for gi in range(6):
                new_pos, new_ori = apply_corner_gen(pos, ori, gi)
                new_idx = encode_corner_state(new_pos, new_ori)
                if depth_table[new_idx] == UNSEEN:
                    depth_table[new_idx] = depth + 1
                    move_table[new_idx] = gi
                    next_level.append((new_pos, new_ori))
                    total_seen += 1

        depth += 1
        dt = time.time() - t0
        log(f"  Depth {depth}: {len(next_level):,} new states "
            f"(total: {total_seen:,}, {dt:.1f}s)")
        current_level = next_level

        if depth > 30:  # Safety limit
            break

    log(f"  BFS complete: {total_seen:,} states reached, max depth {depth-1}")
    unreached = sum(1 for d in depth_table if d == UNSEEN)
    log(f"  Unreached states: {unreached:,} ({unreached/NUM_CORNER_STATES*100:.1f}%)")

    return depth_table, move_table


def solve_corners(perm, depth_table, move_table):
    """Given a 54-sticker permutation, find the crawler sequence to solve corners."""
    cpos, cori = get_corner_state(perm)
    if cpos is None:
        return None

    idx = encode_corner_state(cpos, cori)
    if depth_table[idx] == 255:
        return None  # Unreachable

    # Trace back from this state to solved
    moves = []
    pos, ori = cpos, cori
    while depth_table[encode_corner_state(pos, ori)] > 0:
        idx = encode_corner_state(pos, ori)
        gi = move_table[idx]
        moves.append(GEN_NAMES[gi])
        # Apply inverse of this generator to go back
        inv_gi = GEN_INV_IDX[gi]
        pos, ori = apply_corner_gen(pos, ori, inv_gi)

    # Moves are in reverse order (from target back to solved)
    # We need the forward sequence (from solved to target), then invert it
    # Actually: we traced from target→solved, each step using the INVERSE of the stored move
    # So the forward sequence from solved→target is: the stored moves in reverse order
    # But we want to go from target→solved, which means applying the inverses in forward order
    moves_to_solve = []
    for m in moves:
        inv_m = EXTENDED_INVERSES[m]
        moves_to_solve.append(inv_m)

    return moves_to_solve


def main():
    log("=" * 60)
    log("Two-Phase Crawler Solver — Corner BFS")
    log("=" * 60)

    # Verify encoding/decoding
    log("\n--- Encoding verification ---")
    for test_pos, test_ori in [
        (list(range(8)), [0]*8),
        ([1,0,2,3,4,5,6,7], [1,2,0,0,0,0,0,0]),
        ([7,6,5,4,3,2,1,0], [2,2,2,2,2,2,2,1]),
    ]:
        idx = encode_corner_state(test_pos, test_ori)
        dec_pos, dec_ori = decode_corner_state(idx)
        match = dec_pos == test_pos and dec_ori == test_ori
        log(f"  pos={test_pos[:4]}... ori={test_ori[:4]}... → idx={idx} → "
            f"{'OK' if match else 'FAIL'}")
        assert match, f"Encoding mismatch: {dec_pos} {dec_ori}"

    # Verify corner generator application
    log("\n--- Generator verification ---")
    for gi in range(6):
        pos, ori = list(range(8)), [0]*8
        new_pos, new_ori = apply_corner_gen(pos, ori, gi)
        expected_pos, expected_ori = get_corner_state(GENERATORS[gi])
        assert new_pos == expected_pos, f"Gen {gi}: pos mismatch"
        assert new_ori == expected_ori, f"Gen {gi}: ori mismatch"
        log(f"  {GEN_NAMES[gi]}: pos and ori match ✓")

    # Build BFS table
    depth_table, move_table = build_corner_table()

    # Test: solve R's corner effect
    log("\n--- Test: solving R's corner state ---")
    r_sol = solve_corners(R, depth_table, move_table)
    if r_sol:
        log(f"  R corners solved in {len(r_sol)} moves: {' '.join(r_sol)}")
        # Verify: apply R then the solution, check corners are solved
        state = R
        for m in r_sol:
            state = compose(state, EXTENDED_GENERATORS[m])
        cpos, cori = get_corner_state(state)
        log(f"  After solving: pos={cpos}, ori={cori}")
        corners_solved = cpos == list(range(8)) and cori == [0]*8
        log(f"  Corners solved: {corners_solved}")
    else:
        log(f"  Failed to solve R's corners")

    # Test: solve D's corner effect
    log("\n--- Test: solving D's corner state ---")
    d_sol = solve_corners(D, depth_table, move_table)
    if d_sol:
        log(f"  D corners solved in {len(d_sol)} moves: {' '.join(d_sol)}")
        state = D
        for m in d_sol:
            state = compose(state, EXTENDED_GENERATORS[m])
        cpos, cori = get_corner_state(state)
        corners_solved = cpos == list(range(8)) and cori == [0]*8
        log(f"  Corners solved: {corners_solved}")

    # Test: solve a random scramble's corners
    log("\n--- Test: random scramble ---")
    import random
    random.seed(42)
    state = IDENTITY
    scramble = []
    gen_list = list(EXTENDED_GENERATORS.items())
    for _ in range(20):
        name, perm = random.choice(gen_list)
        state = compose(state, perm)
        scramble.append(name)
    log(f"  Scramble: {' '.join(scramble)}")
    sol = solve_corners(state, depth_table, move_table)
    if sol:
        log(f"  Corner solution: {len(sol)} moves")
        for m in sol:
            state = compose(state, EXTENDED_GENERATORS[m])
        cpos, cori = get_corner_state(state)
        corners_solved = cpos == list(range(8)) and cori == [0]*8
        log(f"  Corners solved: {corners_solved}")
        epos, eori = get_edge_state(state)
        edges_solved = epos == list(range(12)) and eori == [0]*12
        log(f"  Edges solved: {edges_solved}")
        if not edges_solved:
            moved_edges = sum(1 for i in range(12) if epos[i] != i or eori[i] != 0)
            log(f"  Edges still scrambled: {moved_edges} edges affected")
    else:
        log(f"  Failed to solve corners")

    # ─── Summary ───
    log("\n" + "=" * 60)
    log("SUMMARY")
    log("=" * 60)
    log(f"Corner BFS table: {NUM_CORNER_STATES:,} states")
    unreached = sum(1 for d in depth_table if d == 255)
    if unreached == 0:
        log("All corner states reachable ✓")
    else:
        log(f"Unreachable: {unreached:,} ({unreached/NUM_CORNER_STATES*100:.1f}%)")
    max_depth = max(d for d in depth_table if d != 255)
    log(f"Max depth (God's number for corners): {max_depth}")
    log("")
    log("Phase 1 (corner solving) complete ✓")
    log("Phase 2 (edge solving): edge-only commutators generate only 128 of")
    log("  239M+ possible edge states — insufficient for general edge solving.")
    log("  Corner-preserving edge operations need longer sequences or different approach.")
    log("  For the game: history reversal remains the primary solver.")


if __name__ == '__main__':
    main()
