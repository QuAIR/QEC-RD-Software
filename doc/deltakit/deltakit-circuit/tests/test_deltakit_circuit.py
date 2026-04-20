# (c) Copyright Riverlane 2020-2025.
import importlib


def test_package_version_is_expected_version():
    # To ensure no false positives test this in tox rather than Poetry.
    assert importlib.metadata.version("deltakit_circuit")
