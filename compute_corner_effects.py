#!/usr/bin/env python3
"""
Compute how each crawler generator affects corner positions and orientations.
Output C code for the IDA* solver.
"""
import sys
sys.path.insert(0, '.')
from crawler_macros import (
    IDENTITY, CRAWL_PX, CRAWL_MX, CRAWL_PZ, CRAWL_MZ, SPIN1, SPIN1_P,
    R, R_prime, L, L_prime, F, F_prime, B, B_prime, D, D_prime, U, U_prime,
    compose, invert
)

# Corner definitions: (U/D face sticker, clockwise sticker, counter-clockwise sticker)
# The U/D face sticker defines orientation 0
CORNERS = [
    (8, 9, 20),    # 0: URF - U(2,2), R(0,0), F(0,2)
    (2, 11, 45),   # 1: URB - U(0,2), R(0,2), B(0,0) -- WAIT
]

# Let me verify by checking what R move does to corners
# R_arr = [0, 1, 20, 3, 4, 23, 6, 7, 26, 15, 12, 9, 16, 13, 10, 17, 14, 11, 18, 19, 29, 21, 22, 32, 24, 25, 35, 27, 28, 51, 30, 31, 48, 33, 34, 45, 36, 37, 38, 39, 40, 41, 42, 43, 44, 8, 46, 47, 5, 49, 50, 2, 52, 53]

# Under R (pulls-from):
# pos 2 <- 20 (F sticker goes to U position of URB)
# pos 11 <- 9 (R sticker stays R-type in URB)
# pos 45 <- 8 (U sticker of URF goes to B position of URB)
# So URF piece moves to URB slot, with U sticker at B position -> twist

# Let me carefully define corners based on standard Rubik's cube convention
# Each corner has 3 stickers. The first is the U/D face sticker (defines orientation 0).
# The other two follow CLOCKWISE order when looking at the corner from outside.

# When looking at the U face from above:
#  ULB(3)  .  URB(1)
#    .   U   .
#  ULF(2)  .  URF(0)

# When looking at the D face from below:
#  DLF(6)  .  DRF(4)
#    .   D   .
#  DLB(7)  .  DRB(5)

# Corner sticker positions (U/D sticker, CW sticker, CCW sticker)
# CW/CCW when looking at the corner from outside the cube

# URF: looking at the corner from outside, starting from U sticker going CW: U -> R -> F
CORNER_STICKERS = [
    (8, 9, 20),    # 0: URF
    (2, 45, 11),   # 1: URB - U, B, R (CW from outside looking at corner)
    (6, 18, 38),   # 2: ULF - U, F, L
    (0, 36, 47),   # 3: ULB - U, L, B  (WAIT, need to verify CW order)
    (29, 26, 15),  # 4: DRF - D, F, R
    (35, 17, 51),  # 5: DRB - D, R, B
    (27, 44, 24),  # 6: DLF - D, L, F  (WAIT, need to verify)
    (33, 53, 42),  # 7: DLB - D, B, L
]

# Build reverse lookup: sticker position -> (corner_index, twist)
# twist 0 = U/D sticker, twist 1 = 2nd sticker, twist 2 = 3rd sticker
STICKER_TO_CORNER = {}
for ci, (s0, s1, s2) in enumerate(CORNER_STICKERS):
    STICKER_TO_CORNER[s0] = (ci, 0)
    STICKER_TO_CORNER[s1] = (ci, 1)
    STICKER_TO_CORNER[s2] = (ci, 2)

def get_corner_state(perm):
    """
    Given a pulls-from permutation, compute corner positions and orientations.
    Returns (positions[8], orientations[8]) where:
    - positions[i] = which corner slot piece i is now in
    - orientations[i] = twist of piece i (0, 1, or 2)
    """
    # For each corner slot, find which piece is there and its twist
    slot_piece = [0] * 8
    slot_twist = [0] * 8

    for slot_idx, (s0, s1, s2) in enumerate(CORNER_STICKERS):
        # Sticker at s0 came from position perm[s0]
        orig_pos = perm[s0]  # original position of the sticker now at U/D face position
        if orig_pos not in STICKER_TO_CORNER:
            print(f"ERROR: position {orig_pos} (at slot {slot_idx} pos {s0}) is not a corner sticker!")
            # Check all three positions
            for sp in [s0, s1, s2]:
                op = perm[sp]
                if op in STICKER_TO_CORNER:
                    print(f"  pos {sp} <- {op}: corner {STICKER_TO_CORNER[op]}")
                else:
                    print(f"  pos {sp} <- {op}: NOT a corner sticker")
            return None, None

        piece_idx, twist = STICKER_TO_CORNER[orig_pos]
        slot_piece[slot_idx] = piece_idx
        slot_twist[slot_idx] = twist  # 0 means correctly oriented

    # Convert from "slot -> piece" to "piece -> slot"
    positions = [0] * 8
    orientations = [0] * 8
    for slot_idx in range(8):
        piece_idx = slot_piece[slot_idx]
        positions[piece_idx] = slot_idx
        orientations[piece_idx] = slot_twist[slot_idx]

    return positions, orientations


