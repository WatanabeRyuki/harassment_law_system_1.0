from decimal import Decimal
from typing import Dict, List, Any

from pyannote.core import Annotation

from hsie.preprocessed_evidence.dto.diarization import (
    DiarizationOutputDTO,
    SpeakerSegmentDTO,
)


class DiarizationMapper:
    """
    Convert pyannote diarization result into HSIE DTO structure.

    pyannote.audio 4.x 以降では、パイプラインの戻り値が
    `DiarizeOutput` のようなラッパー型となり、その中に
    `speaker_diarization` 属性として Annotation が含まれる。
    このクラスでは旧来の Annotation 直接返却パターンと、
    新しいラッパー型の両方をサポートする。
    """

    def _extract_annotation(self, diarization: Any) -> Annotation:
        """
        サポートされる型から Annotation を取り出す。

        優先順:
            1. 引数自体が Annotation で itertracks を持つ場合
            2. `speaker_diarization` 属性が Annotation の場合
        """
        # 1) すでに Annotation 互換（itertracks を持つ）ならそのまま使う
        if hasattr(diarization, "itertracks"):
            return diarization  # type: ignore[return-value]

        # 2) pyannote.audio 4.x 系の DiarizeOutput: .speaker_diarization を参照
        candidate = getattr(diarization, "speaker_diarization", None)
        if candidate is not None and hasattr(candidate, "itertracks"):
            return candidate  # type: ignore[return-value]

        raise TypeError(
            f"Unsupported diarization result type: {type(diarization)!r}. "
            "Expected Annotation or object with 'speaker_diarization' Annotation."
        )

    def to_output_dto(
        self,
        diarization: Any,
    ) -> DiarizationOutputDTO:

        annotation: Annotation = self._extract_annotation(diarization)

        label_mapping: Dict[str, str] = {}
        segments: List[SpeakerSegmentDTO] = []

        for turn, _, label in annotation.itertracks(yield_label=True):

            # 初出現順 speaker_id 割り当て
            if label not in label_mapping:
                label_mapping[label] = f"speaker_{len(label_mapping)}"

            new_id: str = label_mapping[label]

            # Decimal変換（証拠再現性のため）
            start_time: Decimal = Decimal(str(turn.start))
            end_time: Decimal = Decimal(str(turn.end))

            # 異常区間防止（pyannote稀発バグ）
            if end_time < start_time:
                continue

            segment = SpeakerSegmentDTO(
                speaker_id=new_id,
                start_time=start_time,
                end_time=end_time,
            )

            segments.append(segment)

        # 時系列順ソート
        segments.sort(key=lambda s: s.start_time)

        return DiarizationOutputDTO(
            speaker_segments=segments
        )