# (c) Copyright Riverlane 2020-2025.
"""Description of ``deltakit.core`` namespace here."""

import importlib.metadata

# It looks like these were intended to be separate, public modules.
# For now, import them as such. This can be reconsidered during API review.
from . import decoding_graphs

__version__ = importlib.metadata.version(__package__)

# Prevent import of `importlib` (and any other non-public objects) from this module.
del importlib

# List only public members in `__all__`.
__all__ = ["decoding_graphs"]
