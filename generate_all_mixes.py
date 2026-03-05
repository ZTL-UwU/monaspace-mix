#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from itertools import product
from pathlib import Path


def parse_repo_from_releases_url(url: str) -> tuple[str, str]:
    cleaned = url.rstrip("/")
    parts = cleaned.split("/")
    if len(parts) < 5 or parts[2] != "github.com":
        raise ValueError(f"Unsupported GitHub releases URL: {url}")
    owner = parts[3]
    repo = parts[4]
    return owner, repo


def fetch_latest_release(owner: str, repo: str) -> dict:
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    request = urllib.request.Request(
        api_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "monaspace-mix-script",
        },
    )
    with urllib.request.urlopen(request) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def choose_zip_asset(release_data: dict, asset_pattern: str) -> dict:
    assets = release_data.get("assets", [])
    if not assets:
        raise ValueError("Release has no downloadable assets")

    pattern = asset_pattern.lower()
    matching = [
        asset
        for asset in assets
        if asset.get("name", "").lower().endswith(".zip")
        and pattern in asset.get("name", "").lower()
    ]
    if matching:
        return matching[0]

    zips = [asset for asset in assets if asset.get("name", "").lower().endswith(".zip")]
    if zips:
        return zips[0]

    raise ValueError("No .zip asset found in release")


def choose_zip_asset_with_filters(
    release_data: dict,
    include_terms: list[str],
    exclude_terms: list[str],
) -> dict:
    assets = [
        asset
        for asset in release_data.get("assets", [])
        if asset.get("name", "").lower().endswith(".zip")
    ]
    if not assets:
        raise ValueError("Release has no downloadable .zip assets")

    include_terms_l = [term.lower() for term in include_terms if term.strip()]
    exclude_terms_l = [term.lower() for term in exclude_terms if term.strip()]

    matching = []
    for asset in assets:
        name = asset.get("name", "").lower()
        if any(term not in name for term in include_terms_l):
            continue
        if any(term in name for term in exclude_terms_l):
            continue
        matching.append(asset)

    if matching:
        return matching[0]

    asset_names = ", ".join(asset.get("name", "") for asset in assets)
    raise ValueError(
        "No matching .zip asset found with include/exclude filters. "
        f"Available ZIP assets: {asset_names}"
    )


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, destination)


def extract_zip(zip_path: Path, extract_root: Path) -> Path:
    target_dir = extract_root / zip_path.stem
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(target_dir)

    return target_dir


def find_nerdfonts_dir(extracted_root: Path) -> Path:
    candidates = [path for path in extracted_root.rglob("NerdFonts") if path.is_dir()]
    if not candidates:
        raise FileNotFoundError(
            f"Could not find NerdFonts directory in {extracted_root}"
        )
    return sorted(candidates, key=lambda path: len(path.parts))[0]


def find_static_fonts_dir(extracted_root: Path) -> Path:
    candidates = [path for path in extracted_root.rglob("Static Fonts") if path.is_dir()]
    if not candidates:
        raise FileNotFoundError(
            f"Could not find Static Fonts directory in {extracted_root}"
        )
    return sorted(candidates, key=lambda path: len(path.parts))[0]


def collect_family_dirs(nerdfonts_dir: Path) -> list[Path]:
    families = [
        path
        for path in sorted(nerdfonts_dir.iterdir())
        if path.is_dir() and path.name.startswith("Monaspace ")
    ]
    if not families:
        raise FileNotFoundError(
            f"No Monaspace family directories found in {nerdfonts_dir}"
        )
    return families


def short_family_name(path: Path) -> str:
    return path.name.replace("Monaspace ", "").strip()


def parse_variants(value: str) -> list[str]:
    variants = [item.strip().lower() for item in value.split(",") if item.strip()]
    valid = {"nf", "non-nf"}
    invalid = [variant for variant in variants if variant not in valid]
    if invalid:
        invalid_str = ", ".join(invalid)
        raise ValueError(f"Unsupported variant(s): {invalid_str}. Use nf,non-nf")
    if not variants:
        raise ValueError("At least one variant must be selected")
    seen: set[str] = set()
    deduped: list[str] = []
    for variant in variants:
        if variant not in seen:
            deduped.append(variant)
            seen.add(variant)
    return deduped


