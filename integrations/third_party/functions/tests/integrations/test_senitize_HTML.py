from ..core.product import Product
from ..core.session import ScriptSession

def test_sanitize_html_removes_script():
    product = Product()
    session = ScriptSession(product)

    request = {
        "html": "<b>Hello</b><script>alert('x')</script>"
    }

    response = session.sanitize_html(request)

    print("Sanitized HTML:", response["result"])

    assert "<script>" not in response["result"]
    assert response["result"] == "<b>Hello</b>"
