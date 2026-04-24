# Acceptance Showcase

This is the heavier Stage 1 acceptance-oriented demo for QEC-RD-Software.
It is designed to exercise more of the backbone than the quick default demo:

- built-in `rotated_surface_code`
- scheduled `si1000` noise
- `pymatching` MWPM decoding
- `ldpc` BP+OSD-0 decoding
- multiple code distances `d = 3, 5, 7, 9`
- threshold-style logical-error-rate sweep

## Why This Is Separate

The default evaluation demo stays fast:

```powershell
python -m qec_rd.demo
```

This acceptance showcase is intentionally heavier and is meant to generate review assets:

```powershell
python -m qec_rd.showcase
```

Or, after editable install:

```powershell
qec-rd-showcase
```

## What It Generates

By default the generator writes three files under `docs/demos/assets/`:

- `rotated_surface_si1000_threshold_showcase.csv`
- `rotated_surface_si1000_threshold_showcase.json`
- `rotated_surface_si1000_threshold_showcase.png`

The planned sweep is:

- distances: `3, 5, 7, 9`
- decoders: `pymatching`, `bposd`
- physical error rates: `0.25%`, `0.35%`, `0.42%`, `0.50%`, `0.60%`
- shots per point: `10000`

## Current Status

The generator script is implemented, but the final committed showcase assets are tracked separately because the full local run is slow.

Until the final PNG is committed, use this page as the canonical reproduction entry point for the acceptance showcase.
