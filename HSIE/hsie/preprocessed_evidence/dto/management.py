"""Management DTO."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ManagementDTO:
    """Management/metadata section."""

    version: str
    build_timestamp: datetime
