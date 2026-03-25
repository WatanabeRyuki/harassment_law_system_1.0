from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class MorphToken:
    """
    形態素情報DTO
    """
    surface: str        # 表層形
    base_form: str      # 原形
    pos: str            # 品詞


@dataclass(frozen=True)
class UtteranceDTO:
    """
    発話単位DTO（Segmentationの出力）
    """
    speaker_id: str
    start_time: float
    end_time: float
    text: str
    tokens: List[MorphToken]