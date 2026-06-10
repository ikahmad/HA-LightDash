from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from app.sse_manager import HAWebSocket, SSEManager

logger = logging.getLogger(__name__)

_CACHE_TTL = 1800  # 30 minutes


class ForecastCache:
    def __init__(self):
        self._data: Dict[str, tuple[Any, float]] = {}

    def get(self, entity_id: str) -> Any:
        entry = self._data.get(entity_id)
        if entry is None:
            return None
        data, ts = entry
        if time.monotonic() - ts > _CACHE_TTL:
            del self._data[entity_id]
            return None
        return data

    def set(self, entity_id: str, data: Any) -> None:
        self._data[entity_id] = (data, time.monotonic())

    def clear(self, entity_id: str) -> None:
        self._data.pop(entity_id, None)


def _extract_forecast_list(entity_id: str, forecast_result: Any) -> list:
    if not isinstance(forecast_result, dict):
        return []
    response = forecast_result.get("response", {})
    if not isinstance(response, dict):
        return []
    entity_data = response.get(entity_id, {})
    if not isinstance(entity_data, dict):
        return []
    forecast = entity_data.get("forecast", [])
    return forecast if isinstance(forecast, list) else []


async def get_forecast(
    entity_id: str,
    ws_client: HAWebSocket,
    cache: ForecastCache,
    entity_states: dict,
) -> list:
    cached = cache.get(entity_id)
    if cached is not None:
        return _extract_forecast_list(entity_id, cached)

    if ws_client.connected:
        try:
            result = await ws_client.call_service(
                "weather",
                "get_forecasts",
                {"type": "daily"},
                return_response=True,
                target={"entity_id": entity_id},
            )
            cache.set(entity_id, result)
            return _extract_forecast_list(entity_id, result)
        except TimeoutError:
            logger.warning("Weather forecast WS call timed out for %s", entity_id)
        except ConnectionError:
            logger.warning("WebSocket not connected — cannot fetch forecast for %s", entity_id)
        except Exception as e:
            logger.warning("Weather forecast WS call failed for %s: %s", entity_id, e)

    state = entity_states.get(entity_id, {})
    attrs = state.get("attributes", {}) if state else {}
    return attrs.get("forecast", [])


async def refresh_forecast(
    entity_id: str,
    ws_client: HAWebSocket,
    cache: ForecastCache,
    sse: SSEManager,
) -> None:
    cached = cache.get(entity_id)
    if cached is not None:
        return

    if not ws_client.connected:
        return

    try:
        result = await ws_client.call_service(
            "weather",
            "get_forecasts",
            {"type": "daily"},
            return_response=True,
            target={"entity_id": entity_id},
        )
        cache.set(entity_id, result)
        event_name = f"forecast_{entity_id.replace('.', '_')}"
        sse.broadcast(event_name, {"entity": entity_id})
        logger.info("Forecast refreshed for %s, SSE event=%s", entity_id, event_name)
    except Exception as e:
        logger.debug("Forecast background refresh failed for %s: %s", entity_id, e)



