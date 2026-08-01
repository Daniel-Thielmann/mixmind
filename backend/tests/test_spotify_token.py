from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.entities.spotify_connection import SpotifyConnection


class TestSpotifyConnectionExpiration:
    def test_token_far_from_expiry_not_expired(self) -> None:
        conn = SpotifyConnection(
            user_id="u1",
            spotify_user_id="s1",
            access_token="tok",
            refresh_token="ref",
            expires_at=int(time.time()) + 3600,
        )
        assert not conn.is_expired

    def test_token_within_safety_margin_triggers_refresh(self) -> None:
        conn = SpotifyConnection(
            user_id="u1",
            spotify_user_id="s1",
            access_token="tok",
            refresh_token="ref",
            expires_at=int(time.time()) + 60,
        )
        assert conn.is_expired

    def test_token_fresh_does_not_trigger_refresh(self) -> None:
        conn = SpotifyConnection(
            user_id="u1",
            spotify_user_id="s1",
            access_token="tok",
            refresh_token="ref",
            expires_at=int(time.time()) + 180,
        )
        assert not conn.is_expired

    def test_token_expired_when_well_past_expiry(self) -> None:
        conn = SpotifyConnection(
            user_id="u1",
            spotify_user_id="s1",
            access_token="tok",
            refresh_token="ref",
            expires_at=int(time.time()) - 3600,
        )
        assert conn.is_expired

    def test_token_expired_at_threshold_plus_one(self) -> None:
        conn = SpotifyConnection(
            user_id="u1",
            spotify_user_id="s1",
            access_token="tok",
            refresh_token="ref",
            expires_at=int(time.time()) + 121,
        )
        assert not conn.is_expired

    def test_token_expired_at_threshold_minus_one(self) -> None:
        conn = SpotifyConnection(
            user_id="u1",
            spotify_user_id="s1",
            access_token="tok",
            refresh_token="ref",
            expires_at=int(time.time()) + 119,
        )
        assert conn.is_expired

    def test_needs_reauthorization_true(self) -> None:
        conn = SpotifyConnection(
            user_id="u1",
            spotify_user_id="s1",
            access_token="tok",
            refresh_token="ref",
            status="reauthorization_required",
        )
        assert conn.needs_reauthorization

    def test_needs_reauthorization_false(self) -> None:
        conn = SpotifyConnection(
            user_id="u1",
            spotify_user_id="s1",
            access_token="tok",
            refresh_token="ref",
        )
        assert not conn.needs_reauthorization

    def test_scopes_list_splits_space_separated(self) -> None:
        conn = SpotifyConnection(
            user_id="u1",
            spotify_user_id="s1",
            access_token="tok",
            refresh_token="ref",
            scope="user-read-private user-library-read",
        )
        assert conn.scopes_list == ["user-read-private", "user-library-read"]


