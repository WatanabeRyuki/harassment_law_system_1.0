"""Evidence Repository for HSIE EntryPoint layer.

This module provides persistence for Evidence DTOs using JSON format.
It handles only save and load operations without any judgment or transformation.

Design Philosophy:
    - Repository is responsible only for persistence (save/load).
    - No business logic, judgment, or data transformation.
    - Uses pydantic for serialization/deserialization.
    - Evidence is immutable, so save operations are write-only (no updates).
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from hsie.entrypoint.dto.evidence_dto import Evidence


class EvidenceRepository:
    """Repository for Evidence persistence using JSON format.

    This repository handles saving and loading Evidence DTOs to/from JSON files.
    All Evidence objects are immutable, so save operations are write-only.

    Storage location: data/evidence/{evidence_id}.json
    """

    def __init__(self, base_dir: Path | str = "data/evidence"):
        """Initialize the repository with a base directory.

        Args:
            base_dir: Base directory for storing evidence files.
                     Defaults to "data/evidence".
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, evidence: Evidence) -> None:
        """Save an Evidence DTO to a JSON file.

        Args:
            evidence: The Evidence object to save.

        Raises:
            IOError: If the file cannot be written.
            ValidationError: If the Evidence object is invalid (should not happen).
        """
        file_path = self._get_file_path(evidence.evidence_id)
        
        # Serialize using pydantic's model_dump_json
        json_content = evidence.model_dump_json(indent=2, exclude_none=False)
        
        # Write to file atomically
        file_path.write_text(json_content, encoding="utf-8")

    def load(self, evidence_id: UUID) -> Evidence:
        """Load an Evidence DTO from a JSON file.

        Args:
            evidence_id: The UUID of the evidence to load.

        Returns:
            The loaded Evidence object.

        Raises:
            FileNotFoundError: If the evidence file does not exist.
            ValidationError: If the JSON content cannot be deserialized to Evidence.
            IOError: If the file cannot be read.
        """
        file_path = self._get_file_path(evidence_id)
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"Evidence file not found: {file_path} (evidence_id: {evidence_id})"
            )
        
        # Read JSON content
        json_content = file_path.read_text(encoding="utf-8")
        
        # Deserialize using pydantic's model_validate_json
        return Evidence.model_validate_json(json_content)

    def exists(self, evidence_id: UUID) -> bool:
        """Check if an Evidence with the given ID exists.

        Args:
            evidence_id: The UUID of the evidence to check.

        Returns:
            True if the evidence file exists, False otherwise.
        """
        file_path = self._get_file_path(evidence_id)
        return file_path.exists()

    def _get_file_path(self, evidence_id: UUID) -> Path:
        """Get the file path for a given evidence_id.

        Args:
            evidence_id: The UUID of the evidence.

        Returns:
            Path to the JSON file for this evidence.
        """
        return self.base_dir / f"{evidence_id}.json"

