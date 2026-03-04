#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import re
from pathlib import Path
from typing import Any

TTFont = importlib.import_module("fontTools.ttLib").TTFont


def sanitize_postscript_name(value: str) -> str:
    cleaned = re.sub(r"\s+", "", value)
    return re.sub(r"[^A-Za-z0-9_-]", "", cleaned)


def filename_prefix(value: str) -> str:
    cleaned = re.sub(r"\s+", "", value)
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "", cleaned)
    return cleaned or "MixedFont"


def parse_style_from_filename(font_path: Path) -> str:
    stem = font_path.stem
    if "-" not in stem:
        raise ValueError(f"Could not parse style from filename: {font_path.name}")
    return stem.rsplit("-", 1)[1]


def is_italic_style(style_name: str) -> bool:
    return style_name.lower().endswith("italic")


def collect_style_map(font_dir: Path) -> dict[str, Path]:
    style_map: dict[str, Path] = {}
    for font_path in sorted(font_dir.glob("*.otf")):
        style = parse_style_from_filename(font_path)
        if style in style_map:
            raise ValueError(f"Duplicate style '{style}' in {font_dir}")
        style_map[style] = font_path
    return style_map


def set_name_record(font: Any, name_id: int, value: str) -> None:
    name_table = font["name"]
    existing = [record for record in name_table.names if record.nameID == name_id]
    if not existing:
        name_table.setName(value, name_id, 3, 1, 0x409)
        name_table.setName(value, name_id, 1, 0, 0)
        return

    for record in existing:
        name_table.setName(value, name_id, record.platformID, record.platEncID, record.langID)


def update_naming(font: Any, family_name: str, style_name: str) -> None:
    ps_family = sanitize_postscript_name(family_name)
    ps_style = sanitize_postscript_name(style_name)
    full_name = f"{family_name} {style_name}".strip()
    postscript_name = f"{ps_family}-{ps_style}".strip("-")

    set_name_record(font, 1, family_name)              # Font Family name
    set_name_record(font, 2, style_name)               # Font Subfamily name
    set_name_record(font, 3, f"{full_name};Mixed")    # Unique font identifier
    set_name_record(font, 4, full_name)                # Full font name
    set_name_record(font, 6, postscript_name)          # PostScript name
    set_name_record(font, 16, family_name)             # Typographic Family
    set_name_record(font, 17, style_name)              # Typographic Subfamily


def update_italic_style(font: Any, italic_angle: float) -> None:
    if "OS/2" in font:
        os2 = font["OS/2"]
        os2.fsSelection |= 0x0001           # italic bit
        os2.fsSelection &= ~0x0040          # clear regular bit

    if "head" in font:
        head = font["head"]
        head.macStyle |= 0x0002             # italic bit

    if "post" in font:
        post = font["post"]
        post.italicAngle = italic_angle


def update_upright_style(font: Any) -> None:
    if "OS/2" in font:
        os2 = font["OS/2"]
        os2.fsSelection &= ~0x0001          # clear italic bit

    if "head" in font:
        head = font["head"]
        head.macStyle &= ~0x0002            # clear italic bit

    if "post" in font:
        post = font["post"]
        post.italicAngle = 0


def build_font(source_font: Path, output_font: Path, family_name: str, style_name: str, italic_angle: float | None) -> None:
    font = TTFont(source_font)
    update_naming(font, family_name, style_name)

    if is_italic_style(style_name) and italic_angle is not None:
        update_italic_style(font, italic_angle)
    else:
        update_upright_style(font)

    font.save(output_font)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a mixed font family from two source fonts or two source folders."
    )
    parser.add_argument("--regular", type=Path, help="Path to source regular/base font file.")
    parser.add_argument("--italic", type=Path, help="Path to source italic font file.")
    parser.add_argument("--regular-dir", type=Path, help="Directory with base (upright) fonts for all styles.")
    parser.add_argument("--italic-dir", type=Path, help="Directory with italic fonts for all styles.")
    parser.add_argument("--name", required=True, help="Output family name, e.g. 'Monaspace Frankenstein'.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./mixed-fonts"),
        help="Directory for generated font files (default: ./mixed-fonts).",
    )
    parser.add_argument(
        "--italic-angle",
        type=float,
        default=-12,
        help="Italic angle to write in the italic font's post table (default: -12).",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if a style exists in only one source directory. By default, missing styles are skipped.",
    )
    return parser.parse_args()


