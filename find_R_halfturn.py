#!/usr/bin/env python3
"""
find_R_halfturn.py — Search for face moves using available crawler tools.

Strategy (updated based on group_analysis.py findings):
  - R is NOT in the half-turn group {U, F2, B2, R2, L2}
  - D IS in the half-turn group — search for it via BFS
  - R IS in the original crawler group — use SymPy to decompose it

Part 1: BFS for D in the half-turn metric {U, U', F2, B2, R2, L2}
  - Each "abstract move" maps to 1-2 actual crawler moves
  - D should be findable at moderate depth

Part 2: Use SymPy's Schreier-Sims machinery to express R as a word
  in the crawler generators (this may produce a very long sequence)

Part 3: Try MITM (meet in the middle) for R in the extended generator set
"""

import sys
import time
from collections import deque
sys.path.insert(0, '.')

from crawler_macros import (
    IDENTITY, compose, invert, apply_perm,
    U, U_prime, D, D_prime, R, R_prime, L, L_prime,
    F, F_prime, B, B_prime,
    CRAWL_PX, CRAWL_MX, CRAWL_PZ, CRAWL_MZ,
    SPIN1, SPIN1_P,
)
from crawler_extended import (
    FB_SPIN, FB_SPIN_P, LR_SPIN, LR_SPIN_P,
    F_squared, B_squared, R_squared, L_squared,
    EXTENDED_GENERATORS, EXTENDED_INVERSES,
)

def log(msg):
    print(msg, flush=True)


# ─── Part 1: BFS for D in half-turn metric ───

def find_D_halfturn():
    """BFS for D using {U, U', F2, B2, R2, L2} as generators."""
    log("\n" + "=" * 60)
    log("Part 1: BFS for D in half-turn metric")
    log("=" * 60)

    # Define abstract generators and their crawler translations
    abstract_gens = {
        'U':  (U,         ['spin1']),
        "U'": (U_prime,   ["spin1'"]),
        'F2': (F_squared,  ["fb_spin'", '-x']),   # or [-x, fb_spin'] — both work
        'B2': (B_squared,  ['fb_spin', '-x']),
        'R2': (R_squared,  ['lr_spin', '-z']),
        'L2': (L_squared,  ["lr_spin'", '-z']),
    }

    gen_names = list(abstract_gens.keys())
    gen_perms = {n: abstract_gens[n][0] for n in gen_names}
    gen_crawl = {n: abstract_gens[n][1] for n in gen_names}

    # Inverse mapping for pruning
    inverses = {
        'U': "U'", "U'": 'U',
        'F2': 'F2', 'B2': 'B2', 'R2': 'R2', 'L2': 'L2',
    }

    target = D
    target_name = 'D'

    # BFS
    log(f"\nSearching for {target_name}...")
    visited = {IDENTITY: []}
    queue = deque([(IDENTITY, [])])

    t0 = time.time()
    depth = 0
    count = 0

    while queue:
        state, path = queue.popleft()

        if len(path) > depth:
            depth = len(path)
            dt = time.time() - t0
            log(f"  Depth {depth}: {count:,} states ({dt:.1f}s)")
            if depth > 15:  # Safety limit
                break

        count += 1

        for gname in gen_names:
            # Prune: don't apply inverse of last move
            if path and gname == inverses.get(path[-1]):
                continue
            # Prune: don't apply same half-turn twice (X2·X2 = identity)
            if path and gname == path[-1] and gname.endswith('2'):
                continue

            new_state = compose(gen_perms[gname], state)
            if new_state in visited:
                continue
            visited[new_state] = path + [gname]
            new_path = path + [gname]

            if new_state == target:
                dt = time.time() - t0
                log(f"\n  FOUND {target_name} at depth {len(new_path)}! ({dt:.1f}s)")
                log(f"  Abstract sequence: {' '.join(new_path)}")

                # Convert to crawler moves
                crawler_seq = []
                for move in new_path:
                    crawler_seq.extend(gen_crawl[move])
                log(f"  Crawler sequence ({len(crawler_seq)} moves): {' '.join(crawler_seq)}")

                # Verify
                verify_perm = IDENTITY
                for move in crawler_seq:
                    verify_perm = compose(EXTENDED_GENERATORS[move], verify_perm)
                assert verify_perm == target, "VERIFICATION FAILED!"
                log(f"  Verified: crawler sequence produces {target_name} ✓")
                return new_path, crawler_seq

            queue.append((new_state, new_path))

    log(f"  {target_name} not found up to depth {depth}")
    return None, None


