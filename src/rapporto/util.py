def sanitize_title(title: str) -> str:
    """
    Strip characters that are unfortunate in Markdown link titles.
    """
    return title.replace("[", "").replace("]", "")


def goosefeet(text: str) -> str:
    """
    Parameters including spaces need to be treated specially for the GitHub API.
    """
    if " " in text:
        return f'"{text}"'
    return text
