class ServiceException(Exception):
    def __init__(self, msg: str) -> None:
        self.message = msg
        super().__init__(self.message)


class MultipleActionsFound(ServiceException):
    pass
