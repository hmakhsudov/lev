import json
import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Iterable, Optional

import requests
from django.conf import settings
from django.db import transaction

from integrations.ads_api_client import AdsAPIError, fetch_flats_for_city

from .models import Property, PropertyImage


class CIANClient:
    base_url = "https://api.cian.ru/stub"

    def fetch_listings(self, **filters):
        # Placeholder for real integration with the CIAN API.
        return [
            {
                "external_id": "mock-1",
                "title": "Светлая двушка у метро",
                "description": "Просторная квартира с видом на парк",
                "price": 9800000,
                "area": 62.5,
                "rooms": 2,
                "floor": 7,
                "floors_total": 16,
                "property_type": "apartment",
                "address": "пр. Просвещения, 15",
                "district": "Приморский",
                "city": "Санкт-Петербург",
                "images": [
                    "https://placehold.co/600x400",
                ],
            }
        ]


class YandexGeocoder:
    base_url = "https://geocode-maps.yandex.ru/1.x"

    def geocode(self, address: str):
        api_key = settings.YANDEX_GEOCODER_API_KEY
        if not api_key:
            return None
        params = {
            "apikey": api_key,
            "geocode": address,
            "format": "json",
            "results": 1,
        }
        response = requests.get(self.base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        try:
            pos = data["response"]["GeoObjectCollection"]["featureMember"][0][
                "GeoObject"
            ]["Point"]["pos"].split(" ")
            lon, lat = map(float, pos)
            return lat, lon
        except (KeyError, IndexError, ValueError):
            return None

    def geocode_properties(self, properties: Iterable[Property]):
        updated = 0
        for prop in properties:
            result = self.geocode(prop.address)
            if result:
                prop.latitude, prop.longitude = result
                prop.save(update_fields=["latitude", "longitude"])
                updated += 1
        return updated


def sync_cian_listings(user):
    client = CIANClient()
    listings = client.fetch_listings()
    created = 0
    for listing in listings:
        property_values = {k: v for k, v in listing.items() if k != "images"}
        property_values.setdefault("created_by", user)
        property_obj, _created = Property.objects.update_or_create(
            external_id=listing.get("external_id"), defaults=property_values
        )
        if _created:
            created += 1
        if listing.get("images"):
            property_obj.images = listing["images"]
            property_obj.save(update_fields=["images"])
    return created


logger = logging.getLogger(__name__)
ADS_SOURCE = "ads_api"


def sync_ads_listings(
    city: Optional[str] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    startid: Optional[int] = None,
    limit: int = 200,
    polygon: Optional[list[dict]] = None,
    with_coords: bool = True,
    nedvigimost_type: Optional[str | int] = 1,
) -> dict:
    """
    Import or update properties from ADS-API into the local database.
    """

    computed_startid = startid
    if computed_startid is None:
        computed_startid = _determine_next_startid()

    fetch_startid = computed_startid
    if fetch_startid is not None:
        fetch_startid = max(fetch_startid, 0)

    ads_items = fetch_flats_for_city(
        city=city,
        price_min=price_min,
        price_max=price_max,
        startid=fetch_startid,
        limit=limit,
        polygon=polygon,
        withcoords=with_coords,
        nedvigimost_type=nedvigimost_type,
    )
    created = updated = skipped = 0

    for payload in ads_items:
        logger.debug("ADS raw payload: %s", json.dumps(payload, ensure_ascii=False))
        external_id = str(payload.get("id") or "").strip()
        if not external_id:
            skipped += 1
            logger.debug("ADS object skipped: missing id")
            continue

        coords = payload.get("coords") or {}
        latitude = _to_decimal(coords.get("lat"))
        longitude = _to_decimal(coords.get("lng"))
        if latitude is None or longitude is None:
            skipped += 1
            continue

        price = _extract_price(payload)
        if price is None:
            logger.warning(
                "ADS listing %s has no price in ADS payload, importing with price=0 (raw=%s | full=%s)",
                external_id,
                payload.get("price"),
                json.dumps(payload, ensure_ascii=False),
            )
            price = Decimal("0")

        defaults, gallery_urls = _map_payload_to_defaults(
            payload, price, latitude, longitude
        )

        try:
            with transaction.atomic():
                property_obj, created_flag = Property.objects.update_or_create(
                    external_id=external_id,
                    source=defaults["source"],
                    defaults=defaults,
                )
                PropertyImage.objects.filter(property=property_obj).delete()
                gallery = [
                    PropertyImage(property=property_obj, url=url)
                    for url in gallery_urls
                ]
                if gallery:
                    PropertyImage.objects.bulk_create(gallery)
            if created_flag:
                created += 1
            else:
                updated += 1
        except Exception:  # pragma: no cover - defensive logging
            skipped += 1
            logger.exception("Failed to sync ADS listing %s", external_id)
            continue

    total = len(ads_items)
    logger.info(
        "ADS sync finished city=%s total=%s created=%s updated=%s skipped=%s",
        city,
        total,
        created,
        updated,
        skipped,
    )
    return {"created": created, "updated": updated, "total": total, "skipped": skipped}


def _determine_next_startid() -> Optional[int]:
    values = (
        Property.objects.filter(source=ADS_SOURCE)
        .exclude(external_id__isnull=True)
        .values_list("external_id", flat=True)
    )
    max_id = None
    for value in values:
        try:
            numeric = int(value)
        except (TypeError, ValueError):
            continue
        if max_id is None or numeric > max_id:
            max_id = numeric
    if max_id is None:
        return None
    return max_id + 1


def _map_payload_to_defaults(payload, price, latitude, longitude):
    source = str(payload.get("source") or payload.get("source_id") or ADS_SOURCE)
    city = payload.get("city1") or payload.get("city") or ""
    district = _extract_district(payload)
    address = payload.get("address") or ", ".join(
        filter(None, [payload.get("region"), city, payload.get("street")])
    )
    rooms = _extract_rooms(payload)
    area_total = _extract_area(payload, ["общ", "площад"])
    living_area = _extract_area(payload, ["жила"])
    kitchen_area = _extract_area(payload, ["кух"])
    floor = _safe_int(payload.get("floor"))
    floors_total = _safe_int(payload.get("floors_total") or payload.get("floors"))
    property_type, property_display = _extract_property_type(payload)
    building_type = payload.get("house_type") or property_display or ""
    year_built = _extract_year_built(payload)
    is_new_building = _extract_is_new_building(payload)
    image_urls = _collect_image_urls(payload.get("images") or [])
    title = payload.get("title") or _compose_title(rooms, area_total, property_display)
    description = payload.get("description") or payload.get("about") or ""

    defaults = {
        "source": source,
        "source_id": payload.get("source_id") or "",
        "title": title,
        "description": description,
        "price": price,
        "predicted_price": _to_decimal(payload.get("predicted_price")),
        "area_total": area_total,
        "living_area": living_area,
        "kitchen_area": kitchen_area,
        "rooms": rooms,
        "floor": floor,
        "floors_total": floors_total,
        "property_type": property_type,
        "building_type": building_type,
        "address": address or city,
        "district": district,
        "city": city or "",
        "latitude": latitude,
        "longitude": longitude,
        "is_new_building": is_new_building,
        "year_built": year_built,
        "images": image_urls,
        "external_url": payload.get("url"),
    }
    return defaults, image_urls


def _collect_image_urls(images) -> list[str]:
    urls = []
    for image in images:
        if isinstance(image, dict):
            url = image.get("imgurl") or image.get("url")
        else:
            url = image
        if url:
            urls.append(url)
    return urls


def _extract_price(payload) -> Optional[Decimal]:
    candidates = [
        payload.get("price"),
        payload.get("price_real"),
        payload.get("price_from"),
        payload.get("price_to"),
        payload.get("price_min"),
        payload.get("price_max"),
        payload.get("price1"),
        payload.get("price2"),
    ]
    for name, value in _iterate_param_items(payload):
        if "цен" in name:
            candidates.append(value)
    for candidate in candidates:
        decimal_value = _to_decimal(candidate)
        if decimal_value is not None and decimal_value >= 0:
            return decimal_value
    return None


def _extract_rooms(payload) -> Optional[int]:
    candidates = [
        payload.get("rooms"),
        payload.get("roomcount"),
        payload.get("rooms_count"),
        payload.get("room_number"),
    ]
    for name, value in _iterate_param_items(payload):
        if any(key in name for key in ("комнат", "кол-во комнат")):
            candidates.append(value)
    for candidate in candidates:
        value = _safe_int(candidate)
        if value is not None:
            return value
    return None


def _extract_area(payload, keywords) -> Optional[Decimal]:
    direct_candidates = []
    if "общ" in keywords:
        direct_candidates.extend(
            [
                payload.get("square_total"),
                payload.get("square"),
                payload.get("area"),
            ]
        )
    if "жила" in keywords:
        direct_candidates.append(payload.get("square_living"))
    if "кух" in keywords:
        direct_candidates.append(payload.get("square_kitchen"))

    for name, value in _iterate_param_items(payload):
        if any(key in name for key in keywords):
            direct_candidates.append(value)

    for candidate in direct_candidates:
        decimal_value = _to_decimal(candidate)
        if decimal_value is not None:
            return decimal_value
    return None


def _extract_property_type(payload):
    candidates = [
        payload.get("property_type"),
        payload.get("estate_type"),
        payload.get("category_name"),
        payload.get("type_name"),
        payload.get("realty_type"),
    ]
    for name, value in _iterate_param_items(payload):
        if any(key in name for key in ("тип недвижимости", "тип жилья", "тип объекта")):
            candidates.append(value)
    display = next((val for val in candidates if val), "")
    slug = _normalize_property_type(display)
    return slug, display


def _extract_district(payload):
    return (
        payload.get("district_only")
        or payload.get("microdistrict")
        or payload.get("district")
        or payload.get("city_district")
        or payload.get("subdistrict")
        or payload.get("metro")
        or ""
    )


def _extract_is_new_building(payload):
    candidates = [
        payload.get("is_newbuilding"),
        payload.get("is_new"),
        payload.get("newbuilding"),
    ]
    for name, value in _iterate_param_items(payload):
        if "новострой" in name:
            candidates.append(value)
    for candidate in candidates:
        if isinstance(candidate, str):
            value = candidate.strip().lower()
            if value in {"1", "true", "да", "yes"}:
                return True
        elif candidate:
            return True
    return False


def _extract_year_built(payload):
    candidates = [payload.get("year_built")]
    for name, value in _iterate_param_items(payload):
        if "год" in name and ("постро" in name or "стро" in name):
            candidates.append(value)
    for candidate in candidates:
        if candidate in (None, ""):
            continue
        match = re.search(r"\d{4}", str(candidate))
        if match:
            return _safe_int(match.group())
    return None


def _compose_title(rooms, area_total, property_display):
    if rooms or area_total:
        parts = []
        if rooms:
            parts.append(f"{rooms}-комн.")
        parts.append(property_display or "квартира")
        if area_total:
            area_value = (
                f"{area_total.normalize()}" if isinstance(area_total, Decimal) else str(area_total)
            )
            parts.append(f"{area_value} м²")
        return " ".join(parts)
    return property_display or "Квартира"


def _iterate_param_items(payload):
    params = payload.get("params")
    if isinstance(params, list):
        for item in params:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).lower()
            yield name, item.get("value")
    elif isinstance(params, dict):
        for key, value in params.items():
            if isinstance(value, dict):
                name = str(value.get("name", key)).lower()
                yield name, value.get("value")
            else:
                yield str(key).lower(), value
    for key, value in payload.items():
        if isinstance(key, str) and key.lower().startswith("param"):
            yield key.lower(), value


def _normalize_property_type(label: Optional[str]) -> str:
    text = (label or "").lower()
    if "коммер" in text:
        return "commercial"
    if "комнат" in text or "комнат" == text or "комната" in text:
        return "room"
    if "дом" in text or "котт" in text or "таун" in text:
        return "house"
    return "apartment"


def _safe_int(value) -> Optional[int]:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_decimal(value) -> Optional[Decimal]:
    if value in (None, ""):
        return None
    if isinstance(value, str):
        cleaned = re.sub(r"[^\d,.\-]", "", value.replace(" ", ""))
        if cleaned in {"", ".", "-"}:
            logger.debug("Unable to parse decimal from string %s (cleaned result empty)", value)
            return None
        value = cleaned.replace(",", ".")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        logger.debug("Failed to convert value %s to Decimal", value)
        return None
