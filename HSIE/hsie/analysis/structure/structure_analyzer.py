from typing import Any, List, Dict, Tuple, Optional

from .segmentation import segment_conversation
from .turn_detection import detect_turns
from .interruption import detect_interruptions
from .turn_occupancy import calc_turn_occupancy
from .negation_chain import detect_negation_chain
from .structural_pressure import calc_structural_pressure
from .scoring import calc_s_raw
from .correction import apply_correction
from .final_score import calc_final_score

# 新規追加：静かな圧を解決するモジュール
from .silent_aggression_resolver import SilentAggressionResolver

from .dto.structure_result_dto import StructureResultDTO
from .dto.turn_dto import TurnDTO


def analyze_structure(data: Any) -> Tuple[Dict[str, StructureResultDTO], float, Optional[str]]:
    """
    Structure Aggression Analyzer 統合パイプライン（全話者対応版）
    戻り値: (結果辞書, SAIスコア, 加害者として反転された話者ID)
    """

    # ① segmentation (全話者の発話を抽出)
    utterances = segment_conversation(data)
    if not utterances:
        return {}, 0.0, None

    # 話者リストの取得
    speakers = list(set(u.speaker_id for u in utterances))

    # ② turn detection (話者交代の構造化)
    turns = detect_turns(utterances)
    if not turns:
        return {sid: _empty_result(sid) for sid in speakers}, 0.0, None

    # ==========================================
    # 指標算出（基本メトリクス）
    # ==========================================
    
    # ④ interruption (辞書: {sid: InterruptionDTO})
    inter_results = detect_interruptions(turns, speakers)

    # ⑤ turn occupancy (辞書: {sid: float})
    occupancy_results = calc_turn_occupancy(utterances, speakers)

    # ⑥ negation chain (辞書: {sid: float})
    negation_results = detect_negation_chain(turns, speakers)

    # ==========================================
    # 静かな圧（Silent Aggression）の判定と占有率の反転
    # ==========================================
    
    # Resolverに必要な統計情報を準備
    speaker_stats = {}
    for sid in speakers:
        speaker_utters = [u for u in utterances if u.speaker_id == sid]
        total_chars = sum(len(u.text) for u in speaker_utters)
        count = len(speaker_utters)
        speaker_stats[sid] = {
            "occupancy": occupancy_results.get(sid, 0.0),
            "avg_chars": total_chars / count if count > 0 else 0,
            "utterance_count": count
        }

    # 反転ロジックの適用
    resolver = SilentAggressionResolver()
    # 占有率が反転される場合、updated_stats 内の occupancy が書き換わる
    updated_stats, sai_score, aggressor_id = resolver.resolve(speaker_stats, utterances)
    
    # 反転結果を occupancy_results に反映（後の計算で使用するため）
    for sid in speakers:
        occupancy_results[sid] = updated_stats[sid]["occupancy"]

    # ==========================================
    # ⑦ structural pressure (ウィンドウ単位の集計と係数算出)
    # ※ 反転後の占有率を用いて計算されるため、加害者の c が上昇する
    # ==========================================
    scores_by_window = _build_window_scores(
        speakers, occupancy_results, inter_results, negation_results
    )
    c_results = calc_structural_pressure(scores_by_window, speakers)

    # ==========================================
    # 最終スコアリング（話者ごとにループ実行）
    # ==========================================
    final_results: Dict[str, StructureResultDTO] = {}

    for sid in speakers:
        # ⑧ S_raw の算出 (反転済みの occupancy を使用)
        score_params = {
            "turn_occupancy": occupancy_results.get(sid, 0.0),
            "interruption_rate": inter_results[sid].interruption_rate,
            "negation_score": negation_results.get(sid, 0.0)
        }
        s_raw = calc_s_raw(score_params)

        # ⑨ correction
        c = c_results.get(sid, 1.0)
        x = apply_correction(s_raw, c)

        # ⑩ final score
        fs = calc_final_score(x)

        # DTOに格納
        final_results[sid] = StructureResultDTO(
            speaker_id=sid,
            s_raw=s_raw,
            c=c,
            x=x,
            final_score=fs
        )

    return final_results, sai_score, aggressor_id


# =========================
# 内部関数
# =========================

def _empty_result(speaker_id: str) -> StructureResultDTO:
    return StructureResultDTO(
        speaker_id=speaker_id,
        s_raw=0.0,
        c=1.0,
        x=0.0,
        final_score=0.0
    )


def _build_window_scores(
    speakers: List[str],
    occupancy: Dict[str, float],
    inter: Dict[str, Any],
    negation: Dict[str, float]
) -> List[Dict[str, Dict[str, float]]]:
    """
    3分ウィンドウごとのスコア構造を生成
    """
    window_data = {}
    for sid in speakers:
        window_data[sid] = {
            "turn_occupancy": occupancy.get(sid, 0.0),
            "interruption_rate": inter[sid].interruption_rate,
            "negation_score": negation.get(sid, 0.0)
        }
    
    return [window_data]