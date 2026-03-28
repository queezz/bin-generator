import cadquery as cq
from pathlib import Path

from .ears import make_ear
from .pattern import place_wall_pattern


def rounded_rect_sketch(x, y, r):
    return cq.Sketch().rect(x, y).vertices().fillet(r)


def make_inset_wall(small_x, small_y, small_r, inset_h):
    return (
        cq.Workplane("XY")
        .placeSketch(rounded_rect_sketch(small_x, small_y, small_r))
        .extrude(inset_h)
    )


def make_ramp(small_x, small_y, x, y, small_r, big_r, inset_h, ramp_h):
    bottom = (
        cq.Workplane("XY")
        .workplane(offset=inset_h)
        .placeSketch(rounded_rect_sketch(small_x, small_y, small_r))
    )

    top = (
        cq.Workplane("XY")
        .workplane(offset=inset_h + ramp_h)
        .placeSketch(rounded_rect_sketch(x, y, big_r))
    )

    return bottom.add(top).loft()


def make_walls(x, y, big_r, z0, height):
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .placeSketch(rounded_rect_sketch(x, y, big_r))
        .extrude(height)
    )


def build_bin_shell(
    x, y, h, wall,
    clearance, inset_h, max_overhang_angle,
    small_r, big_r,
    use_ramp
):
    parts = []

    if use_ramp:
        inset_x = x - 2 * wall - clearance
        inset_y = y - 2 * wall - clearance

        import math

        dx = (x - inset_x) / 2
        ramp_h = dx / math.tan(math.radians(max_overhang_angle))

        parts.append(make_inset_wall(inset_x, inset_y, small_r, inset_h))
        parts.append(make_ramp(
            inset_x, inset_y,
            x, y,
            small_r, big_r,
            inset_h, ramp_h
        ))

        z0 = inset_h + ramp_h
    else:
        z0 = 0

    parts.append(make_walls(x, y, big_r, z0, h - z0))

    outer = parts[0]
    for p in parts[1:]:
        outer = outer.union(p)

    return outer.faces(">Z").shell(-wall).edges("<Z").chamfer(0.4)


def place_ears(model, x, y, h, ear_offset):

    ear_z = h - 10

    ear_points = [
        (x / 2 - ear_offset, y / 2 - ear_offset),
        (-x / 2 + ear_offset, y / 2 - ear_offset),
        (x / 2 - ear_offset, -y / 2 + ear_offset),
        (-x / 2 + ear_offset, -y / 2 + ear_offset),
    ]

    for px, py in ear_points:

        origin = cq.Vector(px, py, ear_z)

        sx = 1 if px > 0 else -1
        sy = 1 if py > 0 else -1

        # 45° corner bisector
        direction = cq.Vector(sx, sy, 0)

        ear = make_ear(origin=origin, direction=direction)

        model = model.union(ear)

    return model


def make_bin(
    x=70.0,
    y=50.0,
    h=19.5,
    wall=1.2,
    clearance=0.6,
    inset_h=3.0,
    max_overhang_angle=50,
    small_r=8.0,
    big_r=10.0,
    ear_offset=1.9,
    ears=True,
    use_ramp=True,
    pattern=False,
    pattern_params=None,
):

    model = build_bin_shell(
        x,
        y,
        h,
        wall,
        clearance,
        inset_h,
        max_overhang_angle,
        small_r,
        big_r,
        use_ramp
    )

    if ears:
        model = place_ears(model, x, y, h, ear_offset)

    patt = None
    if pattern:
        patt = place_wall_pattern(
            x=x,
            y=y,
            h=h,
            big_r=big_r,
            **(pattern_params or {}),
        )

    if pattern and patt:
        model = cq.Workplane("XY").newObject(
            model.val().Solids() + patt.val().Solids()
        )

    return model


def export(model, path, fmt: str = "stl"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if fmt in ("stl", "both"):
        cq.exporters.export(model, str(path.with_suffix(".stl")))

    if fmt in ("step", "both"):
        cq.exporters.export(model, str(path.with_suffix(".step")))


# model = make_bin(
#     x=70,
#     y=50,
#     h=40,
#     pattern=True,
#     pattern_params={
#         "delta_pattern": 4.0,
#         "delta_h": 6.0,
#         "r_sphere": 0.8,
#     }
# )
