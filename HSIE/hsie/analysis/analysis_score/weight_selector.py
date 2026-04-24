from .dto.speaker_score_input_dto import SpeakerScoreInputDTO


def select_weights(speaker_input: SpeakerScoreInputDTO):
    L = speaker_input.language_score
    S = speaker_input.structure_score
    is_S_reversal = speaker_input.is_S_reversal

    # 条件3：L >= 85（最優先）
    if L >= 85:
        return 0.30, 0.70, "L_highest"

    #条件5追加ロジック Lスコア（言葉の丁寧さ）が高くても、構造的支配が強すぎる場合は強制的にSを重視
    elif S >= 75:
        return 0.80, 0.20, "S_highest"
    
    #条件6追加ロジック
    elif L >= 65:
        return 0.40, 0.60, "L_high"

    # 条件1：反転ロジック
    elif is_S_reversal:
        return 0.80, 0.20, "S_reversal"

    # 条件2：S高 & L低
    elif S > 60 and L < 30:
        return 0.20, 0.80, "S_high_L_low"

    # デフォルト
    else:
        return 0.50, 0.50, "default"