def run_mix(
    mixer_script: Path,
    python_exec: str,
    regular_dir: Path,
    italic_dir: Path,
    family_name: str,
    output_dir: Path,
    overwrite: bool,
) -> None:
    command = [
        python_exec,
        str(mixer_script),
        "--regular-dir",
        str(regular_dir),
        "--italic-dir",
        str(italic_dir),
        "--name",
        family_name,
        "--output-dir",
        str(output_dir),
    ]
    if overwrite:
        command.append("--overwrite")

    process = subprocess.run(command, text=True, capture_output=True)
    if process.returncode != 0:
        if process.stdout:
            print(process.stdout)
        if process.stderr:
            print(process.stderr, file=sys.stderr)
        raise RuntimeError(f"Mix failed for {regular_dir.name} x {italic_dir.name}")


def zip_directory(source_dir: Path, zip_path: Path, overwrite: bool) -> None:
    if zip_path.exists():
        if not overwrite:
            raise FileExistsError(
                f"Output ZIP already exists: {zip_path}. Use --overwrite to replace it."
            )
        zip_path.unlink()

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(source_dir.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, arcname=file_path.relative_to(source_dir))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download Monaspace release ZIP and generate mixed fonts for all family combinations."
    )
    parser.add_argument(
        "--releases-url",
        default="https://github.com/githubnext/monaspace/releases/",
        help="GitHub releases page URL.",
    )
    parser.add_argument(
        "--nf-zip-url",
        help="Optional direct Nerd Fonts ZIP URL.",
    )
    parser.add_argument(
        "--non-nf-zip-url",
        help="Optional direct non-NF static ZIP URL.",
    )
    parser.add_argument(
        "--nf-asset-pattern",
        default="nerdfonts",
        help="Pattern to choose NF ZIP asset from latest release.",
    )
    parser.add_argument(
        "--non-nf-asset-pattern",
        default="static",
        help="Pattern to choose non-NF ZIP asset from latest release.",
    )
    parser.add_argument(
        "--variants",
        default="nf,non-nf",
        help="Comma-separated variants to generate: nf,non-nf (default: both).",
    )
    parser.add_argument(
        "--download-dir",
        type=Path,
        default=Path("./downloads"),
        help="Where ZIP files are stored.",
    )
    parser.add_argument(
        "--extract-dir",
        type=Path,
        default=Path("./extracted"),
        help="Where ZIP content is extracted.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("./all-combinations"),
        help="Root folder containing one output directory per combination.",
    )
    parser.add_argument(
        "--zip-output",
        action="store_true",
        help="Create one ZIP file per generated combination.",
    )
    parser.add_argument(
        "--zip-dir",
        type=Path,
        default=Path("./all-combinations-zips"),
        help="Where generated ZIP files are written (used with --zip-output).",
    )
    parser.add_argument(
        "--zip-only",
        action="store_true",
        help="Remove combination output directories after creating ZIP files (implies --zip-output).",
    )
    parser.add_argument(
        "--include-self",
        action="store_true",
        help="Include combinations where regular and italic families are the same (disabled by default).",
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing generated files."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional limit for number of combinations to generate (0 = no limit).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    variants = parse_variants(args.variants)
    owner, repo = parse_repo_from_releases_url(args.releases_url)
    release_data = fetch_latest_release(owner, repo)

    mixer_script = Path(__file__).with_name("mix_fonts.py")
    if not mixer_script.exists():
        raise FileNotFoundError(f"Could not find mixer script: {mixer_script}")

    args.output_root.mkdir(parents=True, exist_ok=True)
    if args.zip_only:
        args.zip_output = True
    if args.zip_output:
        args.zip_dir.mkdir(parents=True, exist_ok=True)

    variant_totals: dict[str, int] = {}
    multi_variant = len(variants) > 1

    for variant in variants:
        if variant == "nf":
            if args.nf_zip_url:
                zip_url = args.nf_zip_url
                zip_name = Path(zip_url.split("?")[0]).name or "monaspace-nerdfonts.zip"
            else:
                asset = choose_zip_asset_with_filters(
                    release_data,
                    include_terms=[args.nf_asset_pattern],
                    exclude_terms=["webfont"],
                )
                zip_url = asset["browser_download_url"]
                zip_name = asset["name"]
            fonts_root_finder = find_nerdfonts_dir
            variant_label = "NF"
            variant_suffix = " NF"
        else:
            if args.non_nf_zip_url:
                zip_url = args.non_nf_zip_url
                zip_name = Path(zip_url.split("?")[0]).name or "monaspace-static.zip"
            else:
                asset = choose_zip_asset_with_filters(
                    release_data,
                    include_terms=[args.non_nf_asset_pattern],
                    exclude_terms=["webfont", "nerdfonts"],
                )
                zip_url = asset["browser_download_url"]
                zip_name = asset["name"]
            fonts_root_finder = find_static_fonts_dir
            variant_label = "non-NF"
            variant_suffix = ""

        zip_path = args.download_dir / zip_name
        print(f"[{variant_label}] Downloading: {zip_url}")
        if not zip_path.exists():
            download_file(zip_url, zip_path)

        print(f"[{variant_label}] Extracting: {zip_path}")
        extracted_root = extract_zip(zip_path, args.extract_dir)

        fonts_root = fonts_root_finder(extracted_root)
        family_dirs = collect_family_dirs(fonts_root)

        combinations: list[tuple[Path, Path]] = []
        for regular_dir, italic_dir in product(family_dirs, family_dirs):
            if not args.include_self and regular_dir == italic_dir:
                continue
            combinations.append((regular_dir, italic_dir))

        if args.limit > 0:
            combinations = combinations[: args.limit]

        if not combinations:
            raise ValueError(f"No family combinations to process for variant: {variant}")

        variant_output_root = args.output_root / variant if multi_variant else args.output_root
        variant_output_root.mkdir(parents=True, exist_ok=True)

        total = len(combinations)
        variant_totals[variant] = total
        for index, (regular_dir, italic_dir) in enumerate(combinations, start=1):
            regular_short = short_family_name(regular_dir)
            italic_short = short_family_name(italic_dir)
            family_name = f"Monaspace Mix {regular_short}-{italic_short}{variant_suffix}"
            combo_dir_name = f"Monaspace-Mix-{regular_short}-{italic_short}"
            if variant == "nf":
                combo_dir_name = f"{combo_dir_name}-NF"
            combo_out_dir = variant_output_root / combo_dir_name

            print(
                f"[{variant_label}] [{index}/{total}] {regular_short} + {italic_short} -> {combo_out_dir}"
            )
            run_mix(
                mixer_script=mixer_script,
                python_exec=sys.executable,
                regular_dir=regular_dir,
                italic_dir=italic_dir,
                family_name=family_name,
                output_dir=combo_out_dir,
                overwrite=args.overwrite,
            )

            if args.zip_output:
                zip_name_base = f"{regular_short}-{italic_short}"
                if variant == "nf":
                    zip_name_base = f"{zip_name_base}-NF"
                zip_path = args.zip_dir / f"{zip_name_base}.zip"
                zip_directory(combo_out_dir, zip_path, overwrite=args.overwrite)
                print(f"  Zipped -> {zip_path}")
                if args.zip_only:
                    shutil.rmtree(combo_out_dir)
                    print(f"  Removed directory -> {combo_out_dir}")

    print("Done. Generated combinations:")
    for variant in variants:
        variant_label = "NF" if variant == "nf" else "non-NF"
        count = variant_totals.get(variant, 0)
        if args.zip_output and args.zip_only:
            print(f"- {variant_label}: {count} ZIP files in {args.zip_dir}")
        elif args.zip_output:
            variant_output_root = args.output_root / variant if multi_variant else args.output_root
            print(f"- {variant_label}: {count} families in {variant_output_root}")
            print(f"- {variant_label}: {count} ZIP files in {args.zip_dir}")
        else:
            variant_output_root = args.output_root / variant if multi_variant else args.output_root
            print(f"- {variant_label}: {count} families in {variant_output_root}")


if __name__ == "__main__":
    main()
