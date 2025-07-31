from ..core.mock_session import MockSession
from ..core.product import MockProduct

class TestSession(MockSession):
    def __init__(self):
        super().__init__()
        self.product = MockProduct()
