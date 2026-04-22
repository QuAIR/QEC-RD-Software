"""Thin Stage 1 public API exposing pipeline and runner entry points."""
from qec_rd.core import CodeSpec, ExperimentConfig, ExperimentResult, NoiseModel
from qec_rd.kernel.analysis import analyze_results
from qec_rd.kernel.circuit import build_circuit, load_circuit
from qec_rd.kernel.decode import normalize_custom_decode_result, run_decoder
from qec_rd.kernel.graph import build_decoding_graph, extract_dem, sample_syndromes
from qec_rd.kernel.runner import benchmark, run_experiment, sweep

__all__ = [
    "analyze_results",
    "benchmark",
    "build_circuit",
    "build_decoding_graph",
    "extract_dem",
    "load_circuit",
    "normalize_custom_decode_result",
    "run_decoder",
    "run_experiment",
    "sample_syndromes",
    "sweep",
    "CodeSpec",
    "ExperimentConfig",
    "ExperimentResult",
    "NoiseModel",
]
