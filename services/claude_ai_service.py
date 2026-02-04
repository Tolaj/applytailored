"""
Enhanced Claude AI Service with hierarchical regeneration methods
Supports: Section, Subsection, and Bullet Point level regeneration
"""

import os
import anthropic
from typing import Optional, Dict, Any
import json


class ClaudeAIService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"

    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """Analyze job description to extract key information"""
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

        try:
            if "```json" in response_text:
                response_text = (
                    response_text.split("```json")[1].split("```")[0].strip()
                )
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "company_name": "Unknown",
                "position_title": "Unknown",
                "required_skills": [],
                "preferred_skills": [],
                "experience_level": "unknown",
                "key_responsibilities": [],
                "keywords": [],
            }

    def regenerate_bullet_point(
        self,
        bullet_content: str,
        job_description: str,
        job_analysis: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        """
        Regenerate a single bullet point to match job requirements

        Args:
            bullet_content: Original bullet point text
            job_description: Target job description
            job_analysis: Analyzed job information
            context: Additional context (section, subsection names)

        Returns:
            LaTeX code for regenerated bullet point
        """
        prompt = f"""You are an expert resume writer. Optimize this single bullet point to better match the job description.

Job Context:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
- Required Skills: {', '.join(job_analysis.get('required_skills', [])[:10])}
- Key ATS Keywords: {', '.join(job_analysis.get('keywords', [])[:15])}

Resume Context:
- Section: {context.get('section', 'Unknown')}
- Subsection: {context.get('subsection', 'Unknown')}

Original Bullet Point:
{bullet_content}

CRITICAL GUIDELINES:
1. Keep the same achievement/responsibility - DO NOT invent new ones
2. Emphasize aspects that match the job requirements
3. Include 1-2 ATS keywords naturally if relevant
4. Quantify impact if numbers already exist (don't add fake numbers)
5. Return ONLY the LaTeX code for this bullet point
6. Use \\resumeItemNH{{...}} format
7. Keep it concise (1-2 lines maximum)

Return the optimized bullet point in LaTeX:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        result = message.content[0].text

        # Clean up response
        if "```latex" in result:
            result = result.split("```latex")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()

        return result

    def regenerate_subsection(
        self,
        subsection_latex: str,
        section_type: str,
        job_description: str,
        job_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Regenerate an entire subsection (e.g., a job entry)

        Args:
            subsection_latex: Original LaTeX for the subsection
            section_type: Type of section (experience, education, etc.)
            job_description: Target job description
            job_analysis: Analyzed job information
            context: Additional context

        Returns:
            Regenerated LaTeX for the subsection
        """
        context = context or {}

        prompt = f"""You are an expert resume writer. Optimize this resume subsection to better match the job description.

Job Context:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
- Required Skills: {', '.join(job_analysis.get('required_skills', [])[:10])}
- Key Responsibilities: {', '.join(job_analysis.get('key_responsibilities', [])[:5])}
- ATS Keywords: {', '.join(job_analysis.get('keywords', [])[:15])}

Section Type: {section_type.upper()}
Subsection: {context.get('subsection_title', 'Unknown')}

Original LaTeX:
{subsection_latex}

CRITICAL GUIDELINES:
1. Preserve ALL LaTeX structure and commands EXACTLY
2. Keep job title, company, dates unchanged
3. ONLY optimize bullet points to emphasize relevant experience
4. Include ATS keywords naturally where appropriate
5. Reorder bullet points to put most relevant first
6. Quantify achievements if numbers already exist
7. Maintain professional tone
8. Return ONLY the LaTeX code, no explanations

Return the optimized subsection in LaTeX:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        result = message.content[0].text

        # Clean up response
        if "```latex" in result:
            result = result.split("```latex")[1].split("```")[0].strip()
        elif "```tex" in result:
            result = result.split("```tex")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()

        return result

    def regenerate_section(
        self,
        section_content: str,
        section_type: str,
        job_description: str,
        job_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Regenerate an entire section (kept for compatibility)
        """
        context = context or {}

        prompt = f"""You are an expert resume writer. Optimize this {section_type.upper()} section to match the job description.

Job Context:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
- Required Skills: {', '.join(job_analysis.get('required_skills', [])[:10])}
- ATS Keywords: {', '.join(job_analysis.get('keywords', [])[:15])}

Original {section_type.upper()} Section:
{section_content}

CRITICAL GUIDELINES:
1. Preserve ALL LaTeX formatting and structure
2. Maintain professional tone
3. Include ATS keywords naturally
4. Emphasize relevant experiences
5. Keep dates and factual information unchanged
6. Return ONLY LaTeX code

Return the optimized section:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        result = message.content[0].text

        if "```latex" in result:
            result = result.split("```latex")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()

        return result

    def tailor_resume(
        self,
        base_resume_latex: str,
        job_description: str,
        job_analysis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Full resume regeneration (original method)"""
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

        prompt = f"""You are an expert resume writer. Tailor this LaTeX resume to match the job description.

IMPORTANT GUIDELINES:
1. Preserve ALL LaTeX formatting and structure
2. Maintain professional tone
3. Optimize for ATS by including relevant keywords
4. Emphasize matching experiences and skills
5. Reorder/rephrase bullet points for relevance
6. Quantify achievements where possible
7. Ensure valid LaTeX syntax
8. DO NOT invent experience or skills
9. Return ONLY the LaTeX code

{analysis_context}

Job Description:
{job_description}

Base Resume:
{base_resume_latex}

Return the tailored LaTeX resume:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        tailored_latex = message.content[0].text

        if "```latex" in tailored_latex:
            tailored_latex = tailored_latex.split("```latex")[1].split("```")[0].strip()
        elif "```tex" in tailored_latex:
            tailored_latex = tailored_latex.split("```tex")[1].split("```")[0].strip()
        elif "```" in tailored_latex:
            tailored_latex = tailored_latex.split("```")[1].split("```")[0].strip()

        return tailored_latex

    def generate_cover_letter(
        self,
        resume_text: str,
        job_description: str,
        job_analysis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a tailored cover letter"""
        analysis_context = ""
        if job_analysis:
            analysis_context = f"""
Job Details:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
"""

        prompt = f"""Write a professional cover letter for this job application.

{analysis_context}

Job Description:
{job_description}

Candidate's Background:
{resume_text}

Guidelines:
1. Keep it concise (3-4 paragraphs)
2. Show enthusiasm and cultural fit
3. Highlight 2-3 key achievements relevant to the role
4. Demonstrate understanding of company/role
5. Include clear call to action
6. Professional but warm tone
7. Avoid generic phrases

Return only the cover letter text:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text
