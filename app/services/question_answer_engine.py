from app.models.application_question import ApplicationQuestion
from anthropic import Anthropic
from app.config import ANTHROPIC_API_KEY


async def generate_question_answer(
    job_application_id: str, question: str
) -> ApplicationQuestion:
    """
    Generate an AI answer to an application question.
    """

    if ANTHROPIC_API_KEY:
        try:
            client = Anthropic(api_key=ANTHROPIC_API_KEY)

            prompt = f"""You are helping someone answer a job application question. 
Provide a thoughtful, professional answer.

Question: {question}

Provide a clear, concise answer that would be appropriate for a job application.
Keep it to 2-3 paragraphs."""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            answer = message.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            answer = f"AI generated answer for question: {question}"
    else:
        answer = f"AI generated answer for question: {question}\n\nNote: Set ANTHROPIC_API_KEY for AI-generated content."

    return ApplicationQuestion(
        job_application_id=job_application_id,
        question=question,
        answer=answer,
        ai_generated=True,
    )
