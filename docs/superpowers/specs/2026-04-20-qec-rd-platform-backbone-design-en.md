# QEC-RD Platform Backbone Design

Date: 2026-04-20

## 1. Background and Goals

The long-term goal of QEC-RD-Software is to become a full-stack R&D foundation for quantum error correction, spanning code and circuit construction, realistic noise modeling, high-performance simulation, DEM extraction, decoding analysis, and future FTQC estimation.

The current repository already contains a minimal Phase 0 loop built on top of `stim`, but it is still far from a unified platform backbone with a reusable local scientific kernel. The purpose of this design is not to implement the full platform immediately, but to define a stable, extensible, and incrementally realizable backbone for the next stage.

This design focuses on the first-stage goals:

- Establish a platform-owned unified object model and end-to-end workflow in `qec_rd`.
- Use `stim` as the only execution backend in the first stage.
- Rebuild and absorb the core local scientific capabilities of DeltaKit inside `qec_rd`.
- Support two first-class entry modes: built-in circuit-catalog generation and external circuit import.
- Include repetition code, rotated surface code, unrotated surface code, and toric code as built-in circuit-catalog entries.
- Treat the code module as a built-in circuit database/selector: users choose built-in keys and parameters to generate circuits, while custom research inputs enter through circuit import.
- Expose both the direct pipeline API and a DeltaKit-style runner API in Stage 1.
- Include both MWPM and BP+OSD in the implementation and acceptance targets, while relying on standard external decoder packages instead of re-implementing decoder algorithms in-repo.
- Allow user-supplied custom decoders to plug into the same end-to-end platform chain instead of living as isolated offline utilities.

## 2. First-Stage Scope Boundary

### 2.1 In Scope for the First Stage

- Circuit generation, import, execution, and sampling based on `stim`
- A unified core object chain:
  `CodeSpec -> CircuitArtifact -> DemArtifact -> DecodingGraph -> SyndromeBatch -> DecodeResult -> AnalysisReport`
- Built-in support for repetition code, rotated surface code, unrotated surface code, and toric code as generated circuit entries
- A user-facing interaction model centered on generated or imported circuits, not arbitrary user-defined code definitions
- A `NoiseModel` limited to Pauli-compatible noise that can actually run in `stim`
- DEM extraction from circuits and construction of a standard decoding graph
- At least one MWPM decoding path
- At least one BP+OSD decoding path
- Support custom decoder integration into the standard `run_decoder(...) -> DecodeResult -> AnalysisReport` chain
- Basic logical error rate computation, batch statistics, and core experiment analysis
- An import-oriented workflow for future research on new circuits, schedules, and hardware-oriented circuit variants
- A high-level orchestration layer based on `ExperimentConfig`, `ExperimentRunner`, and `ExperimentResult`

### 2.2 Explicitly Out of Scope for the First Stage

- A multi-provider architecture
- Treating DeltaKit or TensorQEC as runtime providers in the platform backbone
- Cloud APIs, authentication, and remote experiment execution
- Notebook workflows as part of the product surface
- Full hardware control, compilation, deployment, or experiment orchestration
- Implementation-level TensorQEC integration
- Non-Pauli noise models
- Full replication of DeltaKit Explorer’s visualization and advanced peripheral analysis ecosystem
- In-house implementations of MWPM, BP+OSD, or other decoder algorithms

## 3. Overall Architecture

The first stage adopts a "platform backbone + Stim-only backend" structure. No multi-backend abstraction is introduced at this stage. DeltaKit and TensorQEC are treated as design references, not as runtime implementation components.

### 3.1 Layered Structure

- `qec_rd.core`
  Platform-level core objects, types, exceptions, and result models
- `qec_rd.kernel.runner`
  Experiment orchestration kernel
- `qec_rd.kernel.circuit`
  Circuit and built-in circuit-catalog kernel
- `qec_rd.kernel.graph`
  DEM and decoding-graph kernel
- `qec_rd.kernel.decode`
  Decoding workflow kernel
- `qec_rd.kernel.analysis`
  Analysis kernel
- `qec_rd.adapters.stim`
  Low-level bridge and format adapter to `stim`
