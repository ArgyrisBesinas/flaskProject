class GetRequestError(Exception):
    """Response code not 200"""
    pass


class RequestFailedError(Exception):
    """Response code not 200"""
    pass


class JsonDecodeError(Exception):
    """Json decode error"""
    pass


class InvalidJupyterNotebookError(Exception):
    """Json missing following keys: """
    pass


class MySqlError(Exception):
    """MySQL Error"""
    pass
