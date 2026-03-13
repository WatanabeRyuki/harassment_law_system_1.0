"""Passthrough LLM client that echoes ASR text as corrected (no external API)."""

import json

from hsie.llm.base import LLMClient


class PassthroughLLMClient(LLMClient):
    """
    LLM client that returns input utterances as-is for corrected_text.

    Used when running the pipeline without an external LLM (e.g. Ollama).
    Parses the prompt to extract the input JSON and returns the same
    structure with corrected_text set to the original text.
    """

    def generate(self, prompt: str) -> str:
        """
        Extract input utterances from prompt and return JSON array
        with corrected_text = text for each utterance.

        Args:
            prompt: Prompt containing "Input Utterances:" and a JSON array.

        Returns:
            JSON string: [{"utterance_id": "...", "corrected_text": "..."}, ...]

        Raises:
            ValueError: If the prompt does not contain valid input JSON.
        """
        lines = prompt.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(data, list):
                    continue
                out = []
                for item in data:
                    if isinstance(item, dict) and "utterance_id" in item:
                        text = item.get("text", "")
                        out.append({
                            "utterance_id": str(item["utterance_id"]),
                            "corrected_text": text if isinstance(text, str) else str(text),
                        })
                if len(out) == len(data):
                    return json.dumps(out, ensure_ascii=False)
        raise ValueError(
            "PassthroughLLMClient: could not find valid input JSON array in prompt"
        )