- `qec_rd.api`
  Thin public API layer

### 3.2 Dependency Direction

- `qec_rd.api` may depend on `qec_rd.kernel.*` and `qec_rd.core`
- `qec_rd.kernel.*` may depend on `qec_rd.core` and `qec_rd.adapters.stim`
- `qec_rd.adapters.stim` may depend on `qec_rd.core`
- `qec_rd.core` must not depend on other business packages

### 3.3 Architectural Constraints

- Every executable loop in the first stage must rely only on `stim` as the low-level execution capability.
- The Stage 1 public API should expose both a composable pipeline surface and a higher-level runner surface.
- The public inputs and outputs of `kernel.graph`, `kernel.decode`, and `kernel.analysis` must not expose raw `stim.Circuit` or raw `stim.DetectorErrorModel` as the platform language.
- DeltaKit is the capability benchmark, not the runtime dependency that defines the platform backbone.
- Extensibility points must be defined in terms of platform-standard objects, not by bypassing the backbone and passing arbitrary backend-native objects through the system.
- DEM extraction and graph construction must remain fixed, platform-owned behavior in Stage 1 and should not be exposed as user-customizable strategy points.

## 4. Package Structure and Responsibilities

### 4.1 `qec_rd.core`

This package carries the platform’s unified semantics and should contain at least:

- `codes.py`
  Defines `CodeSpec`
- `experiments.py`
  Defines `ExperimentConfig` and `ExperimentResult`
- `artifacts.py`
  Defines `CircuitArtifact`, `DemArtifact`, and `DecodingGraph`
- `noise.py`
  Defines `NoiseModel`
- `results.py`
  Defines `SyndromeBatch`, `DecodeResult`, and `AnalysisReport`
- `types.py`
  Defines shared types, protocols, and base exceptions

### 4.2 `qec_rd.adapters.stim`

This package is responsible only for bridging to `stim`, not for platform-level analysis logic:

- Build or load `stim.Circuit`
- Extract DEM from a Stim circuit
- Execute detector and measurement sampling
- Convert between Stim-native objects and platform-standard objects

### 4.3 `qec_rd.kernel.circuit`

Responsible for the circuit and built-in circuit-catalog kernel:

- Generate built-in catalog circuits from `CodeSpec`
- Generate circuits from structured built-in definitions of repetition code, rotated surface code, unrotated surface code, and toric code
- Import and wrap external circuits
- Perform basic circuit validation
- Organize annotations, coordinates, logical observables, and detector metadata
- Orchestrate noise injection

### 4.3A `qec_rd.kernel.runner`

Responsible for the experiment orchestration shell:

- Prepare a complete run from `ExperimentConfig`
- Invoke the same circuit-to-analysis backbone used by the direct pipeline API
- Aggregate circuit, sampling, decoding, and analysis outputs into `ExperimentResult`
- Support single runs, benchmark-style execution, and sweep-style execution

### 4.4 `qec_rd.kernel.graph`

Responsible for transforming circuits or DEMs into a standard decoding structure:

- DEM parsing
- Extraction of detector, observable, boundary, and annotation semantics
- Standard decoding graph construction
- Graph processing such as edge weights, coordinates, and windowing

### 4.5 `qec_rd.kernel.decode`

Responsible for the decoder invocation workflow, but not for implementing decoder algorithms:

- Standardize decoder inputs
- Integrate external decoders
- Integrate user-defined custom decoders
- Normalize decoder outputs
- Standardize decoder failures, parameters, and exceptions

### 4.6 `qec_rd.kernel.analysis`

Responsible for the core research analysis layer:

- Logical error rate computation
- Batch statistics
- Aggregation over parameter sweeps
- Basic error distribution analysis and an error-budget skeleton

### 4.7 `qec_rd.api`

Must remain thin and stable, exposing both direct pipeline entry points and runner-style entry points:

- `run_experiment(...)`
- `benchmark(...)`
- `sweep(...)`
- `build_circuit(...)`
- `load_circuit(...)`
- `extract_dem(...)`
- `build_decoding_graph(...)`
- `sample_syndromes(...)`
- `run_decoder(...)`
- `analyze_results(...)`

