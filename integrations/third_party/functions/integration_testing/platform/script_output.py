# integration_testing/platform/script_output.py

class MockResults:
    def __init__(self):
        self.output_message = ""
        self.result_value = None
        self.execution_state = None
        self.json_output = []


class MockActionOutput:
    def __init__(self):
        self.results = MockResults()
