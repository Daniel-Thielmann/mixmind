from app.application.use_cases.track.dto import TrackResponse, UpdateTrackRequest
from app.core.exceptions import NotFoundError
from app.domain.repositories.track_repository import TrackRepository
from app.domain.value_objects.bpm import BPM
from app.domain.value_objects.camelot_key import CamelotKey
from app.domain.value_objects.duration import Duration
from app.domain.value_objects.energy import Energy
from app.domain.value_objects.identifiers import TrackId


class UpdateTrackUseCase:
    def __init__(self, repository: TrackRepository) -> None:
        self._repository = repository

    def execute(self, track_id: TrackId, request: UpdateTrackRequest) -> TrackResponse:
        track = self._repository.find_by_id(track_id)
        if track is None:
            raise NotFoundError(f"Track '{track_id}' not found")

        changes = request.model_dump(exclude_unset=True)
        if "filename" in changes:
            track.filename = changes["filename"]
        if "duration" in changes:
            track.duration = Duration(changes["duration"])
        if "bpm" in changes:
            track.bpm = BPM(changes["bpm"])
        if "energy" in changes:
            track.energy = Energy(changes["energy"])
        if "key" in changes:
            track.key = changes["key"]
        if "camelot" in changes:
            track.camelot = (
                CamelotKey(changes["camelot"]) if changes["camelot"] else None
            )
        if "sample_rate" in changes:
            track.sample_rate = changes["sample_rate"]

        self._repository.update(track)
        return TrackResponse.from_entity(track)
