from pydantic import BaseModel


class ApiResponse(BaseModel):
    """Generic API response envelope."""

    status: str
    message: str


class UploadedTrack(BaseModel):
    """Metadata for an uploaded track."""

    filename: str
    stored_as: str
    status: str


class UploadAnalysisResponse(ApiResponse):
    """Response returned after uploading the two tracks."""

    track_a: UploadedTrack
    track_b: UploadedTrack
