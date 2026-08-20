from typing import Type, TypeVar

from google import genai
from pydantic import BaseModel

from app.config import GEMINI_API_KEY, GEMINI_MODEL


T = TypeVar("T", bound=BaseModel)


class LLMService:

    def __init__(self):
        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )
        self.model = GEMINI_MODEL

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config={
                "system_instruction": system_prompt,
            },
        )

        return response.text

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
    ) -> T:

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config={
                "system_instruction": system_prompt,
                "response_mime_type": "application/json",
                "response_schema": response_model,
            },
        )

        return response_model.model_validate_json(
            response.text
        )