def calculate_hsi(S: float, L: float, alpha: float, beta: float) -> float:
    hsi = alpha * S + beta * L

    # 0〜100にクリップ
    return max(0.0, min(100.0, hsi))