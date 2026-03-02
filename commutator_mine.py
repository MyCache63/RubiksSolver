#!/usr/bin/env python3
"""
commutator_mine.py — Systematic commutator enumeration.

Generates all commutators [A, B] = A·B·A⁻¹·B⁻¹ where A and B are
crawler sequences of length 1-2 (using all 10 extended generators).

Classifies results and saves library to commutator_library.json.
"""

import sys
import json
sys.path.insert(0, '.')

from crawler_macros import (
    IDENTITY, compose, invert,
    R, L, F, B, D,
)
from crawler_extended import EXTENDED_GENERATORS, EXTENDED_INVERSES
# Import corner/edge analysis without the module's top-level print noise
import io as _io
_old_stdout = sys.stdout
sys.stdout = _io.StringIO()
from compute_corner_effects import (
    CORNER_STICKERS, EDGE_STICKERS,
    STICKER_TO_CORNER, EDGE_STICKER_TO_EDGE,
    get_corner_state, get_edge_state,
)
sys.stdout = _old_stdout

def log(msg):
    print(msg, flush=True)


def commutator(a, b):
    """[A, B] = A·B·A'·B': apply B' first, then A', then B, then A."""
    a_inv = invert(a)
    b_inv = invert(b)
    result = IDENTITY
    result = compose(b_inv, result)
    result = compose(a_inv, result)
    result = compose(b, result)
    result = compose(a, result)
    return result


def classify_effect(perm):
    """Classify corner and edge effects of a permutation."""
    cpos, cori = get_corner_state(perm)
    epos, eori = get_edge_state(perm)
    if cpos is None or epos is None:
        return None

    corners_moved_pos = sum(1 for i in range(8) if cpos[i] != i)
    corners_moved_ori = sum(1 for i in range(8) if cori[i] != 0)
    corners_moved = sum(1 for i in range(8) if cpos[i] != i or cori[i] != 0)
    edges_moved_pos = sum(1 for i in range(12) if epos[i] != i)
    edges_moved_ori = sum(1 for i in range(12) if eori[i] != 0)
    edges_moved = sum(1 for i in range(12) if epos[i] != i or eori[i] != 0)

    corner_only = corners_moved > 0 and edges_moved == 0
    edge_only = edges_moved > 0 and corners_moved == 0

    # Cycle lengths
    corner_cycles = []
    visited = [False] * 8
    for i in range(8):
        if not visited[i] and cpos[i] != i:
            cycle_len = 1
            j = cpos[i]
            visited[i] = True
            while j != i:
                visited[j] = True
                cycle_len += 1
                j = cpos[j]
            corner_cycles.append(cycle_len)

    edge_cycles = []
    visited = [False] * 12
    for i in range(12):
        if not visited[i] and epos[i] != i:
            cycle_len = 1
            j = epos[i]
            visited[i] = True
            while j != i:
                visited[j] = True
                cycle_len += 1
                j = epos[j]
            edge_cycles.append(cycle_len)

    return {
        'corners_moved': corners_moved,
        'corners_pos': corners_moved_pos,
        'corners_ori': corners_moved_ori,
        'edges_moved': edges_moved,
        'edges_pos': edges_moved_pos,
        'edges_ori': edges_moved_ori,
        'corner_only': corner_only,
        'edge_only': edge_only,
        'pure_corner_twist': corners_moved_pos == 0 and corners_moved_ori > 0,
        'pure_edge_flip': edges_moved_pos == 0 and edges_moved_ori > 0,
        'is_corner_3cycle': corners_moved_pos == 3 and corners_moved_ori == 0,
        'is_edge_3cycle': edges_moved_pos == 3 and edges_moved_ori == 0,
        'corner_cycles': sorted(corner_cycles),
        'edge_cycles': sorted(edge_cycles),
        'corner_pos': cpos,
        'corner_ori': cori,
        'edge_pos': epos,
        'edge_ori': eori,
    }


