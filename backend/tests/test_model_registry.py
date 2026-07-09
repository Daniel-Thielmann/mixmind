"""Tests for ModelRegistry."""

import time

from app.ai.model_registry import ModelRegistry


class TestModelRegistry:
    def test_register_models(self) -> None:
        registry = ModelRegistry(["model-a", "model-b"])
        assert registry.get_valid_models() == ["model-a", "model-b"]

    def test_get_available_models_returns_all_when_valid(self) -> None:
        registry = ModelRegistry(["a", "b", "c"])
        available = registry.get_available_models()
        assert len(available) == 3

    def test_mark_invalid_removes_from_available(self) -> None:
        registry = ModelRegistry(["a", "b"])
        registry.mark_invalid("a")
        available = registry.get_available_models()
        assert "a" not in available
        assert "b" in available

    def test_mark_invalid_twice_is_idempotent(self) -> None:
        registry = ModelRegistry(["a"])
        registry.mark_invalid("a")
        registry.mark_invalid("a")
        assert registry.get_invalid_models() == ["a"]

    def test_mark_cooldown_removes_from_available(self) -> None:
        registry = ModelRegistry(["a", "b"])
        registry.mark_cooldown("a", duration=3600)
        available = registry.get_available_models()
        assert "a" not in available
        assert "b" in available

    def test_cooldown_expires_after_duration(self) -> None:
        registry = ModelRegistry(["a"])
        registry.mark_cooldown("a", duration=0.001)
        time.sleep(0.01)
        available = registry.get_available_models()
        assert "a" in available

    def test_unknown_model_operations_are_noop(self) -> None:
        registry = ModelRegistry(["a"])
        registry.mark_invalid("nonexistent")
        registry.mark_cooldown("nonexistent")
        registry.record_success("nonexistent", 1.0)
        registry.record_error("nonexistent")
        assert registry.get_available_models() == ["a"]

    def test_health_returns_all_categories(self) -> None:
        registry = ModelRegistry(["a", "b", "c"])
        registry.mark_invalid("a")
        registry.mark_cooldown("b", duration=3600)
        h = registry.health()
        assert "available_models" in h
        assert "cooldown_models" in h
        assert "invalid_models" in h
        assert "a" in h["invalid_models"]
        assert "b" in h["cooldown_models"]
        assert "c" in h["available_models"]

    def test_check_invalid_response_detects_invalid_model(self) -> None:
        registry = ModelRegistry(["model-x"])
        result = registry.check_invalid_response(
            "model-x", 400, "model-x is not a valid model ID"
        )
        assert result is True
        assert "model-x" in registry.get_invalid_models()

    def test_check_invalid_response_ignores_other_400(self) -> None:
        registry = ModelRegistry(["model-x"])
        result = registry.check_invalid_response("model-x", 400, "Bad request")
        assert result is False
        assert registry.get_invalid_models() == []

    def test_check_invalid_response_ignores_500(self) -> None:
        registry = ModelRegistry(["model-x"])
        result = registry.check_invalid_response(
            "model-x", 500, "is not a valid model ID"
        )
        assert result is False
        assert registry.get_invalid_models() == []

    def test_record_success_and_error(self) -> None:
        registry = ModelRegistry(["a"])
        registry.record_success("a", 0.5)
        registry.record_error("a")
        info = registry._models["a"]
        assert info.success_count == 1
        assert info.error_count == 1
        assert info.total_latency == 0.5

    def test_get_cooldown_models(self) -> None:
        registry = ModelRegistry(["a", "b"])
        registry.mark_cooldown("a", duration=3600)
        registry.mark_cooldown("b", duration=0.001)
        time.sleep(0.01)
        cooldown = registry.get_cooldown_models()
        assert "a" in cooldown
        assert "b" not in cooldown

    def test_dynamic_sort_by_success_rate(self) -> None:
        registry = ModelRegistry(["a", "b", "c"])
        registry.record_success("b", 0.5)
        registry.record_success("b", 0.3)
        registry.record_success("c", 0.8)
        registry.record_error("c")
        available = registry.get_available_models()
        assert available[0] == "b"

    def test_dynamic_sort_by_latency(self) -> None:
        registry = ModelRegistry(["a", "b"])
        registry.record_success("a", 2.0)
        registry.record_success("a", 2.0)
        registry.record_success("b", 1.0)
        registry.record_success("b", 1.0)
        available = registry.get_available_models()
        assert available[0] == "b"

    def test_is_valid(self) -> None:
        registry = ModelRegistry(["a", "b"])
        assert registry.is_valid("a") is True
        registry.mark_invalid("a")
        assert registry.is_valid("a") is False
        assert registry.is_valid("nonexistent") is False

    def test_register_models_does_not_duplicate(self) -> None:
        registry = ModelRegistry(["a"])
        registry.register_models(["a", "b"])
        assert registry.get_valid_models() == ["a", "b"]
