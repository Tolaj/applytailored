import os
import subprocess
from pathlib import Path
from typing import Tuple, Optional


class LatexService:
    def __init__(self, storage_path: str = "storage"):
        self.storage_path = Path(storage_path)
        self.generated_path = self.storage_path / "generated"
        self.base_resumes_path = self.storage_path / "base_resumes"

        # Ensure directories exist
        self.generated_path.mkdir(parents=True, exist_ok=True)
        self.base_resumes_path.mkdir(parents=True, exist_ok=True)

    def compile_latex(
        self, tex_content: str, output_filename: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Compile LaTeX content to PDF

        Returns:
            Tuple of (success: bool, pdf_path: str|None, error_message: str|None)
        """
        # Create unique temporary file path
        tex_path = self.generated_path / f"{output_filename}.tex"
        pdf_path = self.generated_path / f"{output_filename}.pdf"

        try:
            # Write LaTeX content to file
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_content)

            # Compile with pdflatex
            # Run twice to resolve references
            for _ in range(2):
                result = subprocess.run(
                    [
                        "pdflatex",
                        "-interaction=nonstopmode",
                        "-output-directory",
                        str(self.generated_path),
                        str(tex_path),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

            # Check if PDF was generated
            if pdf_path.exists():
                # Clean up auxiliary files
                self._cleanup_aux_files(output_filename)
                return True, str(pdf_path), None
            else:
                error_msg = result.stderr if result.stderr else "PDF generation failed"
                return False, None, error_msg

        except subprocess.TimeoutExpired:
            return False, None, "LaTeX compilation timeout"
        except Exception as e:
            return False, None, f"Compilation error: {str(e)}"

    def _cleanup_aux_files(self, base_filename: str):
        """Remove auxiliary LaTeX files"""
        aux_extensions = [".aux", ".log", ".out", ".toc"]
        for ext in aux_extensions:
            aux_file = self.generated_path / f"{base_filename}{ext}"
            if aux_file.exists():
                try:
                    aux_file.unlink()
                except:
                    pass

    def read_base_resume(self, latex_template_path: str) -> Optional[str]:
        """Read base resume template from storage"""
        try:
            full_path = self.base_resumes_path / latex_template_path
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error reading base resume: {e}")
            return None

    def save_base_resume(self, content: str, filename: str) -> str:
        """Save a base resume template"""
        file_path = self.base_resumes_path / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return filename

    def extract_text_from_latex(self, latex_content: str) -> str:
        """
        Extract plain text from LaTeX (rough approximation)
        For better results, compile to PDF and extract from PDF
        """
        import re

        # Remove comments
        text = re.sub(r"%.*", "", latex_content)

        # Remove common LaTeX commands but keep their content
        text = re.sub(r"\\[a-zA-Z]+\*?\{([^}]*)\}", r"\1", text)
        text = re.sub(r"\\[a-zA-Z]+\*?", "", text)

        # Remove special characters
        text = text.replace("\\\\", "\n")
        text = text.replace("~", " ")
        text = text.replace("&", " ")

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n\s*\n", "\n\n", text)

        return text.strip()
