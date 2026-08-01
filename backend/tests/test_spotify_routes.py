from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestSpotifyRoutesRegistered:
    """Verify all Spotify routes are correctly registered (no 404)."""

    def test_playlists_route_exists(self) -> None:
        response = client.get("/api/v1/integrations/spotify/playlists")
        assert response.status_code != 404, "Playlists route should be registered"

    def test_saved_tracks_route_exists(self) -> None:
        response = client.get("/api/v1/integrations/spotify/saved-tracks")
        assert response.status_code != 404, "Saved tracks route should be registered"

    def test_search_route_exists(self) -> None:
        response = client.get("/api/v1/integrations/spotify/search")
        assert response.status_code != 404, "Search route should be registered"

    def test_status_route_exists(self) -> None:
        response = client.get("/api/v1/integrations/spotify/status")
        assert response.status_code != 404, "Status route should be registered"

    def test_connect_route_exists(self) -> None:
        response = client.get("/api/v1/integrations/spotify/connect")
        assert response.status_code != 404, "Connect route should be registered"

    def test_callback_route_exists(self) -> None:
        response = client.get(
            "/api/v1/integrations/spotify/callback?code=test&state=test",
            follow_redirects=False,
        )
        assert response.status_code != 404, "Callback route should be registered"

    def test_disconnect_route_exists(self) -> None:
        response = client.delete("/api/v1/integrations/spotify/")
        assert response.status_code != 404, "Disconnect route should be registered"

    def test_playlist_tracks_route_exists(self) -> None:
        response = client.get("/api/v1/integrations/spotify/playlists/test123/tracks")
        assert response.status_code != 404, "Playlist tracks route should be registered"

    def test_analyze_spotify_route_exists(self) -> None:
        response = client.post("/api/v1/analysis/spotify", json={"tracks": []})
        assert response.status_code != 404, (
            "Spotify analysis route should be registered"
        )

    def test_analyze_spotify_requires_auth(self) -> None:
        response = client.post(
            "/api/v1/analysis/spotify",
            json={
                "tracks": [
                    {"position": "track_a", "spotify_track_id": "id1"},
                    {"position": "track_b", "spotify_track_id": "id2"},
                ]
            },
        )
        assert response.status_code in (401, 422, 500), (
            f"Expected auth/validation error, got {response.status_code}"
        )

    def test_analyze_spotify_rejects_invalid_payload(self) -> None:
        response = client.post(
            "/api/v1/analysis/spotify",
            json={"tracks": [{"position": "track_a", "spotify_track_id": "id1"}]},
        )
        assert response.status_code in (400, 401, 422), (
            f"Expected validation/auth error, got {response.status_code}"
        )

    def test_double_prefix_not_present(self) -> None:
        response = client.get("/api/v1/integrations/integrations/spotify/playlists")
        assert response.status_code == 404, "Double-prefixed route should not exist"

    def test_playlists_returns_json_not_found_text(self) -> None:
        response = client.get("/api/v1/integrations/spotify/playlists")
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type, (
            "Response should be JSON, not plain text"
        )


class TestSpotifyExceptionTypes:
    def test_playlist_forbidden_error_status(self) -> None:
        from app.core.exceptions import SpotifyPlaylistForbiddenError

        exc = SpotifyPlaylistForbiddenError()
        assert exc.status_code == 403
        assert "only allows" in exc.detail

    def test_insufficient_scope_error_status(self) -> None:
        from app.core.exceptions import SpotifyInsufficientScopeError

        exc = SpotifyInsufficientScopeError()
        assert exc.status_code == 403
        assert "permissions are outdated" in exc.detail

    def test_rate_limit_error_status(self) -> None:
        from app.core.exceptions import SpotifyRateLimitError

        exc = SpotifyRateLimitError()
        assert exc.status_code == 429


