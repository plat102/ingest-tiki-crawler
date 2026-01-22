from bs4 import BeautifulSoup

def clean_html_text(html: str) -> str:
    """
    Remove HTML tags
    """
    if not html:
        return ""
    try:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator='\n')
        return '\n'.join([line.strip() for line in text.splitlines() if line.strip()])
    except Exception:
        return str(html)
