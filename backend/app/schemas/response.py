from pydantic import BaseModel


class UploadedTrack(BaseModel):
    filename: str
    stored_as: str
    status: str


class UploadResponse(BaseModel):
    status: str
    message: str

    track_a: UploadedTrack
    track_b: UploadedTrack