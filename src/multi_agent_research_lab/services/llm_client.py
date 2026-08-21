"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

import os
from dataclasses import dataclass

import openai


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client skeleton."""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        from multi_agent_research_lab.core.config import get_settings
        settings = get_settings()
        self.model_name = settings.openai_model or model_name
        api_key = settings.openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = openai.OpenAI(api_key=api_key)

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content
            usage = response.usage

            # gpt-4o-mini approx cost: $0.15/1M input, $0.60/1M output
            cost = 0.0
            if usage:
                cost = (usage.prompt_tokens / 1_000_000 * 0.15) + (
                    usage.completion_tokens / 1_000_000 * 0.6
                )

            return LLMResponse(
                content=content,
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                cost_usd=cost,
            )
        except Exception as e:
            # Handle or re-raise
            raise RuntimeError(f"LLM API Error: {str(e)}")
