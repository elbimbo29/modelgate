"""Tests for HITL and judge models (Step 0.4)."""

import pytest
from pydantic import ValidationError

from modelgate.core.models import Variant
from modelgate.core.review_models import (
    CalibrationPoint,
    JudgeVerdict,
    ReviewItem,
    ReviewLabel,
)


def _item() -> ReviewItem:
    return ReviewItem(
        id="item-1",
        experiment_id="exp-1",
        unit_id="u_42",
        variant_a=Variant(id="A"),
        variant_b=Variant(id="B"),
        response_a="Sure, here's how.",
        response_b="Absolutely! Let me help.",
    )


def test_review_item_defaults_to_pending() -> None:
    item = _item()
    assert item.status == "pending"
    assert item.created_at.tzinfo is not None


def test_review_item_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        ReviewItem(
            id="item-1",
            experiment_id="exp-1",
            unit_id="u_42",
            variant_a=Variant(id="A"),
            variant_b=Variant(id="B"),
            response_a="x",
            response_b="y",
            status="ghost",  # type: ignore[arg-type]
        )


def test_review_label_constructs() -> None:
    label = ReviewLabel(item_id="item-1", labeler="alice", verdict="A")
    assert label.verdict == "A"
    assert label.notes == ""
    assert label.labeled_at.tzinfo is not None


def test_review_label_accepts_tie_and_unsure() -> None:
    for v in ("A", "B", "Tie", "Unsure"):
        ReviewLabel(item_id="item-1", labeler="alice", verdict=v)  # type: ignore[arg-type]


def test_review_label_rejects_unknown_verdict() -> None:
    with pytest.raises(ValidationError):
        ReviewLabel(item_id="item-1", labeler="alice", verdict="Maybe")  # type: ignore[arg-type]


def test_judge_verdict_defaults_parse_ok_true() -> None:
    v = JudgeVerdict(item_id="item-1", judge_model="gpt-4o", verdict="B")
    assert v.parse_ok is True
    assert v.rationale == ""
    assert v.raw == ""


def test_judge_verdict_can_mark_parse_failed() -> None:
    v = JudgeVerdict(
        item_id="item-1",
        judge_model="gpt-4o",
        verdict="Unsure",
        raw="I think maybe A? Hard to say.",
        parse_ok=False,
    )
    assert v.parse_ok is False
    assert "maybe A" in v.raw


def test_calibration_point_constructs() -> None:
    p = CalibrationPoint(n_human_labels=10, n_items=50, agreement=0.82, kappa=0.61)
    assert p.n_human_labels == 10
    assert p.n_items == 50
    assert p.agreement == pytest.approx(0.82)
    assert p.kappa == pytest.approx(0.61)


def test_calibration_point_rejects_out_of_range_agreement() -> None:
    with pytest.raises(ValidationError):
        CalibrationPoint(n_human_labels=10, n_items=50, agreement=1.5, kappa=0.0)


def test_calibration_point_rejects_out_of_range_kappa() -> None:
    with pytest.raises(ValidationError):
        CalibrationPoint(n_human_labels=10, n_items=50, agreement=0.5, kappa=2.0)


def test_calibration_point_allows_negative_kappa() -> None:
    # kappa in [-1, 1] — negative means "worse than chance", a real outcome.
    p = CalibrationPoint(n_human_labels=5, n_items=20, agreement=0.4, kappa=-0.1)
    assert p.kappa == pytest.approx(-0.1)