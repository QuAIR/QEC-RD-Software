# End-to-End Demos

These demos are acceptance-oriented examples for the Stage 1 QEC-RD backbone.
Each demo exercises the same platform object flow:

`CodeSpec -> CircuitArtifact -> DemArtifact -> DecodingGraph -> SyndromeBatch -> DecodeResult -> AnalysisReport`

The demos are intentionally small so they can run locally during review.

## Demo Set

1. [Built-in repetition memory experiment](builtin-repetition-memory.md)
2. [Rotated surface memory with scheduled SI1000-style noise](rotated-surface-si1000.md)
3. [Imported Stim circuit pipeline](imported-stim-circuit.md)
4. [Custom decoder hook](custom-decoder-hook.md)
5. [Parameter sweep and analysis report](sweep-analysis-report.md)

## Before You Run

Install the development environment from the repository root:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Then run any demo snippet with:

```powershell
python demo.py
```
