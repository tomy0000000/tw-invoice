class APIError(Exception):
    """Base class for all API errors."""

    def __init__(self, code: int, message: str, *args: object) -> None:
        super().__init__(*args)
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"<{self.code}> {self.message}"