## 5. Core Object Definition Principles

### 5.1 Experiment-Intent Objects

- `ExperimentConfig`
  Aggregates the user-facing experiment definition, including generated/imported circuit input, noise, decoder, sampling, and analysis specifications.
- `CodeSpec`
  Describes built-in circuit selection and generation parameters such as built-in family key, distance, rounds, logical basis, schedule variant, layout, and related metadata.
- `NoiseModel`
  Describes Stim-executable Pauli-like noise, basic phenomenological noise, and basic physical noise parameters.

These objects describe what experiment should be run. They do not carry runtime results.

### 5.2 Execution-Artifact Objects

- `CircuitArtifact`
  Represents the unified circuit artifact and serves as the standard circuit entry point for the downstream workflow.
- `DemArtifact`
  Represents the unified DEM artifact and its interpreted metadata.
- `DecodingGraph`
  Represents the standard decoding graph, while reserving room for richer graph or hypergraph structures in the future.

### 5.3 Runtime-Data Objects

- `SyndromeBatch`
  Holds batch runtime data such as dets, meas, and obs, together with shots, seed, sampling source, and configuration.

### 5.4 Result Objects

- `DecodeResult`
  Records predicted logical flips, failure statistics, decoder information, and decoder configuration.
- `AnalysisReport`
  Records logical error rate, parameter sweeps, confidence statistics, and core analysis conclusions.
- `ExperimentResult`
  Aggregates `ExperimentConfig`, the produced circuit-level artifacts, runtime data, decode outputs, and analysis outputs into a single user-facing experiment result object.

### 5.5 Object Constraints

- Core objects must be exportable as structured data, at least at a dict/JSON-friendly level.
- Core objects may internally cache Stim-native objects, but those native objects must not become the public language of the backbone.
- The system must strictly distinguish between intent, artifact, runtime data, and result.
- Object semantics should remain stable after construction, with a preference for immutable or semi-immutable designs.
- Every key object must carry minimal necessary provenance metadata.

## 6. Dual-Entry Requirement for `CircuitArtifact`

`CircuitArtifact` must not serve only built-in circuit-catalog generation. It must also serve as the unified platform circuit entry point for external circuit import.

### 6.1 Generated Entry

- `build_circuit(CodeSpec, NoiseModel | None) -> CircuitArtifact`

### 6.2 Imported Entry

- `load_circuit(source, format, metadata=...) -> CircuitArtifact`

The first stage must support at least:

- `stim.Circuit`
- `.stim` files

The design must also reserve room for future import of:

- Circuit text
- `.qasm` files
- OpenQASM 2 / OpenQASM 3 and related formats

### 6.3 Minimum Recommended Metadata for `CircuitArtifact`

- `source_kind`
  Such as `generated`, `stim_object`, `stim_file`, `qasm_file`
- `source_format`
  Such as `stim`, `openqasm2`, `openqasm3`
- `origin_metadata`
  Original file, generator, version, import parameters, and related provenance
- `code_spec`
  Optional field; not every circuit must be traceable to a complete `CodeSpec`
- `raw_handle`
  Optional cache of the backend object, such as `stim.Circuit`

## 7. End-to-End First-Stage Data Flow

### 7.0 Two Public API Layers

Stage 1 should expose two compatible public surfaces:

- Direct pipeline API
  For advanced users who want explicit control over each artifact transition.
- Runner API
  For users who want a DeltaKit-like workflow centered on `ExperimentConfig -> ExperimentRunner -> ExperimentResult`.

### 7.1 Two Entry Modes

- Generated entry:
  `CodeSpec (+ NoiseModel) -> build_circuit(...) -> CircuitArtifact`
- Imported entry:
  `stim.Circuit / .stim / future qasm -> load_circuit(...) -> CircuitArtifact`

### 7.2 Unified Main Chain

Once a circuit enters the system as a `CircuitArtifact`, the downstream flow is unified:

- `extract_dem(CircuitArtifact) -> DemArtifact`
- `build_decoding_graph(DemArtifact) -> DecodingGraph`
- `sample_syndromes(CircuitArtifact, ...) -> SyndromeBatch`
- `run_decoder(DecodingGraph, SyndromeBatch, ...) -> DecodeResult`
- `analyze_results(...) -> AnalysisReport`

