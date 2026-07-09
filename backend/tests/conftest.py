import sys
from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")

BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture(autouse=True)
def _reset_ai_globals() -> None:
    from app.ai.cache import recommendation_cache
    from app.ai.metrics import llm_metrics

    recommendation_cache.clear()
    llm_metrics.reset()
