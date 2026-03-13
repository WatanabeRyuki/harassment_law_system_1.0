from __future__ import annotations

import json
from typing import List, Dict

from hsie.preprocessed_evidence.dto.asr import (
    ASRPostProcessInputDTO,
    UtteranceDTO,
)


class ASRPromptBuilder:
    """
    ASR誤字修正専用プロンプト生成クラス。

    責務:
        - ASRPostProcessInputDTO を受け取り、
          LLMへ渡す最終文字列プロンプトを生成する。

    禁止事項:
        - DTO生成
        - JSONパース
        - LLM呼び出し
        - Validation
        - speaker変更
        - time変更
        - 並び替え
        - logging
        - I/O処理
        - 他層参照
    """

    def build(
        self,
        input_dto: ASRPostProcessInputDTO,
    ) -> str:
        """
        LLM用プロンプト文字列を生成する。

        Args:
            input_dto: ASRPostProcessInputDTO

        Returns:
            str: LLMへ渡す最終プロンプト文字列
        """

        system_instruction: str = (
            "あなたは音声認識(ASR)の誤字修正専用エンジンである。\n"
            "\n"
            "目的：\n"
            "誤字・脱字のみを修正せよ。\n"
            "\n"
            "修正ルール：\n"
            "1. 文脈を理解して自然な日本語になるよう単語のみを修正する。\n"
            "2. 会話として意味が通る単語に修正する。\n"
            "4. 意味が明らかに破綻している場合のみ単語を修正する。\n"
            "5. 文脈から明らかに誤認識と判断できる場合のみ単語を修正する。\n"
            "\n"
            "厳守事項：\n"
            "1. 意味を変更してはならない。\n"
            "2. 文の追加をしてはならない。\n"
            "3. 文の削除をしてはならない。\n"
            "4. 文の分割をしてはならない。\n"
            "5. 文の結合をしてはならない。\n"
            "6. 出力順を変更してはならない。\n"
            "7. 単語のみの修正を行い、文の修正はしてはならない。\n"
            "7. utterance_idは入力と完全一致させること。\n"
            "8. 修正が不要な場合は原文をそのまま出力せよ。\n"
            "9. JSON配列のみを出力せよ。\n"
            "10. 説明文・注釈・コードブロックを出力してはならない。\n"
            "\n"
            "出力形式：\n"
            "[\n"
            "  {\n"
            '    "utterance_id": "...",\n'
            '    "corrected_text": "..."\n'
            "  }\n"
            "]\n"
            "\n"
            "配列長は入力と完全一致させること。"
        )

        utterances_payload: List[Dict[str, str]] = [
            {
                "utterance_id": utterance.utterance_id,
                "speaker_id": utterance.speaker_id,
                "text": utterance.text,
            }
            for utterance in input_dto.utterances
        ]

        json_input: str = json.dumps(
            utterances_payload,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        language: str = input_dto.language

        prompt: str = (
            f"{system_instruction}\n\n"
            f"Input Language: {language}\n\n"
            f"Input Utterances:\n"
            f"{json_input}\n\n"
            "Output must strictly follow the specified JSON structure."
        )

        return prompt