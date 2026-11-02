"""MindScope Causal Inference Package.

Heavy dependencies (DoWhy, EconML, sympy) are loaded lazily
to avoid gmpy2 / sympy DLL crashes on Python 3.13 Windows
during pytest collection.
"""
from .whatif import simulate_what_if_intervention, CAUSAL_COEFFICIENTS


def __getattr__(name):
    """Lazy-load DoWhy-dependent modules on first access."""
    _graph_attrs = {"get_causal_dag_dot", "get_causal_dag_gml"}
    _estimator_attrs = {
        "run_single_causal_pipeline",
        "evaluate_all_causal_benchmarks",
        "CAUSAL_TOLERANCES",
        "BACKDOOR_CONFOUNDERS",
    }
    _subgroup_attrs = {"analyze_subgroup_causal_effects"}

    if name in _graph_attrs:
        from . import graph
        return getattr(graph, name)
    if name in _estimator_attrs:
        from . import estimator
        return getattr(estimator, name)
    if name in _subgroup_attrs:
        from . import subgroups
        return getattr(subgroups, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "get_causal_dag_dot",
    "get_causal_dag_gml",
    "run_single_causal_pipeline",
    "evaluate_all_causal_benchmarks",
    "CAUSAL_TOLERANCES",
    "BACKDOOR_CONFOUNDERS",
    "analyze_subgroup_causal_effects",
    "simulate_what_if_intervention",
    "CAUSAL_COEFFICIENTS",
]
