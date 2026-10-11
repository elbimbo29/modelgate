"""HITL and judge domain models.

These sit one layer above the core experiment models:

    ReviewItem       — a pair of responses waiting for a human to label
    ReviewLabel      — a human's verdict on a ReviewItem
    JudgeVerdict     — an LLM judge's verdict on the same item
    CalibrationPoint — agreement at a given number of human labels

The vocabulary "A / B / Tie / Unsure" is shared between humans and the
judge on purpose. Calibration compares them on equal footing.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from modelgate.core.models import Variant


def _utcnow() -> datetime:
    return datetime.now(UTC)


# Shared verdict vocabulary. Humans and judges speak the same words.
Verdict = Literal["A", "B", "Tie", "Unsure"]


# --------------------------------------------------------------------------
# ReviewItem
# --------------------------------------------------------------------------

ReviewStatus = Literal["pending", "labeled", "resolved"]


class ReviewItem(BaseModel):
    """One ambiguous comparison waiting for a human.

    Created by the decision engine (Phase 3) when stats are inconclusive.
    Stores both variant responses inline so the UI needs one read, not three.
    """

    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1, max_length=64)
    experiment_id: str
    unit_id: str
    variant_a: Variant
    variant_b: Variant
    response_a: str
    response_b: str
    status: ReviewStatus = "pending"
    created_at: datetime = Field(default_factory=_utcnow)


# --------------------------------------------------------------------------
# ReviewLabel
# --------------------------------------------------------------------------

class ReviewLabel(BaseModel):
    """A human's verdict on a ReviewItem.

    Re-labeling is allowed and creates a new ReviewLabel rather than
    mutating the old one — the audit trail is the sequence of labels,
    not the latest one. The Phase 4 repo will store them append-only.
    """

    model_config = ConfigDict(frozen=True)

    item_id: str
    labeler: str = Field(min_length=1, max_length=128)
    verdict: Verdict
    notes: str = Field(default="", max_length=2000)
    labeled_at: datetime = Field(default_factory=_utcnow)


# --------------------------------------------------------------------------
# JudgeVerdict
# --------------------------------------------------------------------------

class JudgeVerdict(BaseModel):
    """An LLM judge's verdict on a ReviewItem.

    `raw` is the judge's unparsed output — useful when the structured
    parse fails or the judge hedges. `parse_ok` records whether the
    structured fields are trustworthy.
    """

    model_config = ConfigDict(frozen=True)

    item_id: str
    judge_model: str = Field(min_length=1, max_length=128)
    verdict: Verdict
    rationale: str = Field(default="", max_length=4000)
    raw: str = Field(default="")
    parse_ok: bool = True
    judged_at: datetime = Field(default_factory=_utcnow)


# --------------------------------------------------------------------------
# CalibrationPoint
# --------------------------------------------------------------------------

class CalibrationPoint(BaseModel):
    """One point on the calibration curve.

    Holds the result of comparing judge verdicts to human labels after
    the judge has been calibrated on `n_human_labels` examples.

    `agreement` is raw agreement rate in [0, 1].
    `kappa` is Cohen's kappa in [-1, 1], the chance-corrected version.
    `n_items` is how many items the comparison ran over — always larger
    than `n_human_labels`, since we reserve items for the test set.
    """

    model_config = ConfigDict(frozen=True)

    n_human_labels: int = Field(ge=0)
    n_items: int = Field(ge=1)
    agreement: float = Field(ge=0.0, le=1.0)
    kappa: float = Field(ge=-1.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)