"""Alignment metadata DTO."""

from dataclasses import dataclass


@dataclass
class AlignmentMetaDTO:
    """Alignment metadata section."""

    time_base: str
