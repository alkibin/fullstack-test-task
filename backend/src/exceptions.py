class BaseError(Exception): # не зависит от Фастапишного http exception
    """Базовый класс для всех ошибок бизнес-логики."""


class NotFoundError(BaseError):
    """Базовый класс для ошибок сущность не найдена."""


class FileNotFoundError(NotFoundError):
    """Файл не найден."""

    def __init__(self, file_id: str):
        self.file_id = file_id
        super().__init__(f"File {file_id!r} not found")


class StoredFileMissingError(NotFoundError):
    """Запись в БД есть, а физического файла на диске нет (рассинхрон)."""

    def __init__(self, file_id: str):
        self.file_id = file_id
        super().__init__(f"Stored file for {file_id!r} not found on disk")


class EmptyFileError(BaseError):
    """Эксепшн о том что загружаемый файл пуст."""

    def __init__(self):
        super().__init__("Uploaded file is empty")


class FileAllreadyExists(BaseError):
    """Эксепшн о том что загружаемый файл уже существует."""

    def __init__(self):
        super().__init__("Uploaded file is allready exists")