"""ASR後処理ユースケース層."""

from typing import Final

from hsie.preprocessed_evidence.dto.asr import (
    ASRPostProcessInputDTO,
    ASRPostProcessOutputDTO,
)
from hsie.preprocessed_evidence.asr_postprocess.prompt import ASRPromptBuilder
from hsie.preprocessed_evidence.asr_postprocess.mapper import ASRResponseMapper
from hsie.llm.base import LLMClient


class ASRPostprocessService:
    """
    ASR後処理サービス。

    責務:
        - ASRPostProcessInputDTOを受け取る
        - PromptBuilderを呼び出しプロンプト生成
        - LLMClientを同期呼び出し
        - Mapperを呼び出しCorrectedDTO生成
        - ASRPostProcessOutputDTOを返却

    この層は純粋ユースケース層であり、
    データ加工・構造変更・推論ロジックは持たない。
    """

    def __init__(
        self,
        prompt_builder: ASRPromptBuilder,
        mapper: ASRResponseMapper,
        llm_client: LLMClient,
    ) -> None:
        """
        依存を注入する。

        Args:
            prompt_builder: プロンプト生成器
            mapper: レスポンスマッパー
            llm_client: LLMクライアント
        """
        self._prompt_builder: Final[ASRPromptBuilder] = prompt_builder
        self._mapper: Final[ASRResponseMapper] = mapper
        self._llm_client: Final[LLMClient] = llm_client

    def correct(
        self,
        input_dto: ASRPostProcessInputDTO,
    ) -> ASRPostProcessOutputDTO:
        """
        ASRテキスト補正を実行する。

        Args:
            input_dto: ASR後処理入力DTO

        Returns:
            ASRPostProcessOutputDTO: 補正済み発話を含む出力DTO

        Raises:
            ValueError: LLMがNoneを返した場合
        """
        prompt: str = self._prompt_builder.build(input_dto)

        response: str = self._llm_client.generate(prompt)

        if response is None:
            raise ValueError("LLM returned None response")

        output_dto: ASRPostProcessOutputDTO = self._mapper.to_output_dto(
            response=response,
            input_dto=input_dto,
        )

        return output_dto
