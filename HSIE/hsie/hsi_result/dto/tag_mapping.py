# hsie/hsi_result/dto/tag_mapping.py

from dataclasses import dataclass
from typing import List


@dataclass
class TagMapping:
    evidence_text: str
    derived_tags: List[str]
    reason: str