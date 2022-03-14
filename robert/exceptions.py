import typing as t


__all__ = [
    'RobertException',
    'DeciderException',
    'CacherExceptions',
    'EmptyCacheException'
]


class RobertException(Exception):
    def __init__(
            self, func_name: str, message: t.Union[str, Exception], *args, **kwargs
    ):
        self.__func_name = func_name
        self.__message = str(message)
        self.__args = args
        self.__kwargs = kwargs
        super().__init__(self.__message)

    def __str__(self):
        __str = f'"{self.__func_name}" -> {self.__message}'

        if self.__args:
            __str += f' | Args: {self.args}'
        if self.__kwargs:
            __str += f' | Kwargs: {self.__kwargs}'

        return __str


class DeciderException(RobertException):
    pass


class CacherExceptions(RobertException):
    pass


class EmptyCacheException(CacherExceptions):
    pass
