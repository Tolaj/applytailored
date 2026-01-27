from app.models.generated_asset import GeneratedAsset
from anthropic import Anthropic
from app.config import ANTHROPIC_API_KEY


async def generate_cover_letter(
    job_application_id: str, user_id: str, job_description: str
) -> GeneratedAsset:
    """
    Generate a tailored cover letter using Claude AI.
    """

    if ANTHROPIC_API_KEY:
        try:
            client = Anthropic(api_key=ANTHROPIC_API_KEY)

            prompt = f"""Write a professional cover letter for this job:

Job Description:
{job_description}

Create a compelling cover letter that:
1. Shows enthusiasm for the position
2. Highlights relevant skills and experience
3. Demonstrates knowledge of the role requirements
4. Is concise and professional (3-4 paragraphs)

Format it as a formal business letter."""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            content = message.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            content = f"Tailored cover letter for job app {job_application_id}"
    else:
        content = f"Tailored cover letter for job app {job_application_id}\n\nNote: Set ANTHROPIC_API_KEY for AI-generated content."

    return GeneratedAsset(
        job_application_id=job_application_id,
        user_id=user_id,
        type="cover_letter",
        title="Cover Letter",
        content_text=content,
        ai_model="claude-sonnet-4-20250514",
    )
