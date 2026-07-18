from uuid import UUID

from fastapi import APIRouter, Response, status

from app.api.dependencies import TrackRepositoryDependency
from app.application.use_cases.track.create.use_case import CreateTrackUseCase
from app.application.use_cases.track.delete.use_case import DeleteTrackUseCase
from app.application.use_cases.track.dto import (
    CreateTrackRequest,
    TrackResponse,
    UpdateTrackRequest,
)
from app.application.use_cases.track.get.use_case import GetTrackUseCase
from app.application.use_cases.track.list.use_case import ListTracksUseCase
from app.application.use_cases.track.update.use_case import UpdateTrackUseCase
from app.domain.value_objects.identifiers import TrackId

router = APIRouter()


def _track_id(value: UUID) -> TrackId:
    return TrackId(value=value.hex)


@router.post("", response_model=TrackResponse, status_code=status.HTTP_201_CREATED)
def create_track(
    request: CreateTrackRequest,
    repository: TrackRepositoryDependency,
) -> TrackResponse:
    return CreateTrackUseCase(repository).execute(request)


@router.get("", response_model=list[TrackResponse])
def list_tracks(repository: TrackRepositoryDependency) -> list[TrackResponse]:
    return ListTracksUseCase(repository).execute()


@router.get("/{track_id}", response_model=TrackResponse)
def get_track(track_id: UUID, repository: TrackRepositoryDependency) -> TrackResponse:
    return GetTrackUseCase(repository).execute(_track_id(track_id))


@router.patch("/{track_id}", response_model=TrackResponse)
def update_track(
    track_id: UUID,
    request: UpdateTrackRequest,
    repository: TrackRepositoryDependency,
) -> TrackResponse:
    return UpdateTrackUseCase(repository).execute(_track_id(track_id), request)


@router.delete("/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_track(track_id: UUID, repository: TrackRepositoryDependency) -> Response:
    DeleteTrackUseCase(repository).execute(_track_id(track_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
