from fastapi import HTTPException, status


class AudioAnalysisException(HTTPException):
    """Raised when audio analysis fails for an uploaded file."""

    def __init__(self, filename: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to analyze audio file: {filename}",
        )


class InvalidAudioFileException(HTTPException):
    def __init__(self, filename: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format: {filename}",
        )


class FileTooLargeException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Uploaded file exceeds maximum allowed size.",
        )