# Also search for D'
def find_D_prime_halfturn():
    """BFS for D' using {U, U', F2, B2, R2, L2}."""
    log(f"\nSearching for D'...")

    abstract_gens = {
        'U':  U,
        "U'": U_prime,
        'F2': F_squared,
        'B2': B_squared,
        'R2': R_squared,
        'L2': L_squared,
    }
    gen_crawl = {
        'U':  ['spin1'],
        "U'": ["spin1'"],
        'F2': ["fb_spin'", '-x'],
        'B2': ['fb_spin', '-x'],
        'R2': ['lr_spin', '-z'],
        'L2': ["lr_spin'", '-z'],
    }
    inverses = {'U': "U'", "U'": 'U', 'F2': 'F2', 'B2': 'B2', 'R2': 'R2', 'L2': 'L2'}
    gen_names = list(abstract_gens.keys())

    target = D_prime
    visited = {IDENTITY: []}
    queue = deque([(IDENTITY, [])])
    t0 = time.time()
    depth = 0

    while queue:
        state, path = queue.popleft()
        if len(path) > depth:
            depth = len(path)
            log(f"  Depth {depth}: {len(visited):,} states")
            if depth > 15:
                break

        for gname in gen_names:
            if path and gname == inverses.get(path[-1]):
                continue
            if path and gname == path[-1] and gname.endswith('2'):
                continue
            new_state = compose(abstract_gens[gname], state)
            if new_state in visited:
                continue
            visited[new_state] = path + [gname]
            new_path = path + [gname]

            if new_state == target:
                dt = time.time() - t0
                log(f"\n  FOUND D' at depth {len(new_path)}! ({dt:.1f}s)")
                log(f"  Abstract sequence: {' '.join(new_path)}")
                crawler_seq = []
                for move in new_path:
                    crawler_seq.extend(gen_crawl[move])
                log(f"  Crawler sequence ({len(crawler_seq)} moves): {' '.join(crawler_seq)}")

                # Verify
                verify_perm = IDENTITY
                for move in crawler_seq:
                    verify_perm = compose(EXTENDED_GENERATORS[move], verify_perm)
                assert verify_perm == target, "VERIFICATION FAILED!"
                log(f"  Verified ✓")
                return new_path, crawler_seq

            queue.append((new_state, new_path))

    log(f"  D' not found up to depth {depth}")
    return None, None


# ─── Part 2: MITM for R in extended crawler generators ───