class TestRefreshTokenConcurrentRefresh:
    @pytest.mark.asyncio
    async def test_concurrent_refreshes_only_one_oauth_call(self) -> None:
        from app.application.use_cases.spotify.refresh_token import (
            RefreshSpotifyAccessTokenUseCase,
        )

        repo = MagicMock()
        repo.find_by_user_id = MagicMock(
            return_value=SpotifyConnection(
                user_id="u1",
                spotify_user_id="s1",
                access_token="old",
                refresh_token="ref",
                expires_at=int(time.time()) - 1,
            )
        )
        repo.save = MagicMock(
            return_value=SpotifyConnection(
                user_id="u1",
                spotify_user_id="s1",
                access_token="new",
                refresh_token="ref",
                expires_at=int(time.time()) + 3600,
            )
        )

        oauth = AsyncMock()
        oauth.refresh_access_token = AsyncMock(
            return_value=MagicMock(
                access_token="new",
                refresh_token=None,
                token_type="Bearer",
                scope="",
                expires_in=3600,
            )
        )

        use_case = RefreshSpotifyAccessTokenUseCase(oauth_client=oauth, repository=repo)

        async def run() -> None:
            await use_case.execute("u1")

        await asyncio.gather(run(), run(), run(), run())

        assert oauth.refresh_access_token.call_count == 1

    @pytest.mark.asyncio
    async def test_concurrent_refresh_returns_same_result(self) -> None:
        from app.application.use_cases.spotify.refresh_token import (
            RefreshSpotifyAccessTokenUseCase,
        )

        repo = MagicMock()
        repo.find_by_user_id = MagicMock(
            return_value=SpotifyConnection(
                user_id="u2",
                spotify_user_id="s2",
                access_token="old",
                refresh_token="ref",
                expires_at=int(time.time()) - 1,
            )
        )
        repo.save = MagicMock(
            return_value=SpotifyConnection(
                user_id="u2",
                spotify_user_id="s2",
                access_token="new",
                refresh_token="ref",
                expires_at=int(time.time()) + 3600,
            )
        )

        oauth = AsyncMock()
        oauth.refresh_access_token = AsyncMock(
            return_value=MagicMock(
                access_token="new",
                refresh_token=None,
                token_type="Bearer",
                scope="",
                expires_in=3600,
            )
        )

        use_case = RefreshSpotifyAccessTokenUseCase(oauth_client=oauth, repository=repo)

        async def run() -> SpotifyConnection | None:
            return await use_case.execute("u2")

        results = await asyncio.gather(run(), run(), run())
        tokens = [r.access_token if r else None for r in results]
        assert all(t == "new" for t in tokens)

    @pytest.mark.asyncio
    async def test_valid_token_skips_refresh(self) -> None:
        from app.application.use_cases.spotify.refresh_token import (
            RefreshSpotifyAccessTokenUseCase,
        )

        repo = MagicMock()
        repo.find_by_user_id = MagicMock(
            return_value=SpotifyConnection(
                user_id="u3",
                spotify_user_id="s3",
                access_token="valid",
                refresh_token="ref",
                expires_at=int(time.time()) + 3600,
            )
        )

        oauth = AsyncMock()
        use_case = RefreshSpotifyAccessTokenUseCase(oauth_client=oauth, repository=repo)
        result = await use_case.execute("u3")
        assert result is not None
        assert result.access_token == "valid"
        oauth.refresh_access_token.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_refresh_token_triggers_reauthorization(self) -> None:
        from app.application.use_cases.spotify.refresh_token import (
            RefreshSpotifyAccessTokenUseCase,
        )

        repo = MagicMock()
        repo.find_by_user_id = MagicMock(
            return_value=SpotifyConnection(
                user_id="u4",
                spotify_user_id="s4",
                access_token="old",
                refresh_token="",
                expires_at=int(time.time()) - 1,
            )
        )

        oauth = AsyncMock()
        use_case = RefreshSpotifyAccessTokenUseCase(oauth_client=oauth, repository=repo)
        result = await use_case.execute("u4")
        assert result is None
        repo.mark_reauthorization_required.assert_called_once_with("u4")

    @pytest.mark.asyncio
    async def test_different_users_get_separate_locks(self) -> None:
        from app.application.use_cases.spotify.refresh_token import (
            RefreshSpotifyAccessTokenUseCase,
        )

        repo = MagicMock()

        def make_find(uid: str, tok: str, exp: bool):
            return MagicMock(
                return_value=SpotifyConnection(
                    user_id=uid,
                    spotify_user_id=uid,
                    access_token=tok,
                    refresh_token="ref",
                    expires_at=int(time.time()) - (1 if exp else 3600),
                )
            )

        def make_save(uid: str, tok: str):
            return MagicMock(
                return_value=SpotifyConnection(
                    user_id=uid,
                    spotify_user_id=uid,
                    access_token=tok,
                    refresh_token="ref",
                    expires_at=int(time.time()) + 3600,
                )
            )

        repo.find_by_user_id = MagicMock(
            side_effect=lambda uid: SpotifyConnection(
                user_id=uid,
                spotify_user_id=uid,
                access_token="old",
                refresh_token="ref",
                expires_at=int(time.time()) - 1,
            )
        )
        repo.save = MagicMock(
            side_effect=lambda conn: SpotifyConnection(
                user_id=conn.user_id,
                spotify_user_id=conn.spotify_user_id,
                access_token="new",
                refresh_token="ref",
                expires_at=int(time.time()) + 3600,
            )
        )

        oauth = AsyncMock()
        oauth.refresh_access_token = AsyncMock(
            return_value=MagicMock(
                access_token="new",
                refresh_token=None,
                token_type="Bearer",
                scope="",
                expires_in=3600,
            )
        )

        use_case = RefreshSpotifyAccessTokenUseCase(oauth_client=oauth, repository=repo)

        async def run_user(uid: str) -> None:
            await use_case.execute(uid)

        await asyncio.gather(run_user("u5"), run_user("u6"))

        assert oauth.refresh_access_token.call_count == 2


class TestSpotifyOAuthReturnDestination:
    def test_signed_state_preserves_internal_return_destination(self) -> None:
        from types import SimpleNamespace
        from unittest.mock import MagicMock

        from app.application.use_cases.spotify.state_service import SpotifyStateService

        repository = MagicMock()
        repository.find_oauth_state.return_value = SimpleNamespace(
            consumed=False,
            expires_at=int(time.time()) + 600,
            user_id="user-1",
        )
        repository.consume_oauth_state.return_value = True
        service = SpotifyStateService(repository=repository)

        state = service.create_state("user-1", "/analyzer?source=spotify")
        context = service.validate_and_consume_state(state)

        assert context == ("user-1", "/analyzer?source=spotify")
        repository.create_oauth_state.assert_called_once()
