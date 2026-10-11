"""Core domain models for ModelGate.

These four models are the vocabulary of the whole system:

    Experiment  — the declaration: "compare these variants on this metric"
    Variant     — one arm of the experiment (a model, prompt, or config blob)
    Assignment  — the routing record: "unit X got variant Y, deterministically"
    Outcome     — the result: "here is what variant Y produced for unit X"

Nothing in this module talks to the database, the network, or the API.
Pure shape, no behavior.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _utcnow() -> datetime:
    return datetime.now(UTC)


# --------------------------------------------------------------------------
# Variant
# --------------------------------------------------------------------------

class Variant(BaseModel):
    """One arm of an experiment.

    A variant is anything that produces a response: a model, a prompt,
    a model+prompt combo, a temperature setting, etc. The `config` dict
    is intentionally free-form — provider adapters validate their own
    config in Phase 5.
    """

    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1, max_length=64)
    weight: float = Field(default=1.0, gt=0.0)
    config: dict[str, Any] = Field(default_factory=dict)


# --------------------------------------------------------------------------
# Experiment
# --------------------------------------------------------------------------

MetricName = Literal["helpfulness", "correctness", "tone", "safety"]


class Experiment(BaseModel):
    """The declaration of what we're testing.

    Variants must have unique ids. Weights are relative — the assignment
    function normalizes them, so {A: 1, B: 1} and {A: 0.5, B: 0.5} are
    equivalent.
    """

    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    variants: list[Variant] = Field(min_length=2)
    metric: MetricName
    created_at: datetime = Field(default_factory=_utcnow)

    @field_validator("variants")
    @classmethod
    def _unique_variant_ids(cls, variants: list[Variant]) -> list[Variant]:
        ids = [v.id for v in variants]
        if len(ids) != len(set(ids)):
            raise ValueError("variant ids must be unique within an experiment")
        return variants


# --------------------------------------------------------------------------
# Assignment
# --------------------------------------------------------------------------

class Assignment(BaseModel):
    """The routing decision for one unit of traffic.

    `unit_id` is whatever you split on — user id, session id, request id.
    The same (experiment_id, unit_id) always yields the same variant_id,
    by construction. This model just records that fact.
    """

    model_config = ConfigDict(frozen=True)

    experiment_id: str
    unit_id: str
    variant_id: str
    assigned_at: datetime = Field(default_factory=_utcnow)


# --------------------------------------------------------------------------
# Outcome
# --------------------------------------------------------------------------

class Outcome(BaseModel):
    """What a variant produced for one unit.

    This is the raw material the decision engine reads in Phase 3 and
    the judge grades in Phase 5. `response` is the actual text; the
    numeric fields are recorded so cost/latency can inform decisions.
    """

    model_config = ConfigDict(frozen=True)

    experiment_id: str
    unit_id: str
    variant_id: str
    response: str
    latency_ms: int = Field(ge=0)
    cost_usd: float = Field(default=0.0, ge=0.0)
    tokens_in: int = Field(default=0, ge=0)
    tokens_out: int = Field(default=0, ge=0)
    recorded_at: datetime = Field(default_factory=_utcnow)