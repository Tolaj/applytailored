import os
import anthropic
from typing import Optional, Dict, Any
import json


class ClaudeAIService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"

    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze job description to extract key information
        """
        prompt = f"""Analyze the following job description and extract structured information.
Return your response in JSON format with these fields:
- company_name: string
- position_title: string
- required_skills: list of strings
- preferred_skills: list of strings
- experience_level: string (entry/mid/senior)
- key_responsibilities: list of strings
- keywords: list of important keywords for ATS

Job Description:
{job_description}

Return only valid JSON, no markdown or additional text."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text

        # Try to parse JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = (
                    response_text.split("```json")[1].split("```")[0].strip()
                )
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "company_name": "Unknown",
                "position_title": "Unknown",
                "required_skills": [],
                "preferred_skills": [],
                "experience_level": "unknown",
                "key_responsibilities": [],
                "keywords": [],
            }

    def tailor_resume(
        self,
        base_resume_latex: str,
        job_description: str,
        job_analysis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Tailor a LaTeX resume to match a job description
        """
        analysis_context = ""
        if job_analysis:
            analysis_context = f"""
Job Analysis:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
- Required Skills: {', '.join(job_analysis.get('required_skills', []))}
- Key Responsibilities: {', '.join(job_analysis.get('key_responsibilities', []))}
- Keywords for ATS: {', '.join(job_analysis.get('keywords', []))}
"""

        prompt = f"""You are an expert resume writer. Your task is to tailor the following LaTeX resume to match the job description below.

IMPORTANT GUIDELINES:
1. Preserve ALL LaTeX formatting, commands, and structure
2. Keep the same document class and packages
3. Maintain professional tone and formatting
4. Optimize for ATS (Applicant Tracking Systems) by including relevant keywords naturally
5. Emphasize experiences and skills that match the job requirements
6. Reorder or rephrase bullet points to highlight relevant achievements
7. Quantify achievements where possible
8. Ensure all LaTeX syntax is valid and compilable
9. Do NOT add fictional experience or skills - only optimize what exists
10. Return ONLY the modified LaTeX code, no explanations or markdown

{analysis_context}

Job Description:
{job_description}

Base Resume (LaTeX):
{base_resume_latex}

Return the tailored LaTeX resume:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        tailored_latex = message.content[0].text

        # Clean up response - remove markdown code blocks if present
        if "```latex" in tailored_latex:
            tailored_latex = tailored_latex.split("```latex")[1].split("```")[0].strip()
        elif "```tex" in tailored_latex:
            tailored_latex = tailored_latex.split("```tex")[1].split("```")[0].strip()
        elif "```" in tailored_latex:
            # Generic code block
            tailored_latex = tailored_latex.split("```")[1].split("```")[0].strip()

        return tailored_latex

    def generate_cover_letter(
        self,
        resume_text: str,
        job_description: str,
        job_analysis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a tailored cover letter
        """
        analysis_context = ""
        if job_analysis:
            analysis_context = f"""
Job Details:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
"""

        prompt = f"""Write a professional cover letter for the following job application.

{analysis_context}

Job Description:
{job_description}

Candidate's Resume/Background:
{resume_text}

Guidelines:
1. Keep it concise (3-4 paragraphs)
2. Show enthusiasm and cultural fit
3. Highlight 2-3 key achievements relevant to the role
4. Demonstrate understanding of the company/role
5. Include a clear call to action
6. Use professional but warm tone
7. Avoid generic phrases

Return only the cover letter text:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text
