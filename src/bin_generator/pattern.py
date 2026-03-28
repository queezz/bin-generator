import cadquery as cq
import math


def make_bump(x=10, y=10, z=0.8):
    wp = cq.Workplane("XY").box(x, y, z, centered=(True, True, False))

    # chamfer top edges slightly
    wp = wp.edges(">Z").chamfer(z - 0.01)

    # safe fillet (like you did)
    bb = wp.faces(">Z").val().BoundingBox()
    limit = min(bb.xlen, bb.ylen) / 2.0
    r = min(3 * z, 0.99 * limit)

    wp = wp.edges(">Z").fillet(r)

    return wp.val()


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
def sample_line(p0, p1, spacing, xy_margin, phase, big_r=10.0):
    dx = p1.x - p0.x
    dy = p1.y - p0.y
    L = math.hypot(dx, dy)

    if L < 1e-6:
        return []

    tx = dx / L
    ty = dy / L

    usable = L - 2 * xy_margin
    if usable <= 0:
        return []

    # stable count
    n = max(1, int(round(usable / spacing)))
    step = usable / n

    pts = []
    for i in range(n + 1):
        s = xy_margin + i * step + phase

        # wrap phase instead of dropping points
        s = xy_margin + (s - xy_margin) % usable

        px = p0.x + tx * s
        py = p0.y + ty * s
        pts.append(cq.Vector(px, py, 0))

    return pts


# -------------------------------
# 3. SINGLE LAYER
# -------------------------------
def make_pattern_layer(
    x,
    y,
    big_r,
    z,
    delta_pattern,
    r_sphere,
    xy_margin,
    phase=0.0,
):
    edges = get_edges_with_normals(x, y, big_r)

    base = make_bump()
    solids = []

    for p0, p1, normal in edges:
        pts = sample_line(p0, p1, delta_pattern, xy_margin, phase)

        for p in pts:
            loc = cq.Location(cq.Vector(p.x, p.y, z))
            solids.append(base.moved(loc))

    if not solids:
        return None

    comp = cq.Compound.makeCompound(solids)
    return cq.Workplane("XY").newObject([comp])


# -------------------------------
# 4. FULL PATTERN (Z STACK)
# -------------------------------
def place_wall_pattern(
    x,
    y,
    h,
    big_r=10.0,
    delta_pattern=6.0,
    delta_h=6.0,
    r_sphere=0.6,
    z_margin_top=2.0,
    z_margin_bottom=2.0,
    xy_margin=3.0,
    offset_factor=0.0,
):
    all_solids = []

    # build ONE bump
    base = make_bump(x=5, y=5, z=0.8)

    z = z_margin_bottom
    layer_index = 0

    edges = get_edges_with_normals(x, y, big_r)

    while z < h - z_margin_top:
        phase = 0.0 if layer_index % 2 == 0 else delta_pattern * 0.5

        for p0, p1, normal in edges:
            pts = sample_line(p0, p1, delta_pattern, xy_margin, phase)

            for p in pts:
                offset = r_sphere * offset_factor
                px = p.x + normal.x * offset
                py = p.y + normal.y * offset
                loc = cq.Location(cq.Vector(px, py, z))
                all_solids.append(base.moved(loc))

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
