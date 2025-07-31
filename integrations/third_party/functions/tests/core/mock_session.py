class MockSession:
    def __init__(self):
        self.request_history = []

    def create_request(self, parameters: dict):
        request = MockRequest(parameters)
        self.request_history.append(request)
        return request

class MockRequest:
    def __init__(self, parameters: dict):
        self.parameters = parameters
