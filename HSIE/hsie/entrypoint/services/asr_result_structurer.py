"""ASR result structurer for HSIE EntryPoint layer.

This service structures ASR segments into UtteranceUnit objects
by applying mechanical rules based on time information and simple patterns.
It does not perform any analysis, judgment, or interpretation.
"""

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .asr_service import ASRResult, ASRSegment


# Constants for pause level classification
PAUSE_THRESHOLD_SHORT: float = 0.7  # Seconds
PAUSE_THRESHOLD_LONG: float = 2.0  # Seconds

# Constants for filler words (mechanical list)
FILLER_WORDS: set[str] = {
    "えー",
    "あの",
    "そのー",
    "えっと",
    "まあ",
    "なんか",
    "その",
    "あー",
    "うーん",
    "んー",
}

# Constants for incomplete sentence endings (mechanical list)
INCOMPLETE_ENDINGS: set[str] = {
    "て",
    "で",
    "から",
    "ので",
    "のに",
    "けど",
    "が",
    "けれど",
    "けれども",
}


class UtteranceUnit(BaseModel):
    """Utterance unit structure.

    Represents the minimum meaningful utterance unit extracted from ASR segments.
    This structure contains only mechanical structuring results without any
    analysis, judgment, or interpretation.

    Attributes:
        utterance_id: Unique identifier for this utterance (UUID).
        speaker_id: Speaker identifier (fixed in Phase1).
        text: Utterance text content.
        start_time: Start time of the utterance in seconds.
        end_time: End time of the utterance in seconds.
        duration: Duration of the utterance in seconds (end_time - start_time).
        confidence: ASR confidence score (None if not available).
        pause_before: Silence duration before this utterance in seconds.
        pause_level: Pause level classification (SHORT / NORMAL / LONG).
        index_in_session: Sequential index of this utterance in the session (0-based).
    """

    utterance_id: UUID = Field(..., description="Unique identifier for this utterance (UUID)")
    speaker_id: str = Field(..., description="Speaker identifier (fixed in Phase1)")
    text: str = Field(..., description="Utterance text content")
    start_time: float = Field(..., description="Start time of the utterance in seconds", ge=0.0)
    end_time: float = Field(..., description="End time of the utterance in seconds", ge=0.0)
    duration: float = Field(..., description="Duration of the utterance in seconds")
    confidence: Optional[float] = Field(None, description="ASR confidence score (None if not available)")
    pause_before: float = Field(..., description="Silence duration before this utterance in seconds", ge=0.0)
    pause_level: str = Field(..., description="Pause level classification (SHORT / NORMAL / LONG)")
    index_in_session: int = Field(..., description="Sequential index of this utterance in the session (0-based)", ge=0)

    class Config:
        """Pydantic configuration."""

        frozen = True  # Make the utterance unit immutable
        validate_assignment = True


