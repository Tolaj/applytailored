import subprocess
import os


def compile_tex_to_pdf(tex_path: str) -> str:
    """
    Compile a LaTeX file to PDF.
    Requires pdflatex to be installed on the system.
    """
    if not os.path.exists(tex_path):
        raise FileNotFoundError(f"LaTeX file not found: {tex_path}")

    cwd = os.path.dirname(tex_path)

    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_path],
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise Exception(f"PDF compilation failed: {e}")
    except FileNotFoundError:
        raise Exception(
            "pdflatex not found. Please install TeX distribution (e.g., TeX Live, MiKTeX)"
        )

    pdf_path = tex_path.replace(".tex", ".pdf")

    if not os.path.exists(pdf_path):
        raise Exception("PDF compilation produced no output file")

    return pdf_path
