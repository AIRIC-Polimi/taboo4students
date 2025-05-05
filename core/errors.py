class AgentError(Exception):
    def __init__(self, message: str, original_error: Exception):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class GuesserError(Exception):
    def __init__(self, message: str, original_error: Exception):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)
