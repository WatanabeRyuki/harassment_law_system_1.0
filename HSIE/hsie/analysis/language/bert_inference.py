# -*- coding: utf-8 -*-

"""
bert_inference.py

責務：
・BERTモデルによる推論のみ
・7指標（I_dir, I_ind, C_shift, C_block, D_p, D_a, D_v）を出力
・0〜100スケールで返却

禁止事項：
・ルール補正は禁止
・スコア解釈は禁止
・Evidence処理は禁止
"""

import torch
import torch.nn as nn
import os
from transformers import BertModel, BertConfig, AutoTokenizer

from .dto.bert_score_dto import BertScoreDTO


# =========================
# ■ モデル定義（学習時と完全一致）
# =========================
class BertForMultiLabel(nn.Module):
    def __init__(
        self,
        model_name: str | None = None,
        bert_config: BertConfig | None = None,
        num_labels: int = 7
    ):
        super().__init__()
        if bert_config is not None:
            self.bert = BertModel(bert_config)
        else:
            self.bert = BertModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_labels)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)

        # ★ 学習時と完全一致（重要）
        pooled = outputs.last_hidden_state[:, 0]
        pooled = self.dropout(pooled)

        logits = self.classifier(pooled)

        return logits


# =========================
# ■ グローバルロード（シングルトン）
# =========================
_MODEL = None
_TOKENIZER = None
_DEVICE = torch.device("cpu")  # Mac M2なら "mps" に変更可能


def _load_model():
    global _MODEL, _TOKENIZER

    if _MODEL is not None:
        return

    model_path = os.path.join(os.path.dirname(__file__), "hsie_core_v1.2")

    # tokenizer（学習時と一致）
    _TOKENIZER = AutoTokenizer.from_pretrained(model_path)

    # モデル初期化（ローカル完結）
    bert_config = BertConfig(
        vocab_size=len(_TOKENIZER),
        hidden_size=768,
        num_hidden_layers=12,
        num_attention_heads=12,
        intermediate_size=3072,
        max_position_embeddings=512,
        type_vocab_size=2,
    )
    _MODEL = BertForMultiLabel(bert_config=bert_config, num_labels=7)

    # 重みロード
    _MODEL.load_state_dict(
        torch.load(f"{model_path}/pytorch_model.bin", map_location=_DEVICE)
    )

    _MODEL.to(_DEVICE)
    _MODEL.eval()

    print("✅ HSIE BERTモデルロード完了")


# =========================
# ■ 入力構築（推論時はcontext不使用）
# =========================
def _build_input_text(utterance_text: str) -> str:
    """
    学習時の入力構造を維持しつつ、推論時はcontextを使わない。
    形式: [SEP]{text}[SEP]
    """
    text = utterance_text if utterance_text else ""
    return f"[SEP]{text}[SEP]"


# =========================
# ■ 推論メイン
# =========================
def run_bert(utterance) -> BertScoreDTO:
    """
    入力：
        LanguageUtterance（context_window含む）

    出力：
        BertScoreDTO（0〜100）
    """

    # モデルロード
    _load_model()

    # =========================
    # ■ 入力構築
    # =========================
    input_text = _build_input_text(getattr(utterance, "text", ""))

    inputs = _TOKENIZER(
        input_text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=256
    )

    inputs = {k: v.to(_DEVICE) for k, v in inputs.items()}

    # =========================
    # ■ 推論
    # =========================
    with torch.no_grad():
        logits = _MODEL(**inputs)

    # =========================
    # ■ sigmoid → 0〜100変換
    # =========================
    probs = torch.sigmoid(logits)[0].cpu().numpy() * 100

    # =========================
    # ■ DTO変換
    # =========================
    return BertScoreDTO(
        I_dir=float(probs[0]),
        I_ind=float(probs[1]),
        C_shift=float(probs[2]),
        C_block=float(probs[3]),
        D_p=float(probs[4]),
        D_a=float(probs[5]),
        D_v=float(probs[6]),
    )