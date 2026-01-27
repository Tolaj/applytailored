from app.models.generated_asset import GeneratedAsset
from anthropic import Anthropic
from app.config import ANTHROPIC_API_KEY
import app.database as database


async def generate_cold_email(job_application_id: str, user_id: str) -> GeneratedAsset:
    """Generate a cold email for networking/outreach."""
    db = database.db
    job_app = await db.job_applications.find_one({"_id": job_application_id})

    if ANTHROPIC_API_KEY and job_app:
        try:
            client = Anthropic(api_key=ANTHROPIC_API_KEY)

            prompt = f"""Write a professional cold email for networking purposes.

Company: {job_app.get('company_name', 'the company')}
Position: {job_app.get('job_title', 'the position')}

The email should:
1. Be concise and respectful of the recipient's time
2. Express genuine interest in the company and role
3. Request a brief informational conversation
4. Be friendly but professional
5. Be no more than 3-4 short paragraphs

Do not include [Your Name] or placeholders - just write the email body."""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            content = message.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            content = f"Cold email for job app {job_application_id}"
    else:
        content = f"Cold email for job app {job_application_id}\n\nNote: Set ANTHROPIC_API_KEY for AI-generated content."

    return GeneratedAsset(
        job_application_id=job_application_id,
        user_id=user_id,
        type="cold_email",
        title="Cold Email",
        content_text=content,
        ai_model="claude-sonnet-4-20250514",
    )
