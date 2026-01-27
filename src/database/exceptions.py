"""
References: https://www.psycopg.org/docs/errors.html
"""

from src.exceptions import TikiError

class DatabaseError(TikiError):
    """Base class for database exceptions."""
    pass

class DBConnectionError(DatabaseError):
    """Db connection error. (network, authentication)
        Transient -> retry
    """
    pass

class DBConstraintError(DatabaseError):
    """
        Dup ID, invalid values
        Permanent -> non-retry
    """
    pass

class DBOperationError(DatabaseError):
    """
        Syntax error
        Permanent -> non-retry (need code fixes)
    """
    pass