def main():
    log("=" * 60)
    log("Commutator Mining — Systematic Enumeration")
    log("=" * 60)

    gen_names = list(EXTENDED_GENERATORS.keys())
    gen_perms = {name: EXTENDED_GENERATORS[name] for name in gen_names}

    # ─── Build all sequences of length 1 and 2, with cached permutations ───
    log("\nBuilding sequence library...")
    sequences = []  # list of (name_list, perm)

    # Length 1
    for g in gen_names:
        sequences.append(([g], gen_perms[g]))

    # Length 2 (prune move followed by inverse)
    for g1 in gen_names:
        for g2 in gen_names:
            if g2 == EXTENDED_INVERSES.get(g1):
                continue
            perm = compose(gen_perms[g2], gen_perms[g1])
            sequences.append(([g1, g2], perm))

    log(f"Sequences (len 1-2): {len(sequences)}")

    # ─── Compute all commutators ───
    log("\nComputing commutators [A, B]...")
    seen_perms = {IDENTITY}
    results = []
    total_pairs = len(sequences) ** 2

    for i, (a_seq, a_perm) in enumerate(sequences):
        if i % 20 == 0:
            log(f"  Progress: {i}/{len(sequences)} ({len(results)} unique found)")
        for j, (b_seq, b_perm) in enumerate(sequences):
            comm = commutator(a_perm, b_perm)
            if comm in seen_perms:
                continue
            seen_perms.add(comm)

            effect = classify_effect(comm)
            if effect is None:
                continue

            total_moves = len(a_seq) * 2 + len(b_seq) * 2
            results.append({
                'a_seq': a_seq,
                'b_seq': b_seq,
                'total_moves': total_moves,
                'perm': comm,
                **effect,
            })

    log(f"\nTotal unique non-identity commutators: {len(results)}")

    # ─── Classify ───
    log("\n--- Classification ---")
    corner_only = [r for r in results if r['corner_only']]
    edge_only = [r for r in results if r['edge_only']]
    corner_3c = [r for r in results if r['is_corner_3cycle']]
    edge_3c = [r for r in results if r['is_edge_3cycle']]
    pure_twist = [r for r in results if r['pure_corner_twist'] and r['corners_pos'] == 0]
    pure_flip = [r for r in results if r['pure_edge_flip'] and r['edges_pos'] == 0]

    log(f"  Corner-only:       {len(corner_only)}")
    log(f"  Edge-only:         {len(edge_only)}")
    log(f"  Corner 3-cycles:   {len(corner_3c)}")
    log(f"  Edge 3-cycles:     {len(edge_3c)}")
    log(f"  Pure corner twists:{len(pure_twist)}")
    log(f"  Pure edge flips:   {len(pure_flip)}")

    # ─── Show best results ───
    def show_top(label, items, n=15):
        log(f"\n--- {label} ---")
        items.sort(key=lambda r: (r['total_moves'], r['corners_moved'] + r['edges_moved']))
        for r in items[:n]:
            a_str = ' '.join(r['a_seq'])
            b_str = ' '.join(r['b_seq'])
            details = []
            if r['corners_moved'] > 0:
                details.append(f"C:{r['corners_moved']}(pos={r['corners_pos']},ori={r['corners_ori']})")
            if r['edges_moved'] > 0:
                details.append(f"E:{r['edges_moved']}(pos={r['edges_pos']},ori={r['edges_ori']})")
            if r['corner_cycles']:
                details.append(f"c_cyc={r['corner_cycles']}")
            if r['edge_cycles']:
                details.append(f"e_cyc={r['edge_cycles']}")
            log(f"  [{a_str}, {b_str}] ({r['total_moves']}mv): {', '.join(details)}")

    show_top("Corner-Only Operations", corner_only)
    show_top("Edge-Only Operations", edge_only)
    show_top("Corner 3-Cycles", corner_3c)
    show_top("Edge 3-Cycles", edge_3c)
    show_top("Pure Corner Twists", pure_twist)
    show_top("Pure Edge Flips", pure_flip)

    # ─── Nested commutators (lightweight: only best base × length 1) ───
    log("\n--- Nested Commutators [[A,B], C] (base × single move) ---")
    best_bases = (corner_only[:15] + edge_only[:15])
    single_moves = [(name, perm) for name, perm in gen_perms.items()]
    nested_results = []

    for base in best_bases:
        base_perm = base['perm']
        for c_name, c_perm in single_moves:
            nested = commutator(base_perm, c_perm)
            if nested in seen_perms:
                continue
            seen_perms.add(nested)
            effect = classify_effect(nested)
            if effect is None:
                continue
            total_moves = base['total_moves'] * 2 + 2  # [base, C] = base·C·base'·C'
            nested_results.append({
                'a_seq': [f"[{' '.join(base['a_seq'])},{' '.join(base['b_seq'])}]"],
                'b_seq': [c_name],
                'total_moves': total_moves,
                'perm': nested,
                **effect,
            })

    log(f"Nested commutators found: {len(nested_results)}")
    nested_co = [r for r in nested_results if r['corner_only']]
    nested_eo = [r for r in nested_results if r['edge_only']]
    nested_c3 = [r for r in nested_results if r['is_corner_3cycle']]
    nested_e3 = [r for r in nested_results if r['is_edge_3cycle']]
    log(f"  Nested corner-only: {len(nested_co)}")
    log(f"  Nested edge-only:   {len(nested_eo)}")
    log(f"  Nested corner 3-cycles: {len(nested_c3)}")
    log(f"  Nested edge 3-cycles:   {len(nested_e3)}")

    if nested_c3:
        show_top("Nested Corner 3-Cycles", nested_c3, 5)
    if nested_e3:
        show_top("Nested Edge 3-Cycles", nested_e3, 5)

    # ─── Check for target matches ───
    log("\n--- Target Move Matches ---")
    targets = {'R': tuple(R), 'L': tuple(L), 'F': tuple(F), 'B': tuple(B), 'D': tuple(D)}
    for tname, tperm in targets.items():
        for r in results + nested_results:
            if r['perm'] == tperm:
                log(f"  FOUND {tname}!")
                break
        else:
            log(f"  {tname}: not found (expected — requires longer sequences)")

    # ─── Save library ───
    log("\n--- Saving commutator library ---")
    library = {
        'corner_only': [
            {'a': r['a_seq'], 'b': r['b_seq'], 'moves': r['total_moves'],
             'corner_pos': r['corner_pos'], 'corner_ori': r['corner_ori'],
             'corner_cycles': r['corner_cycles']}
            for r in sorted(corner_only, key=lambda r: r['total_moves'])[:50]
        ],
        'edge_only': [
            {'a': r['a_seq'], 'b': r['b_seq'], 'moves': r['total_moves'],
             'edge_pos': r['edge_pos'], 'edge_ori': r['edge_ori'],
             'edge_cycles': r['edge_cycles']}
            for r in sorted(edge_only, key=lambda r: r['total_moves'])[:50]
        ],
        'corner_3cycles': [
            {'a': r['a_seq'], 'b': r['b_seq'], 'moves': r['total_moves'],
             'corner_pos': r['corner_pos']}
            for r in sorted(corner_3c, key=lambda r: r['total_moves'])[:20]
        ],
        'edge_3cycles': [
            {'a': r['a_seq'], 'b': r['b_seq'], 'moves': r['total_moves'],
             'edge_pos': r['edge_pos']}
            for r in sorted(edge_3c, key=lambda r: r['total_moves'])[:20]
        ],
        'pure_corner_twists': [
            {'a': r['a_seq'], 'b': r['b_seq'], 'moves': r['total_moves'],
             'corner_ori': r['corner_ori']}
            for r in sorted(pure_twist, key=lambda r: r['total_moves'])[:20]
        ],
        'pure_edge_flips': [
            {'a': r['a_seq'], 'b': r['b_seq'], 'moves': r['total_moves'],
             'edge_ori': r['edge_ori']}
            for r in sorted(pure_flip, key=lambda r: r['total_moves'])[:20]
        ],
        'stats': {
            'total_commutators': len(results),
            'nested_commutators': len(nested_results),
        }
    }

    with open('commutator_library.json', 'w') as f:
        json.dump(library, f, indent=2)
    log("Saved to commutator_library.json")

    # ─── Summary ───
    log("\n" + "=" * 60)
    log("SUMMARY")
    log("=" * 60)
    log(f"Commutators found: {len(results)} direct + {len(nested_results)} nested")
    log(f"Corner-only: {len(corner_only)} (3-cycles: {len(corner_3c)})")
    log(f"Edge-only:   {len(edge_only)} (3-cycles: {len(edge_3c)})")
    log(f"Pure twists: {len(pure_twist)} corner, {len(pure_flip)} edge")

    if corner_3c and edge_3c:
        log("\nWe have both corner and edge 3-cycles!")
        log("This is sufficient to build a complete two-phase solver.")
    else:
        missing = []
        if not corner_3c: missing.append("corner 3-cycles")
        if not edge_3c: missing.append("edge 3-cycles")
        log(f"\nStill need: {', '.join(missing)}")


if __name__ == '__main__':
    main()