### 7.2A Runner-Orchestrated Flow

The higher-level runner path should wrap the same main chain:

- `ExperimentConfig -> ExperimentRunner.prepare(...)`
- `ExperimentRunner.run(...)`
- internal execution through the standard circuit-to-analysis pipeline
- `ExperimentRunner.collect_result(...) -> ExperimentResult`

### 7.3 Responsibility of Each Stage

- Circuit entry stage:
  Unifies generated and imported circuit sources
- DEM extraction stage:
  Converts a circuit into a standard error-model artifact
- Decoding-graph stage:
  Converts the DEM into a unified decoding structure
- Sampling stage:
  Standardizes Stim runtime data into `SyndromeBatch`
- Decoding stage:
  Combines decoding structures and runtime data into a standard decode result
- Analysis stage:
  Converts decode results into research-interpretable metrics

## 8. Decoder Strategy

The first stage must include both MWPM and BP+OSD decoding paths, but must not implement those algorithms in-repo.

### 8.1 External Package Constraint

- MWPM uses the standard external package `pymatching`
- BP+OSD should primarily rely on the standard external ecosystem `ldpc` / `bposd`

In the first stage, the responsibility of `qec_rd` is to:

- Organize a unified decoding input
- Convert `DecodingGraph` and `SyndromeBatch` into the forms required by external packages
- Normalize outputs into `DecodeResult`
- Handle parameters, exceptions, and result aggregation
- Provide the same standard input/output contract for user-defined custom decoders

In the first stage, `qec_rd` does not take responsibility for:

- Implementing the MWPM algorithm
- Implementing the BP+OSD algorithm
- Copying external decoder source code into the repository backbone

### 8.2 Decoder Interface Principles

- MWPM and BP+OSD should be exposed through a unified high-level decoder entry
- Both decoder families should emit the same `DecodeResult` type
- Both decoder families should participate in the same downstream analysis workflow
- Custom decoders should also plug into the same high-level entry; their inputs should be based at minimum on `DecodingGraph` and `SyndromeBatch`, and their outputs must normalize into `DecodeResult`

## 8A. Customization Points

Even though the first stage does not introduce a multi-backend/provider architecture, it should still expose several platform-internal customization points to support research exploration.

### 8A.1 Required customization points

- Circuit entry
  The platform must support both generated circuits and imported external circuits.
- Decoder entry
  The platform must support both standard external-package decoders and user-defined custom decoders.

### 8A.2 Recommended customization points

- `CodeSpec` extension
  Future built-in circuit families, schedule parameters, and experiment metadata should be addable without breaking the backbone; Stage 1 should at minimum cover repetition, rotated surface, unrotated surface, and toric entries.
- `NoiseModel` extension
  Future Stim-supported Pauli-like and hardware-calibrated parameters should fit the same model family, but Stage 1 should not include non-Pauli noise.
- Runtime data entry
  Although Stage 1 is centered on Stim sampling, `SyndromeBatch` should be able to admit future external experiment data or hardware-returned data.
- Analysis layer
  Future threshold sweeps, error budgets, and resource-estimation logic should be able to build on `AnalysisReport` without changing the earlier object chain.

### 8A.3 Areas that should not be opened as customization points in Stage 1

- Execution backend
  Stage 1 remains fixed to `stim`.
- DEM extraction and graph-construction strategy
  Stage 1 keeps this as fixed platform-owned logic, not as a user-defined extension point.
- General provider/plugin systems
  Stage 1 should not introduce a generic plugin mechanism; it should keep only clear and lightweight extension boundaries.

## 9. First-Stage Implementation Waves

### Wave 0: Stabilize Backbone Objects and Directory Layout

- Establish the base object skeleton in `qec_rd.core`
- Establish the directory structure for `kernel.*`, `adapters.stim`, and `api`
- Fix dependency direction and exception structure

### Wave 1: Open the Stim Circuit Entry Path

- Implement `build_circuit(...)`
- Implement `load_circuit(...)`
- Support `stim.Circuit`
- Support `.stim` files
- Support at least one base built-in circuit entry with a memory experiment

