from app.application.use_cases.track.dto import TrackResponse
from app.domain.repositories.track_repository import TrackRepository


class ListTracksUseCase:
    def __init__(self, repository: TrackRepository) -> None:
        self._repository = repository

    def execute(self) -> list[TrackResponse]:
        return [
            TrackResponse.from_entity(track) for track in self._repository.find_all()
        ]
