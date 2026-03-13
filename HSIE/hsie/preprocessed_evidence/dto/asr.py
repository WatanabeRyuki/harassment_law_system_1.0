"""ASR関連DTO定義."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class UtteranceDTO:
    """
    発話情報を保持するDTO。

    Attributes:
        utterance_id: 発話の一意識別子
        speaker_id: 話者ID
        text: 発話テキスト
        start_time: 発話開始時間（秒）
        end_time: 発話終了時間（秒）
    """

    utterance_id: str
    speaker_id: str
    text: str
    start_time: float
    end_time: float


@dataclass(frozen=True)
class CorrectedUtteranceDTO:
    """
    補正済み発話情報を保持するDTO。

    Attributes:
        utterance_id: 発話の一意識別子
        speaker_id: 話者ID
        start_time: 発話開始時間（秒）
        end_time: 発話終了時間（秒）
        corrected_text: 補正済みテキスト
    """

    utterance_id: str
    speaker_id: str
    start_time: float
    end_time: float
    corrected_text: str


@dataclass(frozen=True)
class ASRPostProcessInputDTO:
    """
    ASR後処理入力DTO。

    Attributes:
        utterances: 発話リスト
        language: 言語コード
    """

    utterances: List[UtteranceDTO]
    language: str


@dataclass(frozen=True)
class ASRPostProcessOutputDTO:
    """
    ASR後処理出力DTO。

    Attributes:
        corrected_utterances: 補正済み発話リスト
    """

    corrected_utterances: List[CorrectedUtteranceDTO]
