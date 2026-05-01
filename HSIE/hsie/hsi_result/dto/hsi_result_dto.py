# hsie/hsi_result/dto/hsi_result_dto.py

from dataclasses import dataclass
from typing import List
from .tag_mapping import TagMapping


@dataclass
class HSIResultDTO:

    speaker_id: str

    risk_level: str  # "low" | "gray" | "medium" | "high"

    legal_tags: List[str]
    search_queries: List[str]
    tag_mappings: List[TagMapping]

    summary: str