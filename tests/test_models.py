"""Tests for the core domain models (Step 0.3)."""

import pytest
from pydantic import ValidationError

from modelgate.core.models import (
    Assignment,
    Experiment,
    Outcome,
    Variant,
)


def _variants() -> list[Variant]:
    return [
        Variant(id="A", weight=0.5, config={"provider": "openai", "model": "gpt-4o-mini"}),
        Variant(id="B", weight=0.5, config={"provider": "openai", "model": "gpt-4o"}),
    ]


def test_experiment_constructs() -> None:
    exp = Experiment(
        id="exp-1",
        name="gpt-mini vs gpt-4o",
        variants=_variants(),
        metric="helpfulness",
    )
    assert exp.id == "exp-1"
    assert len(exp.variants) == 2
    assert exp.metric == "helpfulness"
    assert exp.created_at.tzinfo is not None


def test_experiment_rejects_duplicate_variant_ids() -> None:
    dup = [
        Variant(id="A"),
        Variant(id="A"),
    ]
    with pytest.raises(ValidationError, match="unique"):
        Experiment(id="e", name="n", variants=dup, metric="helpfulness")


def test_experiment_rejects_single_variant() -> None:
    with pytest.raises(ValidationError):
        Experiment(
            id="e",
            name="n",
            variants=[Variant(id="A")],
            metric="helpfulness",
        )


def test_variant_rejects_nonpositive_weight() -> None:
    with pytest.raises(ValidationError):
        Variant(id="A", weight=0.0)
    with pytest.raises(ValidationError):
        Variant(id="A", weight=-1.0)


def test_variant_is_frozen() -> None:
    v = Variant(id="A")
    with pytest.raises(ValidationError):
        v.id = "B"  # type: ignore[misc]


def test_assignment_constructs() -> None:
    a = Assignment(experiment_id="exp-1", unit_id="u_42", variant_id="A")
    assert a.unit_id == "u_42"
    assert a.assigned_at.tzinfo is not None


def test_outcome_constructs_with_defaults() -> None:
    o = Outcome(
        experiment_id="exp-1",
        unit_id="u_42",
        variant_id="A",
        response="hello",
        latency_ms=120,
    )
    assert o.cost_usd == 0.0
    assert o.tokens_in == 0
    assert o.recorded_at.tzinfo is not None


def test_outcome_rejects_negative_latency() -> None:
    with pytest.raises(ValidationError):
        Outcome(
            experiment_id="e",
            unit_id="u",
            variant_id="A",
            response="x",
            latency_ms=-1,
        )


def test_metric_literal_rejects_unknown() -> None:
    with pytest.raises(ValidationError):
        Experiment(
            id="e",
            name="n",
            variants=_variants(),
            metric="vibes",  # type: ignore[arg-type]
        )