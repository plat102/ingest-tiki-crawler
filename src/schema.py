from typing import Optional, Any, List

from pydantic import BaseModel, Field, field_validator
from bs4 import BeautifulSoup

class Product(BaseModel):
    id: int
    name: str
    url_key: Optional[str] = ''
    price: float = Field(default=0.0)

    # Process description
    description: Optional[str] = Field(default='')
    @field_validator('description', mode='before')
    @classmethod
    def clean_html(cls, value: Any) -> str:
        if not value:
            return ''
        try:
            soup = BeautifulSoup(str(value), "html.parser")
            txt = soup.get_text(separator='\n')
            lines = [line.strip()
                     for line in txt.splitlines()
                     if line.strip()]
            cleaned_lines = '\n'.join(lines)

            return cleaned_lines

        except Exception:
            return str(value)

    # Process images
    image_urls: List[str] = Field(default_factory=list)

    @field_validator('image_urls', mode='before')
    @classmethod
    def extract_image_urls(cls, value: Any) -> List[str]:
        if not value:
            return []
        if isinstance(value, list):
            return [
                img.get('base_url')
                for img in value
                if img.get('base_url')
            ]
        return []
