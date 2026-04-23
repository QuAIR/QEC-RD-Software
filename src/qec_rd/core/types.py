from __future__ import annotations

from enum import Enum


class QecRdError(Exception):
    """Base exception for platform-level errors."""


class UnsupportedCircuitFormatError(QecRdError):
    """Raised when a circuit format is not supported."""


class UnsupportedDemError(QecRdError):
    """Raised when a DEM cannot be converted into the Stage 1 graph model."""


class DecoderConfigurationError(QecRdError):
    """Raised when decoder inputs or options are invalid."""


class CircuitSourceKind(str, Enum):
    GENERATED = "generated"
    STIM_OBJECT = "stim_object"
    STIM_FILE = "stim_file"
    QASM_FILE = "qasm_file"
