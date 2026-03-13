"""LLMレスポンスを厳格検証し、ASRPostProcessOutputDTO に変換する純粋変換層."""

import json

from hsie.preprocessed_evidence.dto.asr import (
    ASRPostProcessInputDTO,
    ASRPostProcessOutputDTO,
    CorrectedUtteranceDTO,
)


class ASRResponseMapper:
    """LLMレスポンスを厳格検証し DTO に変換する純粋変換層."""

    def to_output_dto(
        self,
        response: str,
        input_dto: ASRPostProcessInputDTO,
    ) -> ASRPostProcessOutputDTO:
        """
        response を検証し ASRPostProcessOutputDTO を返す。

        Args:
            response: LLMの生レスポンス文字列
            input_dto: 入力DTO（発話リスト・言語情報）

        Returns:
            検証済み ASRPostProcessOutputDTO

        Raises:
            ValueError: JSONパース失敗、構造不正、内容不正、コードブロック不正形式など
        """
        raw: str = response.strip()

        if raw.startswith("```") and raw.endswith("```"):
            lines: list[str] = raw.splitlines()
            inner_lines: list[str] = lines[1:-1]
            extracted: str = "\n".join(inner_lines).strip()
        else:
            if not raw.startswith("["):
                raise ValueError("response must be JSON array or valid code block")
            extracted = raw

        if not (extracted.startswith("[") and extracted.endswith("]")):
            raise ValueError("extracted content must start with '[' and end with ']'")

        try:
            data: list[dict[str, str]] = json.loads(extracted)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON parse failed: {e!s}") from e

        if not isinstance(data, list):
            raise ValueError("response must be JSON array, not dict or other")

        if len(data) != len(input_dto.utterances):
            raise ValueError(
                f"array length mismatch: expected {len(input_dto.utterances)}, got {len(data)}"
            )

        required_keys: frozenset[str] = frozenset({"utterance_id", "corrected_text"})
        seen_ids: set[str] = set()

        corrected_utterances: list[CorrectedUtteranceDTO] = []

        for index, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"item at index {index} must be dict")

            item_keys: frozenset[str] = frozenset(item.keys())
            if item_keys != required_keys:
                raise ValueError(
                    f"item at index {index} has invalid keys: expected {required_keys}, got {item_keys}"
                )

            utterance_id: str = item["utterance_id"]
            corrected_text: str = item["corrected_text"]

            if not isinstance(utterance_id, str):
                raise ValueError(f"utterance_id at index {index} must be str")
            if not isinstance(corrected_text, str):
                raise ValueError(f"corrected_text at index {index} must be str")
            if corrected_text.strip() == "":
                raise ValueError(f"corrected_text at index {index} must not be empty")

            expected_id: str = input_dto.utterances[index].utterance_id
            if utterance_id != expected_id:
                raise ValueError(
                    f"utterance_id order mismatch at index {index}: expected {expected_id!r}, got {utterance_id!r}"
                )

            if utterance_id in seen_ids:
                raise ValueError(f"duplicate utterance_id: {utterance_id!r}")
            seen_ids.add(utterance_id)

            utterance = input_dto.utterances[index]
            corrected_utterance: CorrectedUtteranceDTO = CorrectedUtteranceDTO(
                utterance_id=utterance.utterance_id,
                speaker_id=utterance.speaker_id,
                start_time=utterance.start_time,
                end_time=utterance.end_time,
                corrected_text=corrected_text,
            )
            corrected_utterances.append(corrected_utterance)

        return ASRPostProcessOutputDTO(corrected_utterances=corrected_utterances)
