import logging

from requests import Request
from starlette.responses import JSONResponse

import config_ini


class AppExceptionCase(Exception):
    def __init__(self, status_code: int, context: dict):
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.context = context
        self.log = logging.getLogger(config_ini.LOGGING_CONF)

    def __str__(self):
        return (
                f"<AppException {self.exception_case} - "
                + f"status_code={self.status_code} - context={self.context}>"
        )


async def app_exception_handler(request: Request, exc: AppExceptionCase):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "app_exception": exc.exception_case,
            "context": exc.context,
        },
    )


class AppException(AppExceptionCase):
    class BooksGetItem(AppExceptionCase):
        """
        Book with given ID not found.
        """

        def __init__(self, context: dict = None):
            super().__init__(
                status_code=404,
                context=context,
            )
            self.log.warning("Book with given ID not found.")

    class BookAddNewRequestError(AppExceptionCase):
        """
        Error in request to add new book.
        """

        def __init__(self, context: dict = None):
            super().__init__(
                status_code=400,
                context=context,
            )

    class BookAddNewNoDescription(AppExceptionCase):
        """
        No description in book.
        """

        def __init__(self, context: dict = None):
            super().__init__(
                status_code=400,
                context=context,
            )

    class BookAddNewDescriptionTooShort(AppExceptionCase):
        """
        Description too short.
        """

        def __init__(self, context: dict = None):
            super().__init__(
                status_code=400,
                context=context,
            )

    class BookAddNewDescriptionNotInEnglish(AppExceptionCase):
        """
        Description not in English.
        """

        def __init__(self, context: dict = None):
            super().__init__(
                status_code=400,
                context=context,
            )
