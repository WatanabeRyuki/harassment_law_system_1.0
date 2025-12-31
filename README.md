📌 Project Status（現状）

本プロジェクトは現在、以下の段階まで到達しています。

🟢 完了済み

企画書

要件定義書

基本設計書

全体 HSIE 詳細設計書

4.1 エントリーポイント層 設計・実装 完了

EntryPoint 層の責務定義

全体フロー図（assets フォルダ内）

HSIEController 実装

音声入力 → ASR → Evidence(JSON) 生成までの End-to-End 実行確認済み

Evidence は immutable なスナップショットとして保存

🟡 設計完了・実装準備中

4.2 前処理層 設計書

全体フロー図に反映済み（assets フォルダ）

話者分離・セグメント再構成・前処理 Evidence 生成を担う層

EntryPoint 層で生成された Evidence を入力とする設計

🔵 今後実装予定

前処理層（話者分離・再ラベリング・構造正規化）

分析層（A/S/L 分析）

Acoustic / Semantic / Linguistic 各分析モデル

ハラスメント強度指標（HSI / HSIE）算出

Evidence の多段バージョニング（Raw → Preprocessed → Analyzed）

🧠 Architectural Philosophy

EntryPoint 層は **「事実の収集のみ」**を行う

分析・判断・解釈は一切行わない

各層は immutable な Evidence を生成し、前段の Evidence を破壊しない

再現性・監査可能性を最重要視

🚧 Notes

話者識別（speaker diarization）は EntryPoint 層では行いません

speaker_id は前処理層にて再付与される想定です

現在の Evidence JSON は Raw Evidence と位置付けています