class ASRResultStructurer:
    """Service for structuring ASR segments into utterance units.

    This service applies mechanical rules based on time information and simple
    patterns to extract meaningful utterance units from ASR segments.
    It does not perform any analysis, judgment, or interpretation.

    Design Philosophy:
        - EntryPoint layer responsibility: Structure ASR results only
        - No analysis: Does not interpret meaning, attack, pressure, or legal judgment
        - Mechanical rules: Uses only reproducible, mechanical rules
        - Time-based structuring: Extracts utterance units based on time information
        - Pattern-based merging: Applies simple pattern matching for merging segments

    Rules Applied:
        1. Pause calculation: Calculates pause_before from time differences
        2. Pause level classification: Classifies pauses into SHORT/NORMAL/LONG
        3. Filler merging: Merges filler-only segments with previous utterance
        4. Incomplete sentence merging: Merges segments ending with incomplete endings
           when followed by SHORT pause
    """

    def structure(
        self,
        asr_result: ASRResult,
        speaker_id: str,
    ) -> list[UtteranceUnit]:
        """Structure ASR segments into utterance units.

        This method processes ASRResult.segments in chronological order,
        applies mechanical rules for merging and structuring, and returns
        a list of UtteranceUnit objects.

        Args:
            asr_result: ASRResult object containing segments to structure.
            speaker_id: Speaker identifier (fixed in Phase1).

        Returns:
            list[UtteranceUnit]: List of structured utterance units in chronological order.

        Note:
            - Segments are processed in chronological order (by start_time)
            - index_in_session is assigned sequentially starting from 0
            - pause_before for the first utterance is always 0.0
            - Mechanical rules are applied for merging segments
            - No analysis or interpretation is performed
        """
        # Get segments and ensure they are sorted by start_time
        segments = sorted(asr_result.segments, key=lambda s: s.start_time)

        if not segments:
            return []

        # Process segments and build utterance units
        utterance_units: list[UtteranceUnit] = []
        index = 0

        i = 0
        while i < len(segments):
            current_segment = segments[i]

            # Check if current segment is a filler-only segment
            if self._is_filler_only(current_segment.text):
                # Merge with previous utterance if exists
                if utterance_units:
                    utterance_units[-1] = self._merge_with_previous(
                        utterance_units[-1],
                        current_segment,
                    )
                    i += 1
                    continue
                # If no previous utterance, treat as normal segment
                # (fall through to normal processing)

            # Check if current segment should be merged with next segment
            # (incomplete sentence ending + SHORT pause)
            # Note: Skip this check if next segment is a filler (filler merging takes priority)
            if i + 1 < len(segments):
                next_segment = segments[i + 1]
                
                # Skip incomplete merging if next segment is a filler
                # (filler will be merged with the current segment after it becomes an utterance)
                if not self._is_filler_only(next_segment.text):
                    pause = next_segment.start_time - current_segment.end_time

                    if self._has_incomplete_ending(current_segment.text) and self._is_short_pause(pause):
                        # Merge current and next segments
                        merged_segment = self._merge_segments(current_segment, next_segment)
                        utterance_unit = self._create_utterance_unit(
                            merged_segment,
                            speaker_id,
                            utterance_units,
                            index,
                        )
                        utterance_units.append(utterance_unit)
                        index += 1
                        i += 2  # Skip both segments
                        continue

            # Normal processing: create utterance unit from single segment
            utterance_unit = self._create_utterance_unit(
                current_segment,
                speaker_id,
                utterance_units,
                index,
            )
            utterance_units.append(utterance_unit)
            index += 1
            i += 1

        return utterance_units

    def _create_utterance_unit(
        self,
        segment: ASRSegment,
        speaker_id: str,
        previous_units: list[UtteranceUnit],
        index: int,
    ) -> UtteranceUnit:
        """Create an UtteranceUnit from a segment.

        Args:
            segment: ASRSegment to convert to UtteranceUnit.
            speaker_id: Speaker identifier.
            previous_units: List of previously created utterance units.
            index: Index for this utterance unit.

        Returns:
            UtteranceUnit: Created utterance unit with calculated pause information.
        """
        # Calculate pause_before
        if previous_units:
            last_unit = previous_units[-1]
            pause_before = segment.start_time - last_unit.end_time
            # Ensure pause_before is non-negative (handle overlapping segments)
            pause_before = max(0.0, pause_before)
        else:
            pause_before = 0.0

        # Classify pause level
        pause_level = self._classify_pause_level(pause_before)

        # Calculate duration
        duration = segment.end_time - segment.start_time

        # Generate utterance_id
        utterance_id = uuid4()

        return UtteranceUnit(
            utterance_id=utterance_id,
            speaker_id=speaker_id,
            text=segment.text,
            start_time=segment.start_time,
            end_time=segment.end_time,
            duration=duration,
            confidence=None,  # ASR confidence not available in current ASRSegment
            pause_before=pause_before,
            pause_level=pause_level,
            index_in_session=index,
        )

    def _merge_segments(self, segment1: ASRSegment, segment2: ASRSegment) -> ASRSegment:
        """Merge two segments into one.

        This is a mechanical operation that combines text and time information.
        No meaning interpretation is performed.

        Args:
            segment1: First segment (earlier in time).
            segment2: Second segment (later in time).

        Returns:
            ASRSegment: Merged segment with combined text and time range.
        """
        # Combine text with space
        merged_text = f"{segment1.text} {segment2.text}".strip()

        # Use time range from first to second segment
        merged_start = segment1.start_time
        merged_end = segment2.end_time

        # Create merged segment (using segment1's segment_id as base)
        return ASRSegment(
            segment_id=segment1.segment_id,
            start_time=merged_start,
            end_time=merged_end,
            text=merged_text,
            speaker_id=segment1.speaker_id,
        )

    def _merge_with_previous(
        self,
        previous_unit: UtteranceUnit,
        filler_segment: ASRSegment,
    ) -> UtteranceUnit:
        """Merge filler segment with previous utterance unit.

        This is a mechanical operation that combines text and time information.
        No meaning interpretation is performed.

        Args:
            previous_unit: Previous UtteranceUnit to merge with.
            filler_segment: Filler segment to merge.

        Returns:
            UtteranceUnit: Updated utterance unit with merged text and time range.
        """
        # Combine text with space
        merged_text = f"{previous_unit.text} {filler_segment.text}".strip()

        # Extend time range to include filler segment
        merged_end = max(previous_unit.end_time, filler_segment.end_time)

        # Recalculate duration
        merged_duration = merged_end - previous_unit.start_time

        # Create new UtteranceUnit with merged information
        # Note: pause_before and pause_level remain unchanged (from original)
        return UtteranceUnit(
            utterance_id=previous_unit.utterance_id,
            speaker_id=previous_unit.speaker_id,
            text=merged_text,
            start_time=previous_unit.start_time,
            end_time=merged_end,
            duration=merged_duration,
            confidence=previous_unit.confidence,
            pause_before=previous_unit.pause_before,
            pause_level=previous_unit.pause_level,
            index_in_session=previous_unit.index_in_session,
        )

    def _is_filler_only(self, text: str) -> bool:
        """Check if text contains only filler words.

        This is a mechanical check using a fixed list of filler words.
        No meaning interpretation is performed.

        Args:
            text: Text to check.

        Returns:
            bool: True if text contains only filler words, False otherwise.
        """
        # Normalize text (strip whitespace)
        normalized_text = text.strip()

        # Check if normalized text is in filler words set
        return normalized_text in FILLER_WORDS

    def _has_incomplete_ending(self, text: str) -> bool:
        """Check if text ends with incomplete sentence endings.

        This is a mechanical check using endswith() on a fixed list.
        No grammatical analysis is performed.

        Args:
            text: Text to check.

        Returns:
            bool: True if text ends with incomplete ending, False otherwise.
        """
        # Normalize text (strip whitespace)
        normalized_text = text.strip()

        # Check if text ends with any incomplete ending
        for ending in INCOMPLETE_ENDINGS:
            if normalized_text.endswith(ending):
                return True

        return False

    def _is_short_pause(self, pause_duration: float) -> bool:
        """Check if pause duration is classified as SHORT.

        Args:
            pause_duration: Pause duration in seconds.

        Returns:
            bool: True if pause is SHORT, False otherwise.
        """
        return pause_duration < PAUSE_THRESHOLD_SHORT

    def _classify_pause_level(self, pause_duration: float) -> str:
        """Classify pause duration into SHORT, NORMAL, or LONG.

        This is a mechanical classification based on fixed thresholds.
        No interpretation is performed.

        Args:
            pause_duration: Pause duration in seconds (must be >= 0.0).

        Returns:
            str: Pause level classification ("SHORT", "NORMAL", or "LONG").
        """
        if pause_duration < PAUSE_THRESHOLD_SHORT:
            return "SHORT"
        elif pause_duration < PAUSE_THRESHOLD_LONG:
            return "NORMAL"
        else:
            return "LONG"

