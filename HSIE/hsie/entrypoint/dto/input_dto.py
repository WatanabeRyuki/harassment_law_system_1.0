"""Input DTO for HSIE EntryPoint layer.

This module defines the input data transfer object that represents
the maximum information allowed to be passed from external inputs
(FastAPI / API / UI) to the Controller layer.
"""

from pathlib import Path
from typing import Union

from pydantic import BaseModel, Field


class HSIEInputDTO(BaseModel):
    """Input DTO for HSIE system.

    This DTO defines the upper limit of information that can be received
    by the Controller. It serves as a design boundary to prevent
    Controller from becoming bloated.

    Attributes:
        audio_file: Path or string reference to the audio file entity.
        session_id: Conversation session identifier.
        speaker_id: Speaker ID (Phase1: manually specified).
        language: Language code for ASR model selection.
    """

    audio_file: Union[Path, str] = Field(
        ...,
        description="Audio file entity or reference path"
    )
    session_id: str = Field(
        ...,
        description="Conversation session identifier"
    )
    speaker_id: str = Field(
        ...,
        description="Speaker ID (Phase1: manually specified)"
    )
    language: str = Field(
        ...,
        description="Language code for ASR model selection"
    )

    class Config:
        """Pydantic configuration."""

        frozen = True  # Make the DTO immutable
        validate_assignment = True

