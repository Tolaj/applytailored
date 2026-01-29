"""
LaTeX Parser Service - Extract structured content from LaTeX resume templates
FIXED VERSION: Properly handles section comment boundaries
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ResumeSection:
    """Represents a section in the resume"""

    section_type: (
        str  # 'heading', 'experience', 'education', 'skills', 'projects', etc.
    )
    title: str  # Section title
    content: str  # Raw LaTeX content
    start_pos: int  # Position in original document
    end_pos: int  # End position
    subsections: List["ResumeSubsection"] = None

    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []


@dataclass
class ResumeSubsection:
    """Represents a subsection (like individual job, education entry, etc.)"""

    title: str  # e.g., "Senior Software Engineer at Tech Company"
    content: str  # Raw LaTeX content
    lines: List[str]  # Individual bullet points/lines
    start_pos: int
    end_pos: int


class LatexParserService:
    """Parse LaTeX resumes to extract structured content"""

    # Common section headers to look for
    SECTION_PATTERNS = {
        "experience": r"\\section\{.*?(?:experience|employment|work history).*?\}",
        "education": r"\\section\{.*?education.*?\}",
        "skills": r"\\section\{.*?(?:skills|technical skills|competencies).*?\}",
        "projects": r"\\section\{.*?projects.*?\}",
        "summary": r"\\section\{.*?(?:summary|profile|objective).*?\}",
        "certifications": r"\\section\{.*?(?:certifications?|licenses?).*?\}",
        "publications": r"\\section\{.*?publications?.*?\}",
    }

    def parse_resume(self, latex_content: str) -> Dict[str, Any]:
        """
        Parse LaTeX resume into structured sections

        Returns:
            {
                'header': {...},
                'sections': [ResumeSection, ...],
                'raw_content': str
            }
        """
        result = {
            "header": self._extract_header(latex_content),
            "sections": [],
            "raw_content": latex_content,
        }

        # Find all sections
        sections = self._find_sections(latex_content)

        for section_info in sections:
            section = self._parse_section(
                latex_content,
                section_info["type"],
                section_info["title"],
                section_info["start"],
                section_info["end"],
            )
            result["sections"].append(section)

        return result

    def _extract_header(self, latex_content: str) -> Dict[str, str]:
        """Extract resume header information (name, contact, etc.)"""
        header = {"content": "", "name": "", "email": "", "phone": "", "location": ""}

        # Find content before first \section
        section_match = re.search(r"\\section\{", latex_content, re.IGNORECASE)
        if section_match:
            header_content = latex_content[: section_match.start()]
        else:
            # If no sections, take content after \begin{document}
            begin_doc = re.search(r"\\begin\{document\}", latex_content)
            if begin_doc:
                header_content = latex_content[begin_doc.end() :]
            else:
                header_content = latex_content[:500]  # First 500 chars as fallback

        header["content"] = header_content.strip()

        # Try to extract name (usually in \textbf{\Large ...} or similar)
        name_patterns = [
            r"\\textbf\{\\(?:Large|LARGE|huge|Huge)\s+([^}]+)\}",
            r"\\(?:Large|LARGE|huge|Huge)\s+\\textbf\{([^}]+)\}",
            r"\\(?:Large|LARGE)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, header_content)
            if match:
                header["name"] = match.group(1).strip()
                break

        # Extract email
        email_match = re.search(
            r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", header_content
        )
        if email_match:
            header["email"] = email_match.group(1)

        # Extract phone
        phone_match = re.search(
            r"(\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})", header_content
        )
        if phone_match:
            header["phone"] = phone_match.group(1)

        return header

    def _find_sections(self, latex_content: str) -> List[Dict[str, Any]]:
        """Find all section boundaries in the document"""
        sections = []

        # Find all \section{...} commands
        section_matches = list(
            re.finditer(r"\\section\{([^}]+)\}", latex_content, re.IGNORECASE)
        )

        for i, match in enumerate(section_matches):
            section_title = match.group(1)
            start_pos = match.start()

            # Find the comment that precedes this section (if any)
            # Look backward to find %-----------SECTION_NAME-----------
            before_section = latex_content[max(0, start_pos - 200) : start_pos]
            comment_match = re.search(
                r"(%-+[A-Z\s]+-+\n)(?=\s*\\section)", before_section
            )

            if comment_match:
                # Adjust start_pos to include the comment
                comment_offset = len(before_section) - len(
                    before_section[comment_match.start() :]
                )
                start_pos = max(0, start_pos - 200) + comment_match.start()

            # End is either just before the next section's comment or the next section
            if i + 1 < len(section_matches):
                next_section_pos = section_matches[i + 1].start()

                # Look backward from next section to find its comment header
                # Pattern: %-----------SECTION_NAME-----------
                search_start = max(start_pos, next_section_pos - 200)
                before_next = latex_content[search_start:next_section_pos]

                # Find section comment patterns
                # Look for patterns like: %-----------EXPERIENCE----------- or %------EXPERIENCE------
                comment_pattern = r"\n(%-+[A-Z\s]+-+)\n"
                comment_matches = list(re.finditer(comment_pattern, before_next))

                if comment_matches:
                    # End just before the last comment found (which belongs to next section)
                    last_comment = comment_matches[-1]
                    end_pos = (
                        search_start + last_comment.start() + 1
                    )  # +1 to keep the first newline
                else:
                    # No comment found, end just before next section
                    end_pos = next_section_pos
            else:
                # Last section - find \end{document} or use end of content
                end_doc = re.search(r"\\end\{document\}", latex_content[start_pos:])
                if end_doc:
                    end_pos = start_pos + end_doc.start()
                else:
                    end_pos = len(latex_content)

            # Determine section type
            section_type = self._classify_section(section_title)

            sections.append(
                {
                    "type": section_type,
                    "title": section_title,
                    "start": start_pos,
                    "end": end_pos,
                }
            )

        return sections

    def _classify_section(self, section_title: str) -> str:
        """Classify section based on its title"""
        title_lower = section_title.lower()

        for section_type, pattern in self.SECTION_PATTERNS.items():
            if re.search(pattern, f"\\section{{{section_title}}}", re.IGNORECASE):
                return section_type

        # Default classification based on keywords
        if any(word in title_lower for word in ["experience", "work", "employment"]):
            return "experience"
        elif any(word in title_lower for word in ["education", "academic"]):
            return "education"
        elif any(word in title_lower for word in ["skill", "technical", "competenc"]):
            return "skills"
        elif "project" in title_lower:
            return "projects"
        elif any(word in title_lower for word in ["summary", "profile", "objective"]):
            return "summary"
        else:
            return "other"

    def _parse_section(
        self,
        full_content: str,
        section_type: str,
        section_title: str,
        start_pos: int,
        end_pos: int,
    ) -> ResumeSection:
        """Parse a section into structured content"""
        section_content = full_content[start_pos:end_pos]

        section = ResumeSection(
            section_type=section_type,
            title=section_title,
            content=section_content,
            start_pos=start_pos,
            end_pos=end_pos,
        )

        # Parse subsections (like individual jobs, education entries)
        if section_type in ["experience", "education", "projects"]:
            section.subsections = self._parse_subsections(section_content, start_pos)
        elif section_type == "skills":
            section.subsections = self._parse_skills(section_content, start_pos)

        return section

    def _parse_subsections(
        self, section_content: str, base_offset: int
    ) -> List[ResumeSubsection]:
        """Parse subsections like individual job entries"""
        subsections = []

        # Look for \resumeSubheading or similar commands
        patterns = [
            r"\\resumeSubheading\{([^}]+)\}\{([^}]+)\}\{([^}]+)\}\{([^}]+)\}",
            r"\\resumeSubSubheading\{([^}]+)\}\{([^}]+)\}",
            r"\\item\s+\\textbf\{([^}]+)\}",
        ]

        for pattern in patterns:
            matches = list(re.finditer(pattern, section_content))

            for i, match in enumerate(matches):
                # Extract title (usually first group)
                title = match.group(1)
                start = match.start()

                # Find the end of this subsection
                if i + 1 < len(matches):
                    end = matches[i + 1].start()
                else:
                    # Look for next major command or end of section
                    next_section = re.search(
                        r"\\(?:resumeSubHeadingListEnd|end\{itemize\})",
                        section_content[start:],
                    )
                    if next_section:
                        end = start + next_section.start()
                    else:
                        end = len(section_content)

                subsection_content = section_content[start:end]

                # Extract bullet points
                lines = self._extract_bullet_points(subsection_content)

                subsections.append(
                    ResumeSubsection(
                        title=title,
                        content=subsection_content,
                        lines=lines,
                        start_pos=base_offset + start,
                        end_pos=base_offset + end,
                    )
                )

            if subsections:  # If we found matches with this pattern, stop
                break

        return subsections

    def _parse_skills(
        self, section_content: str, base_offset: int
    ) -> List[ResumeSubsection]:
        """Parse skills section"""
        subsections = []

        # Look for \resumeSubItem or individual skill items
        skill_items = re.finditer(
            r"\\resumeSubItem\{([^}]+)\}\{([^}]+)\}", section_content
        )

        for i, match in enumerate(skill_items):
            title = match.group(1)
            content = match.group(2)

            subsections.append(
                ResumeSubsection(
                    title=title,
                    content=match.group(0),
                    lines=[content],
                    start_pos=base_offset + match.start(),
                    end_pos=base_offset + match.end(),
                )
            )

        return subsections

    def _extract_bullet_points(self, content: str) -> List[str]:
        """Extract individual bullet points from content"""
        lines = []

        # Look for \resumeItem{...}
        items = re.finditer(r"\\resumeItem\{([^}]+)\}", content)
        for item in items:
            lines.append(item.group(1))

        # Also look for plain \item commands
        if not lines:
            items = re.finditer(r"\\item\s+([^\n\\]+)", content)
            for item in items:
                lines.append(item.group(1).strip())

        return lines

    def rebuild_latex(
        self,
        original_content: str,
        parsed_structure: Dict[str, Any],
        selected_sections: Dict[str, bool],
        regenerated_sections: Dict[str, str],
    ) -> str:
        """
        Rebuild LaTeX with regenerated sections

        Args:
            original_content: Original LaTeX
            parsed_structure: Parsed structure from parse_resume()
            selected_sections: Dict of section_id -> True/False
            regenerated_sections: Dict of section_id -> new LaTeX content

        Returns:
            Updated LaTeX content
        """
        result = original_content

        # Replace sections from back to front to maintain positions
        sections_to_replace = []

        for section in parsed_structure["sections"]:
            section_id = f"{section.section_type}_{section.start_pos}"

            if section_id in regenerated_sections:
                sections_to_replace.append(
                    {
                        "start": section.start_pos,
                        "end": section.end_pos,
                        "new_content": regenerated_sections[section_id],
                    }
                )

        # Sort by start position (descending) to replace from back to front
        sections_to_replace.sort(key=lambda x: x["start"], reverse=True)

        for replacement in sections_to_replace:
            result = (
                result[: replacement["start"]]
                + replacement["new_content"]
                + result[replacement["end"] :]
            )

        return result

    def get_section_preview(self, section: ResumeSection, max_length: int = 200) -> str:
        """Get a readable preview of a section"""
        # Remove LaTeX commands for preview
        preview = re.sub(r"\\[a-zA-Z]+\*?\{([^}]*)\}", r"\1", section.content)
        preview = re.sub(r"\\[a-zA-Z]+\*?", "", preview)
        preview = preview.strip()

        if len(preview) > max_length:
            preview = preview[:max_length] + "..."

        return preview