def find_R_mitm():
    """Meet-in-the-middle search for R using all 10 extended generators."""
    log("\n" + "=" * 60)
    log("Part 2: MITM for R in extended generators")
    log("=" * 60)

    target = R
    gen_names = list(EXTENDED_GENERATORS.keys())
    gen_perms = EXTENDED_GENERATORS

    # Build forward table: BFS from identity
    log("\nForward BFS from identity...")
    forward = {IDENTITY: []}
    fwd_queue = deque([(IDENTITY, [])])
    max_depth = 7  # Keep memory manageable

    t0 = time.time()
    for depth in range(max_depth):
        next_queue = deque()
        while fwd_queue:
            state, path = fwd_queue.popleft()
            if len(path) != depth:
                next_queue.append((state, path))
                continue
            for gname in gen_names:
                if path and gname == EXTENDED_INVERSES.get(path[-1]):
                    continue
                new_state = compose(gen_perms[gname], state)
                if new_state not in forward:
                    new_path = path + [gname]
                    forward[new_state] = new_path
                    next_queue.append((new_state, new_path))
        fwd_queue = next_queue
        dt = time.time() - t0
        log(f"  Depth {depth+1}: {len(forward):,} states ({dt:.1f}s)")

    # Build backward table: BFS from R (apply inverse generators)
    log("\nBackward BFS from R...")
    backward = {target: []}
    bwd_queue = deque([(target, [])])

    for depth in range(max_depth):
        next_queue = deque()
        while bwd_queue:
            state, path = bwd_queue.popleft()
            if len(path) != depth:
                next_queue.append((state, path))
                continue
            for gname in gen_names:
                inv_name = EXTENDED_INVERSES.get(gname, gname)
                if path and gname == EXTENDED_INVERSES.get(path[-1]):
                    continue
                # Apply inverse: move backward from target
                new_state = compose(gen_perms[inv_name], state)
                if new_state not in backward:
                    new_path = path + [gname]
                    backward[new_state] = new_path
                    next_queue.append((new_state, new_path))

                    # Check for match with forward table
                    if new_state in forward:
                        fwd_path = forward[new_state]
                        bwd_path = new_path  # These are in reverse order
                        total = fwd_path + bwd_path
                        dt = time.time() - t0
                        log(f"\n  MATCH at depth {len(fwd_path)} + {len(bwd_path)} = {len(total)}! ({dt:.1f}s)")
                        log(f"  Forward:  {' '.join(fwd_path)}")
                        log(f"  Backward: {' '.join(bwd_path)}")
                        log(f"  Combined: {' '.join(total)}")

                        # Verify
                        verify = IDENTITY
                        for move in total:
                            verify = compose(gen_perms[move], verify)
                        if verify == target:
                            log(f"  Verified: sequence produces R ✓")
                            return total
                        else:
                            log(f"  Verification FAILED — continuing search...")

        bwd_queue = next_queue
        dt = time.time() - t0
        log(f"  Depth {depth+1}: {len(backward):,} states ({dt:.1f}s)")

    # Check all forward states against backward
    log("\nChecking all forward-backward intersections...")
    matches = set(forward.keys()) & set(backward.keys())
    if matches:
        # Find shortest
        best = None
        for m in matches:
            total_len = len(forward[m]) + len(backward[m])
            if best is None or total_len < best[0]:
                best = (total_len, forward[m], backward[m])
        log(f"  Best match: {best[0]} moves")
        total = best[1] + best[2]
        verify = IDENTITY
        for move in total:
            verify = compose(gen_perms[move], verify)
        if verify == target:
            log(f"  Verified ✓")
            log(f"  Sequence: {' '.join(total)}")
            return total
        else:
            log(f"  Verification failed")
    else:
        log(f"  No matches found up to depth {max_depth}")

    return None


def main():
    log("=" * 60)
    log("Face Move Discovery")
    log("=" * 60)

    # Part 1: Find D
    d_abstract, d_crawler = find_D_halfturn()
    dp_abstract, dp_crawler = find_D_prime_halfturn()

    # Part 2: MITM for R
    r_sequence = find_R_mitm()

    # ─── Summary ───
    log("\n" + "=" * 60)
    log("RESULTS SUMMARY")
    log("=" * 60)

    if d_crawler:
        log(f"\nD macro ({len(d_crawler)} crawler moves):")
        log(f"  {' '.join(d_crawler)}")
    else:
        log("\nD: not found")

    if dp_crawler:
        log(f"\nD' macro ({len(dp_crawler)} crawler moves):")
        log(f"  {' '.join(dp_crawler)}")
    else:
        log("\nD': not found")

    if r_sequence:
        log(f"\nR macro ({len(r_sequence)} extended crawler moves):")
        log(f"  {' '.join(r_sequence)}")
    else:
        log("\nR: not found via MITM (may need deeper search or algebraic approach)")

    log("\n--- Move Cost Summary ---")
    log("Already known:")
    log("  U  = spin1 (1 move)")
    log("  U' = spin1' (1 move)")
    log("  F2 = fb_spin' -x (2 moves)")
    log("  B2 = fb_spin -x (2 moves)")
    log("  R2 = lr_spin -z (2 moves)")
    log("  L2 = lr_spin' -z (2 moves)")
    if d_crawler:
        log(f"  D  = {' '.join(d_crawler)} ({len(d_crawler)} moves)")
    if dp_crawler:
        log(f"  D' = {' '.join(dp_crawler)} ({len(dp_crawler)} moves)")
    if r_sequence:
        log(f"  R  = {' '.join(r_sequence)} ({len(r_sequence)} moves)")


if __name__ == '__main__':
    main()
