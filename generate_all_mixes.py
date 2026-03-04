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
        if asset.get("name", "").lower().endswith(".zip") and pattern in asset.get("name", "").lower()
    ]
    if matching:
        return matching[0]

    zips = [asset for asset in assets if asset.get("name", "").lower().endswith(".zip")]
    if zips:
        return zips[0]

    raise ValueError("No .zip asset found in release")


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
        raise FileNotFoundError(f"Could not find NerdFonts directory in {extracted_root}")
    return sorted(candidates, key=lambda path: len(path.parts))[0]


def collect_family_dirs(nerdfonts_dir: Path) -> list[Path]:
    families = [
        path
        for path in sorted(nerdfonts_dir.iterdir())
        if path.is_dir() and path.name.startswith("Monaspace ")
    ]
    if not families:
        raise FileNotFoundError(f"No Monaspace family directories found in {nerdfonts_dir}")
    return families


def short_family_name(path: Path) -> str:
    return path.name.replace("Monaspace ", "").strip()


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
        "--zip-url",
        help="Optional direct ZIP URL. If set, skips release API asset discovery.",
    )
    parser.add_argument(
        "--asset-pattern",
        default="nerdfonts",
        help="Pattern to choose ZIP asset from latest release (default: nerdfonts).",
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
        "--include-self",
        action="store_true",
        help="Include combinations where regular and italic families are the same (disabled by default).",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing generated files.")
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional limit for number of combinations to generate (0 = no limit).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.zip_url:
        zip_url = args.zip_url
        zip_name = Path(args.zip_url.split("?")[0]).name or "monaspace-release.zip"
    else:
        owner, repo = parse_repo_from_releases_url(args.releases_url)
        release_data = fetch_latest_release(owner, repo)
        asset = choose_zip_asset(release_data, args.asset_pattern)
        zip_url = asset["browser_download_url"]
        zip_name = asset["name"]

    zip_path = args.download_dir / zip_name
    print(f"Downloading: {zip_url}")
    download_file(zip_url, zip_path)

    print(f"Extracting: {zip_path}")
    extracted_root = extract_zip(zip_path, args.extract_dir)

    nerdfonts_dir = find_nerdfonts_dir(extracted_root)
    family_dirs = collect_family_dirs(nerdfonts_dir)

    mixer_script = Path(__file__).with_name("mix_fonts.py")
    if not mixer_script.exists():
        raise FileNotFoundError(f"Could not find mixer script: {mixer_script}")

    combinations: list[tuple[Path, Path]] = []
    for regular_dir, italic_dir in product(family_dirs, family_dirs):
        if not args.include_self and regular_dir == italic_dir:
            continue
        combinations.append((regular_dir, italic_dir))

    if args.limit > 0:
        combinations = combinations[: args.limit]

    if not combinations:
        raise ValueError("No family combinations to process")

    args.output_root.mkdir(parents=True, exist_ok=True)

    total = len(combinations)
    for index, (regular_dir, italic_dir) in enumerate(combinations, start=1):
        regular_short = short_family_name(regular_dir)
        italic_short = short_family_name(italic_dir)
        family_name = f"Monaspace Mix {regular_short}-{italic_short} NF"
        combo_out_dir = args.output_root / f"{regular_short}-{italic_short}"

        print(f"[{index}/{total}] {regular_short} + {italic_short} -> {combo_out_dir}")
        run_mix(
            mixer_script=mixer_script,
            python_exec=sys.executable,
            regular_dir=regular_dir,
            italic_dir=italic_dir,
            family_name=family_name,
            output_dir=combo_out_dir,
            overwrite=args.overwrite,
        )

    print("Done. Generated combinations:")
    print(f"- {total} families in {args.output_root}")


if __name__ == "__main__":
    main()
