"""DEM and graph logic."""
from __future__ import annotations

import numpy as np
from scipy.sparse import csc_matrix

from qec_rd.adapters.stim import extract_stim_dem, sample_stim_detectors
from qec_rd.core import (
    CircuitArtifact,
    DecodingGraph,
    DemArtifact,
    SyndromeBatch,
    UnsupportedDemError,
)


def extract_dem(circuit_artifact: CircuitArtifact) -> DemArtifact:
    return extract_stim_dem(circuit_artifact)


def build_decoding_graph(dem_artifact: DemArtifact) -> DecodingGraph:
    dem = dem_artifact.raw_handle
    row_indices: list[int] = []
    col_indices: list[int] = []
    obs_pairs: list[tuple[int, int]] = []
    data: list[int] = []
    error_probabilities: list[float] = []
    edge_fault_ids: list[int] = []
    column = 0

    for instruction in dem.flattened():
        if instruction.type != "error":
            continue
        components: list[tuple[list[int], list[int]]] = [([], [])]
        for target in instruction.targets_copy():
            if target.is_relative_detector_id():
                components[-1][0].append(target.val)
            elif target.is_logical_observable_id():
                components[-1][1].append(target.val)
            elif target.is_separator():
                components.append(([], []))
        error_probability = float(instruction.args_copy()[0])
        for detectors, observables in components:
            if not detectors and not observables:
                continue
            if len(detectors) > 2:
                raise UnsupportedDemError(
                    "Stage 1 only supports graphlike DEM terms with up to two detectors."
                )
            for detector in detectors:
                row_indices.append(detector)
                col_indices.append(column)
                data.append(1)
            for observable in observables:
                obs_pairs.append((observable, column))
            error_probabilities.append(error_probability)
            edge_fault_ids.append(column)
            column += 1

    check_matrix = csc_matrix(
        (data, (row_indices, col_indices)),
        shape=(dem_artifact.num_detectors, column),
        dtype=np.uint8,
    )
    observable_matrix = np.zeros(
        (dem_artifact.num_observables, column), dtype=np.uint8
    )
    for observable, fault_id in obs_pairs:
        observable_matrix[observable, fault_id] = 1

    return DecodingGraph(
        num_detectors=dem_artifact.num_detectors,
        num_observables=dem_artifact.num_observables,
        check_matrix=check_matrix,
        observable_matrix=observable_matrix,
        error_probabilities=np.asarray(error_probabilities, dtype=float),
        edge_fault_ids=edge_fault_ids,
        raw_dem_handle=dem,
    )


def sample_syndromes(
    circuit_artifact: CircuitArtifact,
    *,
    shots: int,
    seed: int | None = None,
) -> SyndromeBatch:
    return sample_stim_detectors(circuit_artifact, shots=shots, seed=seed)
