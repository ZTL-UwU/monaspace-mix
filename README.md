# Monaspace Font Mixer

Mix one family for upright styles and another for italic styles.

## Install

```bash
python -m pip install fonttools
```

## Quick start (2 files)

```bash
python mix_fonts.py \
  --regular /path/to/MonaspaceArgon-Regular.otf \
  --italic /path/to/MonaspaceRadon-Regular.otf \
  --name "Monaspace Frankenstein" \
  --output-dir ./out
```

Output:

- `out/MonaspaceFrankenstein-Regular.otf`
- `out/MonaspaceFrankenstein-Italic.otf`

## Folder mode (all styles)

```bash
python mix_fonts.py \
  --regular-dir "/path/to/NerdFonts/Monaspace Argon" \
  --italic-dir "/path/to/NerdFonts/Monaspace Radon" \
  --name "Monaspace Mix NF" \
  --output-dir ./out-all \
  --overwrite
```

- Upright styles come from `--regular-dir`.
- Italic styles come from `--italic-dir`.
- Missing styles are skipped (use `--strict` to fail).

## Generate every combination

```bash
python generate_all_mixes.py --overwrite
```

Useful flags: `--include-self`, `--limit N`, `--output-root PATH`, `--zip-url URL`.

## License

SIL Open Font License 1.1. See [LICENSE](LICENSE).

## Credits

- [Inspired by @blaise-io's issue comment](https://github.com/githubnext/monaspace/issues/30#issuecomment-3109815272)
- [Monaspace Font by Github](https://github.com/githubnext/monaspace)

