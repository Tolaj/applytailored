"""Utility functions for escaping LaTeX special characters."""


def escape_latex(text: str) -> str:
    """
    Escape special LaTeX characters in a string.

    Args:
        text: The text to escape

    Returns:
        The escaped text safe for LaTeX
    """
    if not text:
        return ""

    # Define LaTeX special characters and their escaped versions
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "$": r"\$",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    # Apply replacements
    result = text
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)

    return result
