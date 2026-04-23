"""Experiment runner orchestration logic."""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from qec_rd.core import (
    CodeSpec,
    DecodeResult,
    ExperimentConfig,
    ExperimentResult,
    SyndromeBatch,
    noise_model_from_spec,
)
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

    def run_until_failures(
        self,
        config: ExperimentConfig,
        *,
        min_failures: int,
        max_shots: int,
        batch_size: int,
    ) -> ExperimentResult:
        if min_failures <= 0:
            raise ValueError("min_failures must be greater than zero.")
        if max_shots <= 0:
            raise ValueError("max_shots must be greater than zero.")
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero.")

        circuit, graph = self.prepare(config)
        decoder_spec = dict(config.decoder_spec)
        decoder_name = decoder_spec.pop("name")
        sim_spec = dict(config.sim_spec)
        sim_spec.pop("shots", None)
        base_seed = sim_spec.pop("seed", None)

        batches: list[SyndromeBatch] = []
        decode_results: list[DecodeResult] = []
        shot_count = 0
        failure_count = 0
        batch_index = 0

        while shot_count < max_shots and failure_count < min_failures:
            current_shots = min(batch_size, max_shots - shot_count)
            seed = None if base_seed is None else base_seed + batch_index
            batch = sample_syndromes(circuit, shots=current_shots, seed=seed, **sim_spec)
            decode_result = run_decoder(
                graph,
                batch,
                decoder_name=decoder_name,
                **decoder_spec,
            )
            batches.append(batch)
            decode_results.append(decode_result)
            shot_count += batch.shot_count
            failure_count += decode_result.failure_count
            batch_index += 1

        combined_batch = _combine_syndrome_batches(batches)
        combined_decode_result = _combine_decode_results(decoder_name, decode_results)
        analysis_report = analyze_results(combined_decode_result)
        analysis_report.metadata.update(
            {
                "batches": len(batches),
                "batch_size": batch_size,
                "min_failures": min_failures,
                "max_shots": max_shots,
                "stop_reason": (
                    "min_failures"
                    if analysis_report.failure_count >= min_failures
                    else "max_shots"
                ),
            }
        )
        return self.collect_result(
            config,
            circuit,
            combined_batch,
            combined_decode_result,
            analysis_report,
        )


def _combine_syndrome_batches(batches: list[SyndromeBatch]) -> SyndromeBatch:
    if not batches:
        raise ValueError("Cannot combine an empty list of syndrome batches.")

    observable_flips = (
        None
        if any(batch.observable_flips is None for batch in batches)
        else np.vstack([batch.observable_flips for batch in batches])
    )
    measurements = (
        None
        if any(batch.measurements is None for batch in batches)
        else np.vstack([batch.measurements for batch in batches])
    )
    return SyndromeBatch(
        detection_events=np.vstack([batch.detection_events for batch in batches]),
        observable_flips=observable_flips,
        measurements=measurements,
        shot_count=sum(batch.shot_count for batch in batches),
        seed=batches[0].seed,
        source=batches[0].source,
    )


def _combine_decode_results(
    decoder_name: str,
    results: list[DecodeResult],
) -> DecodeResult:
    if not results:
        raise ValueError("Cannot combine an empty list of decode results.")

    actual_observables = (
        None
        if any(result.actual_observables is None for result in results)
        else np.vstack([result.actual_observables for result in results])
    )
    corrections = (
        None
        if any(result.corrections is None for result in results)
        else np.vstack([result.corrections for result in results])
    )
    return DecodeResult(
        decoder_name=decoder_name,
        predicted_observables=np.vstack(
            [result.predicted_observables for result in results]
        ),
        actual_observables=actual_observables,
        corrections=corrections,
        failure_mask=np.concatenate([result.failure_mask for result in results]),
        metadata={
            "num_batches": len(results),
            "component_metadata": [result.metadata for result in results],
        },
    )


def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    return ExperimentRunner().run(config)


def run_until_failures(
    config: ExperimentConfig,
    *,
    min_failures: int,
    max_shots: int,
    batch_size: int,
) -> ExperimentResult:
    return ExperimentRunner().run_until_failures(
        config,
        min_failures=min_failures,
        max_shots=max_shots,
        batch_size=batch_size,
    )


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
