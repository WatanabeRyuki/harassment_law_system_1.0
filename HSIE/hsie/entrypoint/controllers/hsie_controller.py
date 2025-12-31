"""HSIE Controller for EntryPoint layer.

This module provides the final orchestrator that processes audio files
and saves Evidence objects without any judgment or interpretation.

Design Philosophy:
    - HSIEController is a pure orchestrator that executes services in sequence
    - No business logic, judgment, or interpretation is performed
    - All exceptions are propagated to the caller
    - Services are injected via constructor for testability
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from hsie.entrypoint.dto.evidence_dto import Evidence
from hsie.entrypoint.repository.evidence_repository import EvidenceRepository
from hsie.entrypoint.services.analysis_context_service import (
    AnalysisContextService,
)
from hsie.entrypoint.services.asr_result_structurer import ASRResultStructurer
from hsie.entrypoint.services.asr_service import ASRService
from hsie.entrypoint.services.audio_metadata_service import AudioMetadataService


class HSIEController:
    """Controller for orchestrating HSIE EntryPoint layer processing.

    This controller orchestrates the complete flow from audio file input
    to Evidence saving without performing any judgment or interpretation.
    It executes services in a fixed sequence mechanically.

    Processing Flow:
        1. Collect AudioMetadata from audio file
        2. Transcribe audio using ASRService
        3. Build AnalysisContext from metadata and ASR result
        4. Structure ASR result into UtteranceUnits
        5. Assemble Evidence DTO
        6. Save Evidence using EvidenceRepository
        7. Return evidence_id

    Design Philosophy:
        - Pure orchestrator: No business logic or interpretation
        - Dependency injection: All services injected via constructor
        - Exception propagation: All exceptions propagated to caller
        - Sequential execution: Services executed in fixed order
    """

    def __init__(
        self,
        audio_metadata_service: AudioMetadataService,
        asr_service: ASRService,
        analysis_context_service: AnalysisContextService,
        asr_result_structurer: ASRResultStructurer,
        evidence_repository: EvidenceRepository,
    ) -> None:
        """Initialize HSIEController with required services.

        Args:
            audio_metadata_service: Service for collecting audio metadata.
            asr_service: Service for performing speech-to-text transcription.
            analysis_context_service: Service for building analysis context.
            asr_result_structurer: Service for structuring ASR results.
            evidence_repository: Repository for saving Evidence objects.
        """
        self.audio_metadata_service = audio_metadata_service
        self.asr_service = asr_service
        self.analysis_context_service = analysis_context_service
        self.asr_result_structurer = asr_result_structurer
        self.evidence_repository = evidence_repository

    def run(
        self,
        audio_path: Path,
        session_id: str,
        speaker_id: str,
        language: str,
    ) -> UUID:
        """Process audio file and save Evidence.

        This method orchestrates the complete processing flow from audio file
        to Evidence saving. It executes services in a fixed sequence without
        any judgment or interpretation.

        Args:
            audio_path: Path to the audio file to process.
            session_id: Conversation session identifier.
            speaker_id: Speaker identifier.
            language: Language code for ASR model selection.

        Returns:
            UUID: The evidence_id of the saved Evidence.

        Raises:
            FileNotFoundError: If the audio file does not exist.
            NotImplementedError: If ASRService is not implemented.
            IOError: If Evidence cannot be saved.
            Any other exception from services is propagated as-is.
        """
        # Step 1: Collect AudioMetadata from audio file
        audio_metadata = self.audio_metadata_service.collect(audio_path)

        # Step 2: Transcribe audio using ASRService
        asr_result = self.asr_service.transcribe(
            audio_metadata=audio_metadata,
            language=language,
        )

        # Step 3: Build AnalysisContext from metadata and ASR result
        analysis_context = self.analysis_context_service.build(
            audio_metadata=audio_metadata,
            asr_result=asr_result,
            session_id=session_id,
            speaker_id=speaker_id,
        )

        # Step 4: Structure ASR result into UtteranceUnits
        utterance_units = self.asr_result_structurer.structure(
            asr_result=asr_result,
            speaker_id=speaker_id,
        )

        # Step 5: Assemble Evidence DTO
        evidence = Evidence(
            context=analysis_context,
            asr_result=asr_result,
            utterance_units=utterance_units,
            saved_at=datetime.now(timezone.utc),
            version="v1",
        )

        # Step 6: Save Evidence using EvidenceRepository
        self.evidence_repository.save(evidence)

        # Step 7: Return evidence_id
        return evidence.evidence_id

