"""
Enhanced Section Preferences Controller with Hierarchical Selection
Supports: Section -> Subsection -> Item selection
"""

from flask import request, jsonify, g, render_template
from bson.objectid import ObjectId
from datetime import datetime
from db import db
import subprocess
import tempfile
from bs4 import BeautifulSoup
import sys
import os

# Add parent directory to path to import enhanced parser
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.latex_parser_service import EnhancedLatexParser
from services.latex_service import LatexService


latex_parser = EnhancedLatexParser()
latex_service = LatexService()


def view_section_preferences(resume_id):
    """View and manage section preferences"""
    resume = db.base_resumes.find_one(
        {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]}
    )

    if not resume:
        return "Resume not found", 404

    return render_template(
        "resume/section_preferences.html", resume=resume, resume_id=str(resume["_id"])
    )


def load_resume_structure(resume_id):
    """
    Parse resume and return hierarchical structure

    Returns JSON with sections -> subsections -> items
    """
    try:
        # Get resume
        resume = db.base_resumes.find_one(
            {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]}
        )

        if not resume:
            return jsonify({"success": False, "error": "Resume not found"}), 404

        # Read LaTeX file
        latex_content = latex_service.read_base_resume(resume["latex_template_path"])

        if not latex_content:
            return (
                jsonify({"success": False, "error": "Could not read resume file"}),
                404,
            )

        # Parse into hierarchical structure
        parsed = latex_parser.parse_resume_to_hierarchy(latex_content)

        # Serialize for JSON
        structure = latex_parser.serialize_structure(parsed)

        # Cache in database
        db.base_resumes.update_one(
            {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]},
            {
                "$set": {
                    "section_preferences.parsed_structure": structure,
                    "section_preferences.last_parsed": datetime.utcnow(),
                }
            },
        )

        return jsonify(
            {
                "success": True,
                "structure": structure,
                "header": parsed["header"],
            }
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


def save_section_preferences(resume_id):
    """
    Save hierarchical section preferences

    Expected format from frontend:
    {
        "enabled": true,
        "sections": {
            "experience": {
                "selected": true,
                "subsections": {
                    "experience_0": {
                        "selected": false,
                        "items": ["item_0_0", "item_0_1"]
                    }
                }
            }
        }
    }
    """
    try:
        import json

        data = request.json

        enabled = data.get("enabled", False)
        sections = data.get("sections", [])

        print("\n=== SAVE SECTION PREFERENCES DEBUG ===")
        print(f"Resume ID: {resume_id}")
        print(f"Enabled: {enabled}")
        print(f"Sections received: {json.dumps(sections, indent=2)}")

        # Validate and clean the structure
        cleaned_sections = []
        total_selected_items = 0
        total_selected_subsections = 0

        for section in sections:
            section_id = section.get("section_id")
            section_type = section.get("section_type", "unknown")
            section_title = section.get("title", "Unknown")
            section_selected = section.get("selected", True)
            subsections = section.get("subsections", [])

            cleaned_subsections = []

            for subsection in subsections:
                sub_id = subsection.get("id")
                sub_title = subsection.get("title", "Untitled")
                sub_selected = subsection.get("selected", True)
                items = subsection.get("items", [])

                if sub_selected or items:
                    cleaned_subsections.append(
                        {
                            "id": sub_id,
                            "title": sub_title,
                            "selected": sub_selected,
                            "items": items,
                        }
                    )

                    if sub_selected:
                        total_selected_subsections += 1
                    total_selected_items += len(items)

            if cleaned_subsections:
                cleaned_sections.append(
                    {
                        "section_id": section_id,
                        "section_type": section_type,
                        "title": section_title,
                        "selected": section_selected,
                        "subsections": cleaned_subsections,
                    }
                )

        print(f"\n=== FINAL CLEANED STRUCTURE ===")
        print(f"Total sections: {len(cleaned_sections)}")
        print(f"Total subsections: {total_selected_subsections}")
        print(f"Total items: {total_selected_items}")
        print(f"Cleaned sections: {json.dumps(cleaned_sections, indent=2)}")

        # Update database
        result = db.base_resumes.update_one(
            {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]},
            {
                "$set": {
                    "section_preferences.enabled": enabled,
                    "section_preferences.sections": cleaned_sections,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        print(
            f"Database update result: matched={result.matched_count}, modified={result.modified_count}"
        )

        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Resume not found"}), 404

        return jsonify(
            {
                "success": True,
                "message": "Section preferences saved",
                "enabled": enabled,
                "total_items_selected": total_selected_items,
                "total_subsections_selected": total_selected_subsections,
                "sections_selected": len(cleaned_sections),
            }
        )

    except Exception as e:
        import traceback

        print("\n=== ERROR in save_section_preferences ===")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


def get_section_preferences(resume_id):
    """Get saved section preferences"""
    try:
        resume = db.base_resumes.find_one(
            {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]},
            {"section_preferences": 1},
        )

        if not resume:
            return jsonify({"success": False, "error": "Resume not found"}), 404

        preferences = resume.get(
            "section_preferences",
            {
                "enabled": False,
                "sections": {},
                "parsed_structure": None,
            },
        )

        return jsonify({"success": True, "preferences": preferences})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def latex_to_html(latex_code):
    """Convert LaTeX to HTML using pandoc"""
    with tempfile.NamedTemporaryFile(
        suffix=".tex", mode="w", delete=False
    ) as texfile, tempfile.NamedTemporaryFile(
        suffix=".html", mode="w", delete=False
    ) as htmlfile:

        texfile.write(latex_code)
        texfile.flush()

        try:
            subprocess.run(
                [
                    "pandoc",
                    texfile.name,
                    "--from=latex",
                    "--to=html",
                    "--mathjax",
                    "-o",
                    htmlfile.name,
                ],
                check=True,
                capture_output=True,
            )

            with open(htmlfile.name, "r") as f:
                return f.read()
        except subprocess.CalledProcessError as e:
            print(f"Pandoc error: {e.stderr}")
            return None
        except FileNotFoundError:
            print("Pandoc not found. Install: sudo apt-get install pandoc")
            return None
        finally:
            # Clean up temp files
            try:
                os.unlink(texfile.name)
                os.unlink(htmlfile.name)
            except:
                pass


def latex_to_html_with_flex(latex_code):
    html_body = latex_to_html(latex_code)
    soup = BeautifulSoup(html_body, "html.parser")

    # Find all tables
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue

        wrapper = soup.new_tag("div", **{"class": "resume-subheading-wrapper"})

        for row in rows:
            tds = row.find_all("td")
            if len(tds) != 2:
                continue

            # create flex container for this row
            row_div = soup.new_tag("div", **{"class": "resume-subheading"})

            left = soup.new_tag("div", **{"class": "job-title"})
            # force the job title to italic instead of bold
            for content in tds[0].contents:
                if isinstance(content, str):
                    i_tag = soup.new_tag("i")
                    i_tag.string = content
                    left.append(i_tag)
                else:
                    left.append(content)

            right = soup.new_tag("div", **{"class": "company-location"})
            for content in tds[1].contents:
                right.append(content)

            row_div.append(left)
            row_div.append(right)

            wrapper.append(row_div)

        # Replace the table in the tree safely
        if table.parent:
            table.replace_with(wrapper)

    return str(soup)


def get_resume_html_preview(resume_id):
    """Get HTML preview with hierarchical structure annotations"""
    try:
        resume = db.base_resumes.find_one(
            {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]}
        )

        if not resume:
            return jsonify({"success": False, "error": "Resume not found"}), 404

        # Read LaTeX
        latex_path = f"storage/base_resumes/{resume['latex_template_path']}"

        try:
            with open(latex_path, "r", encoding="utf-8") as f:
                latex_content = f.read()
        except FileNotFoundError:
            return jsonify({"success": False, "error": "Resume file not found"}), 404

        # Convert to HTML
        html_content = latex_to_html_with_flex(latex_content)

        if not html_content:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Failed to convert LaTeX to HTML. Install pandoc: sudo apt-get install pandoc",
                    }
                ),
                500,
            )

        # Parse hierarchical structure
        parsed = latex_parser.parse_resume_to_hierarchy(latex_content)
        structure = latex_parser.serialize_structure(parsed)

        return jsonify(
            {
                "success": True,
                "html": html_content,
                "structure": structure,  # Send structure for proper ID mapping
            }
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# Keep old function name for compatibility
def load_resume_sections(resume_id):
    """Alias for backward compatibility"""
    return load_resume_structure(resume_id)