def validate_mode(args: argparse.Namespace) -> str:
    file_mode = args.regular is not None or args.italic is not None
    dir_mode = args.regular_dir is not None or args.italic_dir is not None

    if file_mode and dir_mode:
        raise ValueError("Use either file mode (--regular/--italic) or directory mode (--regular-dir/--italic-dir), not both.")

    if file_mode:
        if args.regular is None or args.italic is None:
            raise ValueError("File mode requires both --regular and --italic.")
        return "file"

    if dir_mode:
        if args.regular_dir is None or args.italic_dir is None:
            raise ValueError("Directory mode requires both --regular-dir and --italic-dir.")
        return "dir"

    raise ValueError("Provide either --regular/--italic or --regular-dir/--italic-dir.")


def ensure_writable(targets: list[Path], overwrite: bool) -> None:
    if overwrite:
        return
    for target in targets:
        if target.exists():
            raise FileExistsError(
                f"Output already exists: {target}. Use --overwrite or choose a different --name/--output-dir."
            )


def run_file_mode(args: argparse.Namespace) -> list[Path]:
    if not args.regular.is_file():
        raise FileNotFoundError(f"Regular font not found: {args.regular}")
    if not args.italic.is_file():
        raise FileNotFoundError(f"Italic font not found: {args.italic}")

    ext_regular = args.regular.suffix or ".otf"
    ext_italic = args.italic.suffix or ".otf"

    prefix = filename_prefix(args.name)
    regular_out = args.output_dir / f"{prefix}-Regular{ext_regular}"
    italic_out = args.output_dir / f"{prefix}-Italic{ext_italic}"

    ensure_writable([regular_out, italic_out], args.overwrite)

    build_font(args.regular, regular_out, args.name, "Regular", italic_angle=None)
    build_font(args.italic, italic_out, args.name, "Italic", italic_angle=args.italic_angle)

    return [regular_out, italic_out]


def run_dir_mode(args: argparse.Namespace) -> list[Path]:
    if not args.regular_dir.is_dir():
        raise FileNotFoundError(f"Regular font directory not found: {args.regular_dir}")
    if not args.italic_dir.is_dir():
        raise FileNotFoundError(f"Italic font directory not found: {args.italic_dir}")

    regular_styles = collect_style_map(args.regular_dir)
    italic_styles = collect_style_map(args.italic_dir)

    if not regular_styles:
        raise ValueError(f"No .otf files found in regular directory: {args.regular_dir}")
    if not italic_styles:
        raise ValueError(f"No .otf files found in italic directory: {args.italic_dir}")

    all_styles = sorted(set(regular_styles) | set(italic_styles))
    prefix = filename_prefix(args.name)

    build_plan: list[tuple[str, Path, Path]] = []
    missing_styles: list[str] = []

    for style in all_styles:
        source_map = italic_styles if is_italic_style(style) else regular_styles
        source = source_map.get(style)
        if source is None:
            missing_styles.append(style)
            continue
        out_path = args.output_dir / f"{prefix}-{style}{(source.suffix or '.otf')}"
        build_plan.append((style, source, out_path))

    if missing_styles and args.strict:
        missing_str = ", ".join(missing_styles)
        raise ValueError(f"Missing source fonts for styles: {missing_str}")

    ensure_writable([out for _, _, out in build_plan], args.overwrite)

    created: list[Path] = []
    for style, source, out_path in build_plan:
        italic_angle = args.italic_angle if is_italic_style(style) else None
        build_font(source, out_path, args.name, style, italic_angle=italic_angle)
        created.append(out_path)

    if missing_styles and not args.strict:
        missing_str = ", ".join(missing_styles)
        print(f"Skipped styles with missing source files: {missing_str}")

    return created


def main() -> None:
    args = parse_args()
    mode = validate_mode(args)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    created = run_file_mode(args) if mode == "file" else run_dir_mode(args)

    print("Created mixed fonts:")
    for output in created:
        print(f"- {output}")


if __name__ == "__main__":
    main()