# Verify with identity
pos, ori = get_corner_state(IDENTITY)
print(f"Identity corners: pos={pos}, ori={ori}")
assert pos == list(range(8)), "Identity should have each piece in its slot"
assert ori == [0]*8, "Identity should have all orientations 0"

# Verify with R
print(f"\nR perm first 20: {list(R)[:20]}")
pos_R, ori_R = get_corner_state(R)
print(f"R corners: pos={pos_R}, ori={ori_R}")
# Under R: URF->DRF->DRB->URB->URF (pieces 0->4->5->1->0 cyclically)
# In "piece -> slot" notation:
# piece 0 (was in slot 0=URF) -> slot 1 (URB)
# piece 1 (was in slot 1=URB) -> slot 0 (URF) WAIT, that's wrong
# Actually R cycles: URF -> URB -> DRB -> DRF -> URF
# slot 0=URF, slot 1=URB, slot 5=DRB, slot 4=DRF
# After R: slot 0 gets piece from slot 4 (DRF -> URF)
# Actually R (CW from right): URF goes to URB position
# piece 0 was in slot 0 (URF), after R it's in slot 1 (URB)
# piece 1 was in slot 1 (URB), after R it's in slot 5 (DRB)
# piece 5 was in slot 5 (DRB), after R it's in slot 4 (DRF)
# piece 4 was in slot 4 (DRF), after R it's in slot 0 (URF)
expected_pos = list(range(8))
expected_pos[0] = 1  # piece 0 -> slot 1
expected_pos[1] = 5  # piece 1 -> slot 5
expected_pos[5] = 4  # piece 5 -> slot 4
expected_pos[4] = 0  # piece 4 -> slot 0
print(f"Expected R pos: {expected_pos}")
# Don't assert yet - might have corner numbering wrong

# Now compute the effect of each generator on corner state
GENS = [CRAWL_PX, CRAWL_MX, CRAWL_PZ, CRAWL_MZ, SPIN1, SPIN1_P]
GEN_NAMES = ['+x', '-x', '+z', '-z', 'spin1', "spin1'"]

print("\n=== Generator effects on corners ===")
for gi, (gen, name) in enumerate(zip(GENS, GEN_NAMES)):
    pos, ori = get_corner_state(gen)
    if pos is None:
        print(f"\n{name}: ERROR computing corner state")
        continue
    print(f"\n{name}:")
    print(f"  positions:    {pos}")
    print(f"  orientations: {ori}")

    # Also show as slot permutation
    slot_perm = [0] * 8
    for piece in range(8):
        slot_perm[piece] = pos[piece]
    print(f"  slot_perm: piece[i] goes to slot slot_perm[i] = {slot_perm}")

# Also show target moves
print("\n=== Target move effects on corners ===")
TARGETS = [R, R_prime, L, L_prime, F, F_prime, B, B_prime, D, D_prime, U, U_prime]
TARGET_NAMES = ['R', "R'", 'L', "L'", 'F', "F'", 'B', "B'", 'D', "D'", 'U', "U'"]
for target, name in zip(TARGETS, TARGET_NAMES):
    pos, ori = get_corner_state(target)
    if pos is None:
        print(f"\n{name}: ERROR")
        continue
    print(f"\n{name}: pos={pos}, ori={ori}")

# Edge definitions
# 12 edges, each with 2 sticker positions
# First sticker is the "reference" (defines orientation 0)
# Edges on U layer (reference = U sticker):
#   UF: U(2,1)=7, F(0,1)=19
#   UR: U(1,2)=5, R(0,1)=10
#   UB: U(0,1)=1, B(0,1)=46
#   UL: U(1,0)=3, L(0,1)=37

