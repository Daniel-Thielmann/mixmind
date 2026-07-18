from app.application.use_cases.track.dto import TrackResponse
from app.core.exceptions import NotFoundError
from app.domain.repositories.track_repository import TrackRepository
from app.domain.value_objects.identifiers import TrackId


class GetTrackUseCase:
    def __init__(self, repository: TrackRepository) -> None:
        self._repository = repository

    def execute(self, track_id: TrackId) -> TrackResponse:
        track = self._repository.find_by_id(track_id)
        if track is None:
            raise NotFoundError(f"Track '{track_id}' not found")
        return TrackResponse.from_entity(track)
