"""Client helpers for ADS-API (https://ads-api.ru)."""

from __future__ import annotations

import logging
from typing import Iterable, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

MAX_LIMIT = 1000


class AdsAPIError(Exception):
    """Raised when ADS API request fails."""


def _build_base_params(limit: int, withcoords: bool, is_actual: str) -> dict[str, str]:
    params = {
        "user": settings.ADS_API_USER or "",
        "token": settings.ADS_API_TOKEN or "",
        "format": "json",
        "limit": str(min(limit, MAX_LIMIT)),
        "withcoords": "1" if withcoords else "0",
        "is_actual": is_actual,
    }
    return params


def fetch_ads(
    *,
    city: Optional[str] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    nedvigimost_type: Optional[str | int] = 1,
    limit: int = 200,
    startid: Optional[int] = None,
    withcoords: bool = True,
    sources: Optional[Iterable[int]] = None,
    is_actual: str = "11,1",
    category_id: Optional[str] = None,
    polygon: Optional[list[dict]] = None,
) -> list[dict]:
    """Fetch raw ads data from ADS-API."""

    if not settings.ADS_API_USER or not settings.ADS_API_TOKEN:
        raise AdsAPIError("ADS API credentials are not configured")

    params = _build_base_params(limit, withcoords, is_actual)
    if category_id:
        params["category_id"] = str(category_id)
    if city:
        params["city"] = city
    if price_min is not None:
        params["price1"] = str(price_min)
    if price_max is not None:
        params["price2"] = str(price_max)
    if nedvigimost_type is not None:
        params["nedvigimost_type"] = (
            ",".join(map(str, nedvigimost_type))
            if isinstance(nedvigimost_type, (list, tuple, set))
            else str(nedvigimost_type)
        )
    if startid is not None:
        params["startid"] = str(startid)
    if sources:
        params["source"] = ",".join(str(s) for s in sources)
    if polygon:
        for idx, point in enumerate(polygon):
            lat = point.get("lat")
            lng = point.get("lng")
            if lat is None or lng is None:
                continue
            params[f"area[{idx}][lat]"] = str(lat)
            params[f"area[{idx}][lng]"] = str(lng)

    base_url = settings.ADS_API_BASE_URL or "https://ads-api.ru/main/api"
    try:
        response = requests.get(base_url, params=params, timeout=30)
    except requests.RequestException as exc:  # pragma: no cover - network
        logger.exception("ADS-API request error")
        raise AdsAPIError("ADS-API network error") from exc

    if response.status_code != 200:
        logger.error("ADS-API returned HTTP %s: %s", response.status_code, response.text)
        raise AdsAPIError(f"ADS-API HTTP {response.status_code}")

    try:
        payload = response.json()
    except ValueError as exc:
        logger.exception("ADS-API invalid JSON: %s", response.text)
        raise AdsAPIError("ADS-API invalid JSON") from exc

    data = payload.get("data")
    if not isinstance(data, list):
        logger.error("ADS-API payload without data array: %s", payload)
        raise AdsAPIError("ADS-API response missing data array")
    return data


def fetch_flats_for_city(
    *,
    city: Optional[str] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    startid: Optional[int] = None,
    limit: int = 200,
    polygon: Optional[list[dict]] = None,
    withcoords: bool = True,
    nedvigimost_type: Optional[str | int] = 1,
) -> list[dict]:
    """Convenience helper for fetching apartments (category: flats)."""

    category_id = settings.ADS_API_CATEGORY_FLATS
    sources = [4, 11]  # CIAN + Domclick per docs
    return fetch_ads(
        city=city,
        price_min=price_min,
        price_max=price_max,
        nedvigimost_type=nedvigimost_type,
        withcoords=withcoords,
        sources=sources,
        category_id=category_id,
        limit=limit,
        startid=startid,
        polygon=polygon,
    )
