import re

class Product:
    def sanitize_html(self, html: str) -> str:
        return re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL)