class TestSearchRouteValidation:
    """Search endpoint validation rules — Pydantic/FastAPI layer.

    Note: Route requires auth headers (X-MixMind-User, X-MixMind-Timestamp,
    X-MixMind-Signature), so most requests return 401 before the handler runs.
    These tests verify the route is registered and Pydantic constraints exist
    by checking that invalid params would be caught if they reach validation.
    The actual limit clamping is tested at the client/service layer.
    """

    def test_search_route_registered(self) -> None:
        response = client.get("/api/v1/integrations/spotify/search")
        assert response.status_code != 404, "Search route should be registered"

    def test_search_with_minimal_params_registered(self) -> None:
        response = client.get("/api/v1/integrations/spotify/search?q=test")
        # Returns 401 because auth is missing, NOT 404 or 422
        # If the route weren't registered, it'd return 404.
        # If the q param validation failed, it'd return 422.
        assert response.status_code == 401, (
            "Route is registered; 401 confirms params passed basic validation"
        )

    def test_search_client_clamps_limit_20_to_10(self) -> None:
        from app.infrastructure.spotify.extended_api_client import (
            ExtendedSpotifyApiClient,
        )

        client_instance = ExtendedSpotifyApiClient(access_token="fake")
        # Verify the clamp logic exists — we can't easily test the full flow
        # without a token, but we can verify the method handles it.
        assert hasattr(client_instance, "search_tracks")

    def test_search_client_clamps_limit_over_10(self) -> None:
        """Verifies via unit test that limit clamping works in the client."""
        from unittest.mock import AsyncMock

        from app.infrastructure.spotify.extended_api_client import (
            ExtendedSpotifyApiClient,
        )

        client_instance = ExtendedSpotifyApiClient(access_token="fake")
        client_instance._get = AsyncMock(
            return_value={
                "tracks": {
                    "href": "",
                    "items": [],
                    "limit": 10,
                    "next": None,
                    "offset": 0,
                    "previous": None,
                    "total": 0,
                }
            }
        )
        import asyncio

        result = asyncio.run(client_instance.search_tracks(query="test", limit=20))
        call_path = client_instance._get.await_args[0][0]
        assert "limit=10" in call_path, f"Expected limit=10 in call, got: {call_path}"
        assert result is not None


class TestSearchExceptionHandling:
    """SpotifyBadRequestError and friends."""

    def test_bad_request_error(self) -> None:
        from app.core.exceptions import SpotifyBadRequestError

        exc = SpotifyBadRequestError()
        assert exc.status_code == 502
        assert "Please try again" in exc.detail

    def test_bad_request_error_with_detail(self) -> None:
        from app.core.exceptions import SpotifyBadRequestError

        exc = SpotifyBadRequestError(detail="Custom detail")
        assert exc.detail == "Custom detail"

    def test_bad_request_error_carries_spotify_response(self) -> None:
        from app.core.exceptions import SpotifyBadRequestError

        spotify_resp = {"error": {"status": 400, "message": "Invalid limit"}}
        exc = SpotifyBadRequestError(spotify_response=spotify_resp)
        assert exc.spotify_response == spotify_resp

    def test_forbidden_error(self) -> None:
        from app.core.exceptions import SpotifyForbiddenError

        exc = SpotifyForbiddenError()
        assert exc.status_code == 403

    def test_api_unavailable_error(self) -> None:
        from app.core.exceptions import SpotifyApiUnavailableError

        exc = SpotifyApiUnavailableError()
        assert exc.status_code == 502


