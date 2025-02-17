def sanitize_title(title: str) -> str:
    return title.replace("[", "").replace("]", "")
