import cadquery as cq
from pathlib import Path

from .ears import make_ear


def rounded_rect_sketch(x, y, r):
    return cq.Sketch().rect(x, y).vertices().fillet(r)


def build_bin_shell(
    x,
    y,
    h,
    wall,
    bottom_offset,
    lip_h,
    ramp_h,
    small_r,
    big_r,
):

    small_x = x - bottom_offset
    small_y = y - bottom_offset

    lip = (
        cq.Workplane("XY")
        .placeSketch(rounded_rect_sketch(small_x, small_y, small_r))
        .extrude(lip_h)
    )

    ramp_bottom = (
        cq.Workplane("XY")
        .workplane(offset=lip_h)
        .placeSketch(rounded_rect_sketch(small_x, small_y, small_r))
    )

    ramp_top = (
        cq.Workplane("XY")
        .workplane(offset=lip_h + ramp_h)
        .placeSketch(rounded_rect_sketch(x, y, big_r))
    )

    ramp = ramp_bottom.add(ramp_top).loft()

    walls = (
        cq.Workplane("XY")
        .workplane(offset=lip_h + ramp_h)
        .placeSketch(rounded_rect_sketch(x, y, big_r))
        .extrude(h - lip_h - ramp_h)
    )

    outer = lip.union(ramp).union(walls)

    model = outer.faces(">Z").shell(-wall).edges("<Z").chamfer(0.4)

    return model


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
    bottom_offset=3,
    lip_h=3.0,
    ramp_h=1.5,
    small_r=8.0,
    big_r=10.0,
    ear_offset=1.9,
    ears=True,
):

    model = build_bin_shell(
        x,
        y,
        h,
        wall,
        bottom_offset,
        lip_h,
        ramp_h,
        small_r,
        big_r,
    )

    if ears:
        model = place_ears(model, x, y, h, ear_offset)

    return model


def export(model, path, fmt: str = "stl"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if fmt in ("stl", "both"):
        cq.exporters.export(model, str(path.with_suffix(".stl")))

    if fmt in ("step", "both"):
        cq.exporters.export(model, str(path.with_suffix(".step")))
