from app.models.generated_asset import GeneratedAsset
from anthropic import Anthropic
from app.config import ANTHROPIC_API_KEY
import os


async def generate_resume(
    job_application_id: str, user_id: str, job_description: str
) -> GeneratedAsset:
    """
    Generate a tailored resume using Claude AI.

    This is a placeholder implementation. In production, you would:
    1. Fetch user's base resume from database
    2. Parse the job description
    3. Call Claude API to generate tailored content
    4. Compile to PDF if needed
    """

    if ANTHROPIC_API_KEY:
        try:
            client = Anthropic(api_key=ANTHROPIC_API_KEY)

            prompt = f"""Generate a professional resume summary tailored for this job description:

Job Description:
{job_description}

Create a compelling summary that highlights relevant skills and experience for this position. 
Keep it concise and professional (3-4 sentences)."""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            content = message.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            content = f"Tailored resume for job app {job_application_id}\n\nJob Description Summary:\n{job_description[:200]}..."
    else:
        content = f"Tailored resume for job app {job_application_id}\n\nNote: Set ANTHROPIC_API_KEY for AI-generated content."

    return GeneratedAsset(
        job_application_id=job_application_id,
        user_id=user_id,
        type="resume",
        title="Tailored Resume",
        content_text=content,
        ai_model="claude-sonnet-4-20250514",
    )
