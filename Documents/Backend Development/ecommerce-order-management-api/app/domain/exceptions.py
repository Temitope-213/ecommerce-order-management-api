class EmailAlreadyExistsError(Exception):
    """Raised when an email is already registered."""


class InvalidCredentialsError(Exception):
    """Raised when the email or password is wrong."""