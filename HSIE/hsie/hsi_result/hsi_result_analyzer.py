# hsie/hsi_result/hsi_result_analyzer.py

from typing import List

from .dto.hsi_result_input_dto import HSIResultInputDTO
from .dto.hsi_result_dto import HSIResultDTO
from .dto.tag_mapping import TagMapping

from .risk_classifier import classify_hsi
from .evidence_processor import process_evidence
from .legal_mapper import map_to_legal_tags
from .query_generator import generate_queries
from .summary_generator import generate_summary


class HSIResultAnalyzer:

    @staticmethod
    def execute(input_dto: HSIResultInputDTO) -> HSIResultDTO:

        # -----------------------------
        # ① HSI分類
        # -----------------------------
        risk_level = classify_hsi(input_dto.hsi_score)

        # -----------------------------
        # ② lowの場合は軽量出力
        # -----------------------------
        if risk_level == "low":
            return HSIResultDTO(
                speaker_id=input_dto.speaker_id,
                risk_level=risk_level,
                legal_tags=[],
                search_queries=[],
                tag_mappings=[],
                summary="現時点では強い問題行動は確認されませんが、受け手によっては印象が異なる場合があるため注意が必要です。"
            )

        # -----------------------------
        # ③ Evidence解析
        # -----------------------------
        category_count, normalized_evidences = process_evidence(
            input_dto.evidences
        )

        # -----------------------------
        # ④ 法律タグ生成
        # -----------------------------
        legal_tags = map_to_legal_tags(
            category_count=category_count,
            turn_occupancy=input_dto.turn_occupancy,
            interruption_rate=input_dto.interruption_rate,
            negation_score=input_dto.negation_score,
            evidences=input_dto.evidences
        )

        # -----------------------------
        # ⑤ クエリ生成
        # -----------------------------
        search_queries = generate_queries(legal_tags)

        # -----------------------------
        # ⑥ TagMapping生成
        # -----------------------------
        tag_mappings: List[TagMapping] = []

        for ev in normalized_evidences:

            derived_tags = []

            for cat in ev["categories"]:
                # legal_mapperと同じ変換を使用
                from .legal_mapper import CATEGORY_MAP
                derived_tags.extend(CATEGORY_MAP.get(cat, []))

            tag_mappings.append(
                TagMapping(
                    evidence_text=ev["text"],
                    derived_tags=list(set(derived_tags)),
                    reason=f"{', '.join(ev['categories'])} に該当するため"
                )
            )

        # -----------------------------
        # ⑦ summary生成
        # -----------------------------
        summary = generate_summary(legal_tags, risk_level)

        # -----------------------------
        # ⑧ DTO生成
        # -----------------------------
        return HSIResultDTO(
            speaker_id=input_dto.speaker_id,
            risk_level=risk_level,
            legal_tags=legal_tags,
            search_queries=search_queries,
            tag_mappings=tag_mappings,
            summary=summary
        )