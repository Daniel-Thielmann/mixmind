from app.core.exceptions import NotFoundError
from app.domain.repositories.track_repository import TrackRepository
from app.domain.value_objects.identifiers import TrackId


class DeleteTrackUseCase:
    def __init__(self, repository: TrackRepository) -> None:
        self._repository = repository

    def execute(self, track_id: TrackId) -> None:
        if self._repository.find_by_id(track_id) is None:
            raise NotFoundError(f"Track '{track_id}' not found")
        self._repository.delete(track_id)
