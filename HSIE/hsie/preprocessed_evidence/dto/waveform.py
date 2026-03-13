"""Waveform関連DTO定義."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class WaveformInputDTO:
    """
    Waveform入力DTO。

    Attributes:
        audio_path: 音声ファイルパス
    """

    audio_path: str


@dataclass(frozen=True)
class WaveformDTO:
    """
    WaveformDTO。

    Attributes:
        values: 生波形数値リスト
        sampling_rate: サンプリングレート
        ui_downsampled_values: UI表示用ダウンサンプル済み波形
    """

    values: list[float]
    sampling_rate: int
    ui_downsampled_values: list[float]


@dataclass(frozen=True)
class WaveformOutputDTO:
    """
    Waveform出力DTO。

    Attributes:
        waveform: WaveformDTO
        sampling_rate: サンプリングレート
        duration: 音声長（秒）
    """

    waveform: WaveformDTO
    sampling_rate: int
    duration: Decimal
