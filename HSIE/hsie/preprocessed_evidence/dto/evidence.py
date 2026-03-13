"""Evidence metadata DTO."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class EvidenceMetadataDTO:
    """Evidence metadata section."""

    evidence_id: UUID
    context_id: UUID
    version: str
