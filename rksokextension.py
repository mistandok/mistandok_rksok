class NotSpecifiedIPOrPortError(Exception):
    """Error that occurs when there is not Server or Port
    specified in command-line arguments."""
    pass


class CanNotParseResponseError(Exception):
    """Error that occurs when we can not parse some strange
    response from RKSOK server."""
    pass

class CanNotParseRequestError(Exception):
    """Error that occurs when we can not parse some strange
    request from client."""
    pass

if __name__ == '__main__':
    pass