
class TikiError(Exception):
    """Project base exception."""
    def __init__(self, message, original_exception=None, data=None):
        super().__init__(message)
        self.original_exception = original_exception
        self.data = data

    def __str__(self):
        msg = self.message
        if self.original_exception:
            msg += f' | Original Exception: {type(self.original_exception).__name__}: {self.original_exception}'
        if self.data:
            msg += f' | Context data: {self.data}'
        return msg
