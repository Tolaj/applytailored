import re
from dataclasses import dataclass
from typing import List
import uuid


# -------------------------
# Data Model
# -------------------------


@dataclass
class ResumeSection:
    id: str
    section_type: str
    title: str
    subsections: list  # list of dicts: {"id", "title", "selected", "items"}
    raw_content: str


# -------------------------
# Core Parser
# -------------------------


class UniversalLatexResumeParser:
    """
    Core parser for LaTeX resumes.
    Converts LaTeX into a hierarchy of sections -> subsections -> items.
    """

    def __init__(self, latex_source: str):
        self.latex_source = latex_source

    def parse_resume_to_hierarchy(self) -> List[ResumeSection]:
        sections: List[ResumeSection] = []

        # Remove comments
        latex = re.sub(r"%.*", "", self.latex_source)

        # Extract document body
        doc_match = re.search(
            r"\\begin\{document\}(.*?)\\end\{document\}", latex, re.DOTALL
        )
        if not doc_match:
            raise ValueError("No document environment found in LaTeX.")
        content = doc_match.group(1)

        # Find all sections
        section_regex = re.compile(
            r"\\section\{(?P<title>[^}]+)\}(?P<content>.*?)(?=\\section\{|\\end\{document\}|\Z)",
            re.DOTALL,
        )

        for idx, sec_match in enumerate(section_regex.finditer(content)):
            title = sec_match.group("title").strip()
            sec_content = sec_match.group("content").strip()
            section_id = f"{title.lower().replace(' ', '_')}_{idx}"

            # Parse subsections
            subsections = self._parse_subsections(sec_content)

            sections.append(
                ResumeSection(
                    id=section_id,
                    section_type=title.lower(),
                    title=title,
                    subsections=subsections,
                    raw_content=sec_content,
                )
            )

        return sections

    def _parse_subsections(self, sec_content: str) -> list:
        import uuid

        subsections = []

        # 1️⃣ Parse subheadings (like Work Experience, Education)
        subheading_pattern = re.compile(
            r"\\resumeSubheading\s*"
            r"\{(?P<title>[^\}]*)\}\s*"
            r"\{[^\}]*\}\s*"
            r"\{[^\}]*\}\s*"
            r"\{[^\}]*\}\s*"
            r"(?P<content>.*?)(?=\\resumeSubheading|\\resumeSubHeadingListEnd|$)",
            re.DOTALL,
        )

        for sh_match in subheading_pattern.finditer(sec_content):
            sh_title = sh_match.group("title").strip()
            sh_content = sh_match.group("content").strip()
            items = self._parse_items(sh_content)
            subsection_id = (
                f"{sh_title.lower().replace(' ', '_')}_{uuid.uuid4().hex[:6]}"
            )

            subsections.append(
                {
                    "id": subsection_id,
                    "title": sh_title,
                    "selected": True,
                    "items": items if items else ["(No items)"],
                }
            )

        # 2️⃣ Parse bullet items (\resumeSubItem) if no subheadings found
        if not subsections:
            bullet_pattern = re.compile(
                r"\\resumeSubItem\s*\{(?P<title>[^\}]*)\}\s*\{(?P<content>.*?)\}",
                re.DOTALL,
            )
            for b_match in bullet_pattern.finditer(sec_content):
                bullet_title = b_match.group("title").strip()
                bullet_content = b_match.group("content").strip()
                subsection_id = (
                    f"{bullet_title.lower().replace(' ', '_')}_{uuid.uuid4().hex[:6]}"
                )

                subsections.append(
                    {
                        "id": subsection_id,
                        "title": bullet_title,
                        "selected": True,
                        "items": [bullet_content] if bullet_content else ["(No items)"],
                    }
                )

        # 3️⃣ If still empty, add placeholder
        if not subsections:
            subsections.append(
                {
                    "id": f"placeholder_{uuid.uuid4().hex[:6]}",
                    "title": "(No subsection)",
                    "selected": True,
                    "items": ["(No items)"],
                }
            )

        return subsections

    def _parse_items(self, sh_content: str) -> list:
        items = []

        # Check for resumeItemListStart ... resumeItemListEnd
        list_match = re.search(
            r"\\resumeItemListStart(.*?)\\resumeItemListEnd", sh_content, re.DOTALL
        )
        if list_match:
            block = list_match.group(1)
            item_pattern = re.compile(
                r"\\resumeItem(?:NH)?{(?:[^}]*)}{(?P<content>[^}]*)}", re.DOTALL
            )
            items.extend(
                [m.group("content").strip() for m in item_pattern.finditer(block)]
            )

        # If no items found, check for standalone resumeItemNH
        if not items:
            nh_pattern = re.compile(r"\\resumeItemNH{(?P<content>[^}]*)}", re.DOTALL)
            items.extend(
                [m.group("content").strip() for m in nh_pattern.finditer(sh_content)]
            )

        return items


# -------------------------
# App-facing parser
# -------------------------


class EnhancedLatexParser:
    """
    Backward-compatible parser for controllers.
    - Can be initialized with no arguments
    - LaTeX passed at parse time
    """

    def __init__(self):
        pass

    def parse_resume_to_hierarchy(self, latex_source: str) -> List[ResumeSection]:
        parser = UniversalLatexResumeParser(latex_source)
        return parser.parse_resume_to_hierarchy()

    def serialize_structure(self, sections: List[ResumeSection]) -> list:
        """
        Converts parsed ResumeSection objects into JSON-serializable list.
        Compatible with section_preferences structure.
        """
        serialized = []

        for section in sections:
            serialized.append(
                {
                    "section_id": section.id,
                    "section_type": section.section_type,
                    "title": section.title,
                    "selected": True,
                    "subsections": section.subsections,
                    "raw_content": section.raw_content,
                }
            )

        return serialized