### Wave 2: Open the DEM and Decoding-Graph Main Chain

- Produce `DemArtifact`
- Build a standard `DecodingGraph`
- Fix the error semantics for graph-construction failures

### Wave 3: Sampling and MWPM Closed Loop

- Implement `SyndromeBatch`
- Integrate `pymatching`
- Produce a standard `DecodeResult`
- Form the first complete executable closed loop

### Wave 4: BP+OSD Decoder Integration

- Integrate the `ldpc` / `bposd` ecosystem
- Complete the unified decoder adaptation path
- Ensure BP+OSD shares the same object chain as MWPM

### Wave 5: Batch Analysis and Stabilization

- Batch sweeps and aggregation
- Stabilize `AnalysisReport`
- Add object export capability
- Add tests for generated and imported closed loops
- Add acceptance tests for both MWPM and BP+OSD paths

## 10. First-Stage Acceptance Criteria

### 10.1 Object-Chain Acceptance

- Both generated and imported entry modes must flow through the same standard object chain:
  `CircuitArtifact -> DemArtifact -> DecodingGraph -> SyndromeBatch -> DecodeResult -> AnalysisReport`

### 10.2 Stim-Only Backend Acceptance

- Every executable loop in the first stage must rely only on `stim` as the execution backend
- The runtime backbone must not depend on DeltaKit as the implementation carrier

### 10.3 DeltaKit Local Scientific Backbone Benchmark Acceptance

The first stage must at least align with the following categories of local scientific capability:

- Circuit generation and import
- Built-in repetition, rotated surface, unrotated surface, and toric circuit generation
- Imported external circuits as the customization path for user-designed code circuits
- Stim-driven sampling
- DEM and graph construction
- Basic local decoding
- Basic result analysis

### 10.4 External-Circuit Research Entry Acceptance

- The platform must accept external Stim circuits as first-class inputs
- The platform must not require every circuit to originate from built-in `CodeSpec`

### 10.5 MWPM Acceptance

- The platform must be able to perform MWPM decoding through the external `pymatching` package
- The platform must normalize the output into `DecodeResult`

### 10.6 BP+OSD Acceptance

- The platform must be able to perform BP+OSD decoding through the external `ldpc` / `bposd` ecosystem
- The platform must normalize the output into `DecodeResult`

### 10.7 Decoder-Adapter Acceptance

- `qec_rd` must not copy MWPM or BP+OSD algorithm implementations into the backbone
- Decoders must be used as adapted external packages, not as reimplemented internal algorithms

### 10.7A Custom Decoder Acceptance

- The platform must allow a user-defined custom decoder to join the standard high-level decoding entry
- The input contract of a custom decoder must be based at minimum on `DecodingGraph` and `SyndromeBatch`
- The output of a custom decoder must normalize into `DecodeResult`
- The result of a custom decoder must continue into `AnalysisReport` generation without a separate side workflow

### 10.8 Thin-API Acceptance

- A user should be able to complete a basic local QEC research experiment through either the direct pipeline API or the runner API exposed in `qec_rd.api`
- A user should not need to manipulate Stim-native objects directly

### 10.9 Runner-API Acceptance

- Stage 1 must provide `ExperimentConfig`, `ExperimentRunner`, and `ExperimentResult`
- Stage 1 must expose `run_experiment(...)`, `benchmark(...)`, and `sweep(...)` in `qec_rd.api`
- The runner path must internally reuse the same backbone artifacts and pipeline semantics as the direct pipeline API

## 11. Platform State After First-Stage Completion

If the first stage described here is implemented successfully, the platform should reach the following state:

- It is no longer just a Stim demo
- It has its own `qec_rd`-owned unified core object system
- It can already carry the essential local scientific backbone of DeltaKit
- It supports both built-in catalog-driven circuits and imported external Stim circuits
- It supports both a direct pipeline API and a DeltaKit-style runner API
- It supports two common local decoding paths: MWPM and BP+OSD
- It leaves behind a stable backbone for later expansion into more built-in circuit families, richer noise models, TensorQEC-related capabilities, and engineering-oriented features
