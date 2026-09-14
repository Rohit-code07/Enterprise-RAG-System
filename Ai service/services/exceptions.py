class LLMProviderError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class LLMRateLimitError(LLMProviderError):
    def __init__(self, message: str = "LLM API rate limit exceeded. Please wait a moment and try again."):
        super().__init__(message, status_code=429)

class LLMNotFoundError(LLMProviderError):
    def __init__(self, message: str = "The configured LLM model was not found or is no longer available."):
        super().__init__(message, status_code=503)

class LLMAuthenticationError(LLMProviderError):
    def __init__(self, message: str = "LLM API authentication failed. Please check your API keys."):
        super().__init__(message, status_code=401)
