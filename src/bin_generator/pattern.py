import cadquery as cq
import math


def make_bump(length=18, height=8, depth=0.8):
    """Bump in wall-local sense: length along edge, height along bin H, depth outward."""
    wp = cq.Workplane("XY").box(length, height, depth, centered=(True, True, False))

    # chamfer top edges slightly
    wp = wp.edges(">Z").chamfer(depth - 0.01)

    # safe fillet (like you did)
    bb = wp.faces(">Z").val().BoundingBox()
    limit = min(bb.xlen, bb.ylen) / 2.0
    r = min(3 * depth, 0.99 * limit)

    wp = wp.edges(">Z").fillet(r)

    return wp.val()


def bump_wall_location(px, py, z, p0, p1, normal):
    """Wall-aligned placement: depth = outward normal, length = along edge."""
    n = cq.Vector(normal.x, normal.y, normal.z)
    if n.Length < 1e-12:
        n = cq.Vector(0, 0, 1)
    else:
        n = n.normalized()

    t = cq.Vector(p1.x - p0.x, p1.y - p0.y, p1.z - p0.z)
    if t.Length < 1e-12:
        t = cq.Vector(1, 0, 0)
    else:
        t = t.normalized()

    t = t - n * t.dot(n)
    if t.Length < 1e-12:
        t = cq.Vector(0, 0, 1).cross(n)
        if t.Length < 1e-12:
            t = cq.Vector(1, 0, 0)
        else:
            t = t.normalized()
    else:
        t = t.normalized()

    origin = cq.Vector(px, py, z)
    return cq.Plane(origin, t, n).location


# -------------------------------
# 1. GEOMETRY: edges + normals
# -------------------------------
def get_edges_with_normals(x, y, big_r):
    hx = x / 2 - big_r
    hy = y / 2 - big_r

    return [
        # p0, p1, normal
        (cq.Vector(-hx, y / 2, 0), cq.Vector(hx, y / 2, 0), cq.Vector(0, 1, 0)),  # top
        (
            cq.Vector(-hx, -y / 2, 0),
            cq.Vector(hx, -y / 2, 0),
            cq.Vector(0, -1, 0),
        ),  # bottom
        (
            cq.Vector(x / 2, -hy, 0),
            cq.Vector(x / 2, hy, 0),
            cq.Vector(1, 0, 0),
        ),  # right
        (
            cq.Vector(-x / 2, -hy, 0),
            cq.Vector(-x / 2, hy, 0),
            cq.Vector(-1, 0, 0),
        ),  # left
    ]


# -------------------------------
# 2. SAMPLING (fixed!)
# -------------------------------
def sample_line(p0, p1, pitch, xy_margin, phase, big_r=10.0):
    dx = p1.x - p0.x
    dy = p1.y - p0.y
    L = math.hypot(dx, dy)

    if L < 1e-6:
        return None

    tx = dx / L
    ty = dy / L

    usable = L - 2 * xy_margin
    if usable <= 0:
        return None

    return (tx, ty, usable, L)


# -------------------------------
# 4. FULL PATTERN (Z STACK)
# -------------------------------
def place_wall_pattern(
    x,
    y,
    h,
    big_r=10.0,
    pitch=25.0,
    delta_h=10.0,
    bump_length=18.0,
    bump_height=8.0,
    bump_depth=0.8,
    z_margin_top=5.0,
    z_margin_bottom=10.0,
    xy_margin=0.0,
    offset_factor=0.0,
):
    all_solids = []

    base = make_bump(
        length=bump_length,
        height=bump_height,
        depth=bump_depth,
    )

    z = z_margin_bottom
    layer_index = 0

    edges = get_edges_with_normals(x, y, big_r)

    # Same offset scale as previous default r_sphere=0.6
    normal_offset_scale = 0.6

    while z < h - z_margin_top:
        phase = 0.0 if layer_index % 2 == 0 else pitch * 0.5

        for p0, p1, normal in edges:
            result = sample_line(p0, p1, pitch, xy_margin, phase)
            if result is None:
                continue

            tx, ty, usable, L = result

            gap = pitch - bump_length

            base_s_min = xy_margin + bump_length / 2
            base_s_max = L - xy_margin - bump_length / 2

            phase = 0.0 if layer_index % 2 == 0 else (bump_length + gap) / 2

            s_min = base_s_min + phase
            s_max = base_s_max

            if s_min > s_max:
                n = 0
            else:
                n = int((s_max - s_min) // pitch) + 1

            edge_length_min = 3.0

            allowed_start = xy_margin
            allowed_end = L - xy_margin

            for i in range(-1, n + 1):
                s = s_min + i * pitch

                start = s - bump_length / 2
                end = s + bump_length / 2

                # ---- clip to usable edge ----
                clipped_start = max(start, allowed_start)
                clipped_end = min(end, allowed_end)

                length = clipped_end - clipped_start

                if length < edge_length_min:
                    continue

                # ---- recompute center after clipping ----
                s_clipped = (clipped_start + clipped_end) / 2

                px = p0.x + tx * s_clipped
                py = p0.y + ty * s_clipped

                offset = normal_offset_scale * offset_factor
                px += normal.x * offset
                py += normal.y * offset

                # ---- reuse base if full size ----
                if abs(length - bump_length) < 1e-6:
                    bump = base
                else:
                    bump = make_bump(
                        length=length,
                        height=bump_height,
                        depth=bump_depth,
                    )

                loc = bump_wall_location(px, py, z, p0, p1, normal)
                all_solids.append(bump.moved(loc))
        z += delta_h
        layer_index += 1

    if not all_solids:
        return None

    return cq.Workplane("XY").newObject([cq.Compound.makeCompound(all_solids)])


# result = place_wall_pattern(
#     x=50,
#     y=60,
#     h=40,
#     offset_factor=0.8,
# )
