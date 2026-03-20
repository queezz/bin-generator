from pathlib import Path

from .bin import make_bin, export as export_model


def export_bin(
    path: str | Path,
    x: float = 70,
    y: float = 50,
    h: float = 19.5,
    wall: float = 1.2,
    clearance: float = 0.6,
    lip_h: float = 3,
    ramp_h: float = 1.5,
    small_r: float = 8,
    big_r: float = 10,
    ear_offset: float = 1.9,
    ears: bool = False,
    fmt: str = "stl",
) -> Path:
    """Create a bin model and export it."""
    out_path = Path(path)
    name = out_path.stem
    bin_model = make_bin(
        x=x,
        y=y,
        h=h,
        wall=wall,
        clearance=clearance,
        lip_h=lip_h,
        ramp_h=ramp_h,
        small_r=small_r,
        big_r=big_r,
        ear_offset=ear_offset,
        ears=ears,
    )
    export_model(bin_model, out_path, fmt=fmt)
    return out_path
