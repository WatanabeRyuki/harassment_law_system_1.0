"""話者分離（Diarization）関連DTO定義."""

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import List, Union


@dataclass(frozen=True)
class DiarizationInputDTO:
    """
    話者分離入力DTO。

    Attributes:
        audio_path: 音声ファイルパス
    """

    audio_path: Union[str, Path]


@dataclass(frozen=True)
class SpeakerSegmentDTO:
    """
    話者区間DTO。

    Attributes:
        speaker_id: 話者ID（例: speaker_0）
        start_time: 開始時間（秒）
        end_time: 終了時間（秒）
    """

    speaker_id: str
    start_time: Decimal
    end_time: Decimal


@dataclass(frozen=True)
class DiarizationOutputDTO:
    """
    話者分離出力DTO。

    Attributes:
        speaker_segments: 話者区間リスト（start_time昇順）
    """

    speaker_segments: List[SpeakerSegmentDTO]