# Edges on D layer (reference = D sticker):
#   DF: D(0,1)=28, F(2,1)=25
#   DR: D(1,2)=32, R(2,1)=16
#   DB: D(2,1)=34, B(2,1)=52
#   DL: D(1,0)=30, L(2,1)=43

# Edges on middle layer (reference = F/B sticker):
#   FR: F(1,2)=23, R(1,0)=12
#   FL: F(1,0)=21, L(1,2)=41
#   BR: B(1,0)=48, R(1,2)=14
#   BL: B(1,2)=50, L(1,0)=39

EDGE_STICKERS = [
    (7, 19),    # 0: UF
    (5, 10),    # 1: UR
    (1, 46),    # 2: UB
    (3, 37),    # 3: UL
    (28, 25),   # 4: DF
    (32, 16),   # 5: DR
    (34, 52),   # 6: DB
    (30, 43),   # 7: DL
    (23, 12),   # 8: FR
    (21, 41),   # 9: FL
    (48, 14),   # 10: BR
    (50, 39),   # 11: BL
]

EDGE_STICKER_TO_EDGE = {}
for ei, (s0, s1) in enumerate(EDGE_STICKERS):
    EDGE_STICKER_TO_EDGE[s0] = (ei, 0)
    EDGE_STICKER_TO_EDGE[s1] = (ei, 1)

def get_edge_state(perm):
    """Compute edge positions and orientations from a permutation."""
    slot_piece = [0] * 12
    slot_flip = [0] * 12

    for slot_idx, (s0, s1) in enumerate(EDGE_STICKERS):
        orig_pos = perm[s0]
        if orig_pos in EDGE_STICKER_TO_EDGE:
            piece_idx, flip = EDGE_STICKER_TO_EDGE[orig_pos]
            slot_piece[slot_idx] = piece_idx
            slot_flip[slot_idx] = flip
        else:
            print(f"ERROR: edge slot {slot_idx} pos {s0} <- {orig_pos} not an edge sticker")
            return None, None

    positions = [0] * 12
    orientations = [0] * 12
    for slot_idx in range(12):
        piece_idx = slot_piece[slot_idx]
        positions[piece_idx] = slot_idx
        orientations[piece_idx] = slot_flip[slot_idx]

    return positions, orientations

# Verify edges with identity
epos, eori = get_edge_state(IDENTITY)
print(f"\n\n=== Edge verification ===")
print(f"Identity edges: pos={epos}, ori={eori}")
assert epos == list(range(12))
assert eori == [0]*12

print("\n=== Generator effects on edges ===")
for gi, (gen, name) in enumerate(zip(GENS, GEN_NAMES)):
    epos, eori = get_edge_state(gen)
    if epos is None:
        continue
    print(f"\n{name}: pos={epos}, ori={eori}")

print("\n=== Target move effects on edges ===")
for target, name in zip(TARGETS, TARGET_NAMES):
    epos, eori = get_edge_state(target)
    if epos is None:
        continue
    print(f"\n{name}: pos={epos}, ori={eori}")


# Now output C-compatible arrays for the corner transformations
print("\n\n=== C code for corner transformations ===")
print("// Corner position permutation: gen_corner_perm[gen][piece] = new_slot")
print("// Corner orientation delta: gen_corner_ori[gen][piece] = orientation_change")
print("static const uint8_t gen_corner_perm[6][8] = {")
for gi, (gen, name) in enumerate(zip(GENS, GEN_NAMES)):
    pos, ori = get_corner_state(gen)
    # pos[piece] = slot it moves to
    # But we need: for each SLOT, which piece is there, and with what twist
    # Actually for the BFS, we need to know how applying this generator transforms
    # the corner state.
    # If piece i is currently in slot s, after applying gen, piece i is in slot pos[i].
    # But wait - pos is computed from the generator alone (applied to identity).
    # For a general state, the transformation is:
    #   new_position[piece] = ???
    # Actually, the corner permutation induced by the generator is:
    #   slot_to_slot[old_slot] = new_slot
    # This maps: a piece in old_slot goes to new_slot.
    # From pos[piece] = new_slot when piece was in slot=piece (identity):
    # slot_to_slot[piece] = pos[piece]
    # So slot_to_slot = pos (they're the same since we start from identity)

    # For orientation: the orientation change when a piece moves from old_slot to new_slot
    # depends on the move, not the piece.
    # ori_delta[old_slot] = orientation change
    # From identity: piece i was in slot i with orientation 0.
    # After gen: piece i is in slot pos[i] with orientation ori[i].
    # So ori_delta[i] = ori[i] (orientation change for a piece moving from slot i)

    # WAIT - this isn't quite right. The orientation change depends on which slot
    # the piece CAME FROM, not which piece it is. Since at identity, piece i is in slot i,
    # the orientation change for pieces coming from slot i is ori[i].

    # For a general state: if piece P is in slot S, and the generator moves
    # pieces from slot S to slot slot_to_slot[S], then:
    # new_position[P] = slot_to_slot[S]
    # new_orientation[P] = (old_orientation[P] + ori_delta[S]) % 3
    # where ori_delta[S] = ori[piece that was in S at identity] = ori[S]

    print(f"    {{{', '.join(str(x) for x in pos)}}},  // {name}")
