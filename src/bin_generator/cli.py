import argparse
from pathlib import Path

from .export import export_bin


def _format_dim(v: float) -> str:
    if float(v).is_integer():
        return str(int(v))
    return f"{v:g}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a parametric storage bin (STL and STEP)."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("bin"),
        help=(
            "Output path stem (default: bin). By default the CLI appends "
            "'-{x}-{y}-{h}' to the stem."
        ),
    )
    parser.add_argument("--x", type=float, default=70, help="Bin length (X)")
    parser.add_argument("--y", type=float, default=50, help="Bin width (Y)")
    parser.add_argument("--h", type=float, default=19.5, help="Bin height (Z)")
    parser.add_argument("--wall", type=float, default=1.2, help="Wall thickness")
    parser.add_argument(
        "--clearance",
        type=float,
        default=0.6,
        help="Stacking clearance gap",
    )
    parser.add_argument("--lip-h", type=float, default=3, help="Lip height")
    parser.add_argument("--ramp-h", type=float, default=1.5, help="Ramp height")
    parser.add_argument("--small-r", type=float, default=8, help="Lip corner radius")
    parser.add_argument("--big-r", type=float, default=10, help="Wall corner radius")
    parser.add_argument(
        "--ear-offset",
        type=float,
        default=1.9,
        help="Ear placement offset from corner",
    )
    parser.add_argument(
        "--noears",
        dest="ears",
        action="store_false",
        help="Disable mounting ears",
    )
    parser.set_defaults(ears=True)
    parser.add_argument(
        "--format",
        choices=["stl", "step", "both"],
        default="stl",
        help="Output format (default: stl)",
    )
    parser.add_argument(
        "--suppress-default-suffix",
        action="store_true",
        help="Do not append '-{x}-{y}-{h}' to the output filename",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(args=argv)

    out_path = Path(args.output)
    if not args.suppress_default_suffix:
        suffix = f"-{_format_dim(args.x)}-{_format_dim(args.y)}-{_format_dim(args.h)}"
        out_path = out_path.with_name(f"{out_path.stem}{suffix}{out_path.suffix}")

    out = export_bin(
        path=out_path,
        x=args.x,
        y=args.y,
        h=args.h,
        wall=args.wall,
        clearance=args.clearance,
        lip_h=args.lip_h,
        ramp_h=args.ramp_h,
        small_r=args.small_r,
        big_r=args.big_r,
        ear_offset=args.ear_offset,
        ears=args.ears,
        fmt=args.format,
    )
    print(f"Exported '{out.stem}' as format '{args.format}'")


if __name__ == "__main__":
    main()
