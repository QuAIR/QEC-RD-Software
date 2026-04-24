from qec_rd.showcase import (
    ACCEPTANCE_DECODERS,
    ACCEPTANCE_DISTANCES,
    ACCEPTANCE_ERROR_RATES,
    build_acceptance_showcase_plan,
)


def test_acceptance_showcase_plan_covers_all_distances_decoders_and_error_rates() -> None:
    plan = build_acceptance_showcase_plan()

    assert len(plan) == (
        len(ACCEPTANCE_DISTANCES)
        * len(ACCEPTANCE_DECODERS)
        * len(ACCEPTANCE_ERROR_RATES)
    )
    assert {job["distance"] for job in plan} == set(ACCEPTANCE_DISTANCES)
    assert {job["decoder_name"] for job in plan} == set(ACCEPTANCE_DECODERS)
    assert {job["physical_error_rate"] for job in plan} == set(ACCEPTANCE_ERROR_RATES)


def test_acceptance_showcase_plan_uses_requested_shot_budget() -> None:
    plan = build_acceptance_showcase_plan(shots=10_000)

    assert all(job["config"].sim_spec["shots"] == 10_000 for job in plan)
