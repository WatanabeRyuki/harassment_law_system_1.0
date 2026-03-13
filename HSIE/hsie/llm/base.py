"""LLMクライアント抽象基底クラス."""

from abc import ABC, abstractmethod
from typing import Final


class LLMClient(ABC):
    """
    LLMクライアントの抽象基底クラス。

    責務:
        - LLM呼び出しのインターフェースを定義する
        - 同期的なテキスト生成APIを提供する

    制約:
        - 同期呼び出しのみ
        - streaming禁止
        - async禁止
        - retry禁止
        - 戻り値は必ずstr（Noneは返さない）
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        プロンプトからテキストを生成する。

        Args:
            prompt: LLMに渡すプロンプト文字列

        Returns:
            str: LLMが生成したテキスト（空文字列でない）

        Raises:
            RuntimeError: LLM呼び出しに失敗した場合
            ValueError: レスポンスが不正な場合
        """
        ...
