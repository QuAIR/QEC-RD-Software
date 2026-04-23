"""Experiment runner orchestration logic."""
from __future__ import annotations

from dataclasses import replace

from qec_rd.core import CodeSpec, ExperimentConfig, ExperimentResult, noise_model_from_spec
from qec_rd.kernel.analysis import analyze_results
from qec_rd.kernel.circuit import build_circuit, load_circuit
from qec_rd.kernel.decode import run_decoder
from qec_rd.kernel.graph import build_decoding_graph, extract_dem, sample_syndromes


class ExperimentRunner:
    def prepare(self, config: ExperimentConfig):
        if config.circuit_spec:
            circuit = load_circuit(config.circuit_spec["source"], format=config.circuit_spec["format"])
        else:
            code_spec = config.code_spec if isinstance(config.code_spec, CodeSpec) else CodeSpec(**config.code_spec)
            noise_model = noise_model_from_spec(config.noise_spec)
            circuit = build_circuit(
                code_spec,
                noise_model,
            )
        graph = build_decoding_graph(extract_dem(circuit))
        return circuit, graph

    def run(self, config: ExperimentConfig) -> ExperimentResult:
        circuit, graph = self.prepare(config)
        batch = sample_syndromes(circuit, **config.sim_spec)
        decoder_spec = dict(config.decoder_spec)
        decoder_name = decoder_spec.pop("name")
        decode_result = run_decoder(graph, batch, decoder_name=decoder_name, **decoder_spec)
        analysis_report = analyze_results(decode_result)
        return self.collect_result(config, circuit, batch, decode_result, analysis_report)

    def collect_result(self, config, circuit, batch, decode_result, analysis_report) -> ExperimentResult:
        return ExperimentResult(
            config=config,
            circuit=circuit,
            syndrome_batch=batch,
            decode_result=decode_result,
            analysis_report=analysis_report,
        )


def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    return ExperimentRunner().run(config)


def benchmark(config: ExperimentConfig, repeats: int) -> list[ExperimentResult]:
    return [run_experiment(config) for _ in range(repeats)]


def sweep(config: ExperimentConfig, path: str, values: list[object]) -> list[ExperimentResult]:
    head, field_name = path.split(".", 1)
    results: list[ExperimentResult] = []
    for value in values:
        section = dict(getattr(config, head))
        section[field_name] = value
        mutated = replace(config, **{head: section})
        results.append(run_experiment(mutated))
    return results
