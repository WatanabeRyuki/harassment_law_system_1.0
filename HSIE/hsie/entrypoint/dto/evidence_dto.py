"""Evidence DTO for HSIE EntryPoint layer.

This module defines the immutable Evidence snapshot that is saved by the
EntryPoint layer as the final output of HSIEController.

Design Philosophy:
    - Evidence is an immutable snapshot of what was known at a specific time.
    - Evidence must be explainable: each field must be traceable to its origin.
    - Evidence must withstand future court, third-party verification, and re-analysis.
    - EntryPoint results are irreversible: once saved, Evidence is never modified.

This DTO is internal to the EntryPoint layer. It may be read by analysis layers,
but MUST NOT be modified there.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from hsie.entrypoint.services.analysis_context_service import AnalysisContext
from hsie.entrypoint.services.asr_result_structurer import UtteranceUnit
from hsie.entrypoint.services.asr_service import ASRResult


class Evidence(BaseModel):
    """Immutable Evidence snapshot for HSIE EntryPoint layer.

    Evidence is the minimal and complete unit of preservation for the EntryPoint
    layer. It captures *exactly* what was known at the time of saving, without
    any analysis, judgment, interpretation, or structural optimization.

    Evidence = AnalysisContext + ASRResult + UtteranceUnits + metadata

    Attributes:
        evidence_id: Unique identifier for this evidence (UUID).
        context: AnalysisContext snapshot at the time of saving.
        asr_result: ASRResult snapshot at the time of saving.
        utterance_units: List of UtteranceUnit objects produced mechanically.
        saved_at: Timestamp when this evidence was saved.
        version: Storage format version string.
    """

    evidence_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for this evidence (UUID)",
    )
    context: AnalysisContext = Field(
        ...,
        description="AnalysisContext snapshot at the time of saving",
    )
    asr_result: ASRResult = Field(
        ...,
        description="ASRResult snapshot at the time of saving",
    )
    utterance_units: list[UtteranceUnit] = Field(
        ...,
        description="List of mechanically structured UtteranceUnit objects",
    )
    saved_at: datetime = Field(
        ...,
        description="Timestamp when this evidence was saved",
    )
    version: str = Field(
        ...,
        description="Storage format version string",
    )

    class Config:
        """Pydantic configuration."""

        frozen = True  # Make the Evidence immutable
        validate_assignment = True


