from importlib import import_module


def test_stage1_modules_are_importable():
    modules = [
        "qec_rd.api",
        "qec_rd.core",
        "qec_rd.core.experiments",
        "qec_rd.adapters.stim",
        "qec_rd.kernel.circuit",
        "qec_rd.kernel.graph",
        "qec_rd.kernel.decode",
        "qec_rd.kernel.runner",
        "qec_rd.kernel.analysis",
    ]
    for module_name in modules:
        import_module(module_name)
