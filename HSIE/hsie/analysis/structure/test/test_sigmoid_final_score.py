import math
import matplotlib.pyplot as plt

def calc_final_score(x: float, a: float = 0.12, b: float = 50.0) -> float:
    """
    話者ごとの最終Sスコアを算出する（0〜100）
    """
    z = a * (x - b)

    # オーバーフロー対策
    if z > 60:
        return 100.0
    elif z < -60:
        return 0.0

    # シグモイド計算
    S = 100 / (1 + math.exp(-z))
    
    # 0〜100の範囲に収める
    return max(0.0, min(S, 100.0))

def main():
    # x軸のデータ（0から100まで1刻み）
    x_values = list(range(101))
    
    # y軸のデータ（計算結果）
    y_values = [calc_final_score(x) for x in x_values]

    # グラフの描画設定
    plt.figure(figsize=(10, 6))
    
    # メインの曲線を描画
    plt.plot(x_values, y_values, label="Sigmoid (a=0.12, b=50.0)", color="#1f77b4", linewidth=2.5)
    
    # 変化の中心点（x=50, y=50）に赤い点線を引く
    plt.axvline(x=50, color="red", linestyle="--", alpha=0.6, label="Center (x=50)")
    plt.axhline(y=50, color="red", linestyle="--", alpha=0.6)

    # グラフの装飾（タイトル、ラベル、メモリ線など）
    plt.title("Sigmoid Curve: Final Score Visualization", fontsize=14)
    plt.xlabel("Input Score (x)", fontsize=12)
    plt.ylabel("Final Score (S)", fontsize=12)
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.grid(True, linestyle=":", alpha=0.8)
    plt.legend(fontsize=11)
    
    # グラフを表示
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()