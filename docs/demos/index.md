# End-to-End Demos

These demos are arranged as a guided path for a reader who does not yet know
QEC terminology. The first four demos are progressive onboarding demos. They
teach the meaning of four keyword categories:

- `code`
- `noise`
- `decoder`
- `target`

The fifth demo is the heavier acceptance-oriented execution path.

Every runnable demo in this section still exercises the same Stage 1 platform
object flow:

`CodeSpec -> CircuitArtifact -> DemArtifact -> DecodingGraph -> SyndromeBatch -> DecodeResult -> AnalysisReport`

The onboarding demos are intentionally small so they can run locally during review.

## Recommended First Demo

For a first-contact walkthrough, read the demos in order:

1. [What counts as a code?](builtin-repetition-memory.md)
2. [What counts as a noise model?](rotated-surface-si1000.md)
3. [What counts as a decoder and a target?](custom-decoder-hook.md)
4. [How a full experiment description is assembled](sweep-analysis-report.md)
5. [Acceptance showcase](acceptance-showcase.md)

The final acceptance showcase is intentionally heavier and is documented
separately on its own page.

## Guided Demo Set

1. [Demo 1: What counts as a code here?](builtin-repetition-memory.md)
2. [Demo 2: What counts as a noise model here?](rotated-surface-si1000.md)
3. [Demo 3: What counts as a decoder and a target?](custom-decoder-hook.md)
4. [Demo 4: How a full experiment description is assembled](sweep-analysis-report.md)
5. [Demo 5: Acceptance showcase](acceptance-showcase.md)

## Supplementary Demo

- [Imported Stim circuit pipeline](imported-stim-circuit.md)

## Before You Run

Install the development environment from the repository root:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Then run the official default demo with:

```powershell
python -m qec_rd.demo
```
