![Monaspace Mix](./hero.png)

Create your own [Monaspace](https://github.com/githubnext/monaspace) font by mixing and matching styles from different Monaspace variants.

Build your mixed fonts [here](monaspace-mix.ztluwu.dev).

<details>
  <summary><bold>Font Mixer</bold></summary>

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
python generate_all_mixes.py --overwrite --zip-output
```

By default, this now generates both variants:

- NF mixes from `monaspace-nerdfonts-*.zip` (output names include `NF`)
- non-NF mixes from `monaspace-static-*.zip`

To generate only ZIP files and remove intermediate folders:

```bash
python generate_all_mixes.py --overwrite --zip-only
```

Generate only one variant:

```bash
python generate_all_mixes.py --variants nf --overwrite --zip-output
python generate_all_mixes.py --variants non-nf --overwrite --zip-output
```

Useful flags: `--include-self`, `--limit N`, `--output-root PATH`, `--zip-output`, `--zip-dir PATH`, `--zip-only`, `--variants`, `--nf-zip-url`, `--non-nf-zip-url`.

</details>

## License

SIL Open Font License 1.1. See [LICENSE](LICENSE).

## Credits

- [Inspired by @blaise-io's issue comment](https://github.com/githubnext/monaspace/issues/30#issuecomment-3109815272)
- [Monaspace Font by Github](https://github.com/githubnext/monaspace)