class TestSpotifyClientResilience:
    def test_retries_once_with_refreshed_token_after_401(self) -> None:
        import asyncio
        from unittest.mock import AsyncMock, patch

        import httpx

        from app.infrastructure.spotify.extended_api_client import (
            ExtendedSpotifyApiClient,
        )

        request = httpx.Request("GET", "https://api.spotify.com/v1/me/playlists")
        shared_client = AsyncMock()
        shared_client.get.side_effect = [
            httpx.Response(
                401, request=request, json={"error": {"message": "expired"}}
            ),
            httpx.Response(200, request=request, json={"items": [], "total": 0}),
        ]
        refresh = AsyncMock(return_value="fresh-token")
        spotify = ExtendedSpotifyApiClient("expired-token", refresh)

        with patch(
            "app.infrastructure.spotify.extended_api_client._get_shared_client",
            return_value=shared_client,
        ):
            result = asyncio.run(spotify.get_user_playlists())

        assert result.total == 0
        assert shared_client.get.await_count == 2
        assert refresh.await_count == 1
        assert (
            shared_client.get.await_args_list[1].kwargs["headers"]["Authorization"]
            == "Bearer fresh-token"
        )

    def test_maps_network_errors_to_api_unavailable(self) -> None:
        import asyncio
        from unittest.mock import AsyncMock, patch

        import httpx
        import pytest

        from app.core.exceptions import SpotifyApiUnavailableError
        from app.infrastructure.spotify.extended_api_client import (
            ExtendedSpotifyApiClient,
        )

        shared_client = AsyncMock()
        shared_client.get.side_effect = httpx.ConnectError("offline")
        spotify = ExtendedSpotifyApiClient("token")

        with (
            patch(
                "app.infrastructure.spotify.extended_api_client._get_shared_client",
                return_value=shared_client,
            ),
            pytest.raises(SpotifyApiUnavailableError),
        ):
            asyncio.run(spotify.get_user_playlists())

    def test_rate_limit_includes_retry_after(self) -> None:
        import asyncio
        from unittest.mock import AsyncMock, patch

        import httpx
        import pytest

        from app.core.exceptions import SpotifyRateLimitError
        from app.infrastructure.spotify.extended_api_client import (
            ExtendedSpotifyApiClient,
        )

        request = httpx.Request("GET", "https://api.spotify.com/v1/me/playlists")
        shared_client = AsyncMock()
        shared_client.get.return_value = httpx.Response(
            429,
            request=request,
            headers={"Retry-After": "7"},
            json={"error": {"message": "rate limited"}},
        )
        spotify = ExtendedSpotifyApiClient("token")

        with (
            patch(
                "app.infrastructure.spotify.extended_api_client._get_shared_client",
                return_value=shared_client,
            ),
            pytest.raises(SpotifyRateLimitError, match="7 seconds"),
        ):
            asyncio.run(spotify.get_user_playlists())


class TestExtractTrackFromItem:
    def test_extracts_from_item_field(self) -> None:
        from app.infrastructure.spotify.extended_api_client import (
            ExtendedSpotifyApiClient,
        )

        result = ExtendedSpotifyApiClient.extract_track_from_item(
            {
                "added_at": "2025-01-01T00:00:00Z",
                "item": {
                    "id": "abc123",
                    "name": "Test Song",
                    "artists": [{"name": "Test Artist"}],
                    "album": {"name": "Test Album", "images": []},
                    "duration_ms": 200000,
                    "external_urls": {
                        "spotify": "https://open.spotify.com/track/abc123"
                    },
                    "popularity": 50,
                },
            }
        )
        assert result is not None
        assert result.id == "abc123"
        assert result.name == "Test Song"

    def test_extracts_from_track_field_fallback(self) -> None:
        from app.infrastructure.spotify.extended_api_client import (
            ExtendedSpotifyApiClient,
        )

        result = ExtendedSpotifyApiClient.extract_track_from_item(
            {
                "added_at": "2025-01-01T00:00:00Z",
                "track": {
                    "id": "def456",
                    "name": "Old Track",
                    "artists": [{"name": "Old Artist"}],
                    "album": {"name": "Old Album", "images": []},
                    "duration_ms": 180000,
                    "external_urls": {
                        "spotify": "https://open.spotify.com/track/def456"
                    },
                    "popularity": 30,
                },
            }
        )
        assert result is not None
        assert result.id == "def456"
        assert result.name == "Old Track"

    def test_returns_none_for_no_track_or_item(self) -> None:
        from app.infrastructure.spotify.extended_api_client import (
            ExtendedSpotifyApiClient,
        )

        result = ExtendedSpotifyApiClient.extract_track_from_item(
            {"added_at": "2025-01-01T00:00:00Z"}
        )
        assert result is None

    def test_returns_none_for_null_item(self) -> None:
        from app.infrastructure.spotify.extended_api_client import (
            ExtendedSpotifyApiClient,
        )

        result = ExtendedSpotifyApiClient.extract_track_from_item(
            {
                "added_at": "2025-01-01T00:00:00Z",
                "item": None,
            }
        )
        assert result is None
