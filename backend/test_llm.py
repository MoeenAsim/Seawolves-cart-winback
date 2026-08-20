from app.services.llm_service import LLMService


llm = LLMService()


response = llm.generate(
    system_prompt=(
        "You are a concise technical assistant. "
        "Respond in one sentence."
    ),
    user_prompt=(
        "Confirm that the Gemini AI service "
        "is working for our cart win-back project."
    ),
)


print(response)