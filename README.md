本プロジェクトは、会話データをもとにハラスメント構造を可視化し、
証拠保全と事後フィードバックによる行動変容支援を目的としたシステム
**HSIE（Harassment Structure Index Evidence）**の開発である。
このシステムは従来の他のモデルでは検知できないハラスメントを独自のロジックを用いて検知することができる世界初の検知システムである。

本プロジェクトは、ハラスメント検知ではなく「証拠保全と構造分析」に重点を置いた独自アーキテクチャを採用し、現在は音声入力から分析前処理までの基盤が完成し、最大の独自ロジックである会話構造性分析（S）の実装を終えた段階にある。今後は音声・言語分析（A/L）および統合指標（HSI）の実装により、評価機能の完成を目指す。

📌 Project Status（現状）

本プロジェクトは現在、以下の段階まで到達しています。

🟢 完了済み

企画書

↓

要件定義書

↓

基本設計書

↓

全体 HSIE 詳細設計書

↓

エントリーポイント層 設計・実装 完了

　|-EntoryPoint層(フォルダ)
 
     |-エントリーポイント設計書
     
     |-エントリーポイントassets
     
         |-エントリーポイント詳細設計書 -  フローチャート.pdf
         
         |-HSIE エントリーポイントER図 -  フローチャート.pdf
         
         |-HSIEController → DB シーケンス図 -  フローチャート.pdf

↓

preprocessEvidence層 設計・実装 完了

　|-PreprocessEvidence層(フォルダ)
 
     |-Preprocessed Evidence詳細設計書
     
     |-Preprocessed Evidence JSON出力モデル
     
     |-Preprocessed Evidence＿assets
     
         |-Preprocessed Evidence コンポーネント図 -  フローチャート
         
         |-Preprocessed Evidence ER図 
         
↓

Analysis層設計・実装（S完全構築完了）

　|-Analysis層(フォルダ)

     |-Analysis詳細設計書

     |-Structure（フォルダ）

         |-Structure Aggression Analyzer  詳細設計書  

         |-assets(フォルダ)
         
         　　　|-Structure Aggression Analyzer クラス図 
            
            　|-Structure Aggression Analyzer シーケンス図 
     
     |-Language（フォルダ）

          |-Structure Aggression Analyzer  詳細設計書  
          
          |-assets(フォルダ)
         
         　　　|-Language クラス図 
            
            　|-Language シーケンス図 

             
      |-Analysis Score（フォルダ）

          |-Analysis Score 詳細設計書  

↓

|-　HSIResult層(フォルダ)

     |-HSIResult詳細設計書

↓

|-LegalRetrieval層(フォルダ)

     |-LegalRetrieval詳細設計書 


実装済みプログラム内容：
HSIEフォルダ内

EntoryPoint：音声入力 → ASR → Evidence(JSON) 

↓

PreprocessedEvidence：話者分離・波形生成(現在はオフ)・ASR後処理(誤字修正ロジック)

↓

Analysis：

  言語攻撃性ロジック：
  　独自AIモデルによる７指標評価(直接的侮辱・婉曲的侮辱・責任転嫁・拒否不能命令・人格否定・能力否定・価値否定)
   
   　30秒ごとスコアリング
   
   　総合スコアリング

  会話構造性ロジック：
  
  　ターン占有率算出
   
   会話構造否定度算出

   割り込み度算出

   反転ロジック可否算出

   独自シグモンドで活性化

   180秒窓算出

   統合スコアリング

  Analysis Score統合：ロジック：
  
   コンディション算出
   
   エビデンス算出

   コンディションにおけるスコア統合

↓

HSIResult：

　エビデンス変換

 算出理由エビデンス生成
 
 クエリ生成

 人間説明用サマリー生成

↓

LegalRetrieval：

 法律タグ生成

 e-Govによる法令検索

 採択法令決定

 法令エビデンスマッチング生成

↓

API化

 

エンジン一貫しての生成までの End-to-End 実行確認済み

fainal_evidence/JSONに全ての実行結果及び過程とそのタグを記録・保存済み

Evidence は immutable なスナップショットとして保存



🔵 今後改良予定

language独自AIモデルの特化モデルの生成・データの拡充

ASR精度の向上

Analysis別指標の生成

🧠 Architectural Philosophy

EntryPoint 層は **「事実の収集のみ」**を行う

分析・判断・解釈は一切行わない

各層は immutable な Evidence を生成し、前段の Evidence を破壊しない

再現性・監査可能性を最重要視

🚧 Notes

話者識別（speaker diarization）は EntryPoint 層では行いません

speaker_id は前処理層にて再付与されています

