"""Ollama LLMクライアント実装."""

from typing import Final

import requests

from hsie.llm.base import LLMClient


class OllamaLLMClient(LLMClient):
    """
    Ollama経由でローカルLLMを呼び出すクライアント。

    責務:
        - Ollama APIへのHTTPリクエスト送信
        - レスポンスからテキスト抽出

    制約:
        - 同期呼び出しのみ
        - streaming禁止
        - async禁止
        - retry禁止
        - logging禁止
        - print禁止
        - 戻り値は必ずstr（Noneは返さない）

    使用例:
        >>> client = OllamaLLMClient()
        >>> response = client.generate("Hello, world!")
    """

    def __init__(
        self,
        model_name: str = "qwen2.5:3b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.0,
        timeout: float = 120.0,
    ) -> None:
        """
        Ollama LLMクライアントを初期化する。

        Args:
            model_name: Ollamaで使用するモデル名
            base_url: Ollama APIのベースURL
            temperature: 生成時の温度パラメータ
            timeout: HTTPリクエストのタイムアウト秒数
        """
        self._model_name: Final[str] = model_name
        self._base_url: Final[str] = base_url
        self._temperature: Final[float] = temperature
        self._timeout: Final[float] = timeout

    def generate(self, prompt: str) -> str:
        """
        プロンプトからテキストを生成する。

        Ollama APIのPOST /api/generateエンドポイントを呼び出し、
        生成されたテキストを返す。

        Args:
            prompt: LLMに渡すプロンプト文字列

        Returns:
            str: LLMが生成したテキスト（前後の空白を除去）

        Raises:
            RuntimeError: HTTPステータスコードが200以外の場合
            ValueError: レスポンスに"response"キーが無い場合、
                       または空文字列の場合
        """
        url: str = f"{self._base_url}/api/generate"

        payload: dict = {
            "model": self._model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self._temperature,
            },
        }

        response: requests.Response = requests.post(
            url,
            json=payload,
            timeout=self._timeout,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Ollama API returned status code {response.status_code}: "
                f"{response.text}"
            )

        data: dict = response.json()

        if "response" not in data:
            raise ValueError("Ollama response does not contain 'response' key")

        result: str = data["response"].strip()

        if result == "":
            raise ValueError("Ollama returned empty response")

        return result
