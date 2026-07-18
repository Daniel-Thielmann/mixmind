from app.application.use_cases.track.dto import CreateTrackRequest, TrackResponse
from app.domain.entities.track import Track
from app.domain.repositories.track_repository import TrackRepository
from app.domain.value_objects.bpm import BPM
from app.domain.value_objects.camelot_key import CamelotKey
from app.domain.value_objects.duration import Duration
from app.domain.value_objects.energy import Energy


class CreateTrackUseCase:
    def __init__(self, repository: TrackRepository) -> None:
        self._repository = repository

    def execute(self, request: CreateTrackRequest) -> TrackResponse:
        track = Track(
            filename=request.filename,
            duration=Duration(request.duration)
            if request.duration is not None
            else None,
            bpm=BPM(request.bpm) if request.bpm is not None else None,
            energy=Energy(request.energy) if request.energy is not None else None,
            key=request.key,
            camelot=CamelotKey(request.camelot) if request.camelot else None,
            sample_rate=request.sample_rate,
        )
        self._repository.save(track)
        return TrackResponse.from_entity(track)
