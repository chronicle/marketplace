from ..core.product import Product

class ScriptSession:
    def __init__(self, product: Product):
        self.product = product

    def sanitize_html(self, request: dict) -> dict:
        html = request.get("html", "")
        cleaned = self.product.sanitize_html(html)
        return {"result": cleaned}