print("};")

print("static const uint8_t gen_corner_ori[6][8] = {")
for gi, (gen, name) in enumerate(zip(GENS, GEN_NAMES)):
    pos, ori = get_corner_state(gen)
    print(f"    {{{', '.join(str(x) for x in ori)}}},  // {name}")
print("};")

# Also output for the slot-based transformation
# gen_corner_slot_perm[gen][slot] = new_slot (piece at slot goes to new_slot)
# gen_corner_slot_ori[gen][slot] = ori_delta (orientation change for piece leaving slot)
print("\n// Slot-based: gen_slot_perm[gen][old_slot] = new_slot")
print("// gen_slot_ori[gen][old_slot] = orientation delta")
print("static const uint8_t gen_slot_perm[6][8] = {")
for gi, (gen, name) in enumerate(zip(GENS, GEN_NAMES)):
    pos, ori = get_corner_state(gen)
    # pos[piece] = slot for piece (from identity). Since identity has piece=slot,
    # this IS the slot-to-slot mapping.
    print(f"    {{{', '.join(str(x) for x in pos)}}},  // {name}")
print("};")
print("static const uint8_t gen_slot_ori[6][8] = {")
for gi, (gen, name) in enumerate(zip(GENS, GEN_NAMES)):
    pos, ori = get_corner_state(gen)
    print(f"    {{{', '.join(str(x) for x in ori)}}},  // {name}")
print("};")

# Verify: applying +x to identity corners should give the +x corner state
# Also verify composition: (+x)(+z) should give the expected corner state
composed = tuple(CRAWL_PX[CRAWL_PZ[i]] for i in range(54))
pos_c, ori_c = get_corner_state(composed)
print(f"\n// Verification: +z then +x corner state: pos={pos_c}, ori={ori_c}")

# Compute manually:
pos_pz, ori_pz = get_corner_state(CRAWL_PZ)
pos_px, ori_px = get_corner_state(CRAWL_PX)
# After +z: piece i is in slot pos_pz[i] with orientation ori_pz[i]
# After +x: slot s goes to slot pos_px[s] with delta ori_px[s]
# So piece i: new_slot = pos_px[pos_pz[i]], new_ori = (ori_pz[i] + ori_px[pos_pz[i]]) % 3
manual_pos = [pos_px[pos_pz[i]] for i in range(8)]
manual_ori = [(ori_pz[i] + ori_px[pos_pz[i]]) % 3 for i in range(8)]
print(f"// Manual composition: pos={manual_pos}, ori={manual_ori}")
print(f"// Match: pos={'OK' if manual_pos == pos_c else 'FAIL'}, ori={'OK' if manual_ori == ori_c else 'FAIL'}")

# Also output edge transformations
print("\n\n=== C code for edge transformations ===")
print("static const uint8_t gen_edge_perm[6][12] = {")
for gi, (gen, name) in enumerate(zip(GENS, GEN_NAMES)):
    epos, eori = get_edge_state(gen)
    print(f"    {{{', '.join(str(x) for x in epos)}}},  // {name}")
print("};")
print("static const uint8_t gen_edge_ori[6][12] = {")
for gi, (gen, name) in enumerate(zip(GENS, GEN_NAMES)):
    epos, eori = get_edge_state(gen)
    print(f"    {{{', '.join(str(x) for x in eori)}}},  // {name}")
print("};")

# Output target corner/edge states
print("\n\n=== Target corner states ===")
targets_short = [(R, 'R'), (L, 'L'), (F, 'F'), (B, 'B'), (D, 'D')]
for target, name in targets_short:
    pos, ori = get_corner_state(target)
    epos, eori = get_edge_state(target)
    print(f"// {name}: corner_pos={pos}, corner_ori={ori}")
    print(f"// {name}: edge_pos={epos}, edge_ori={eori}")
