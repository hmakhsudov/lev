from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAgentOrAdmin
from integrations.ads_api_client import AdsAPIError
from .models import Property
from .serializers import PropertySerializer, PropertyWriteSerializer
from .services import YandexGeocoder, sync_ads_listings


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all().order_by("-created_at")
    serializer_class = PropertySerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated, IsAgentOrAdmin]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return PropertyWriteSerializer
        return PropertySerializer

    def get_queryset(self):
        queryset = self.queryset
        params = self.request.query_params

        min_price = params.get("min_price")
        max_price = params.get("max_price")
        rooms = params.get("rooms")
        district = params.get("district")
        property_type = params.get("property_type")
        area_min = params.get("area_min")
        area_max = params.get("area_max")
        order_by = params.get("order_by")

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if rooms:
            queryset = queryset.filter(rooms=rooms)
        if district:
            queryset = queryset.filter(district__icontains=district)
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        if area_min:
            queryset = queryset.filter(area_total__gte=area_min)
        if area_max:
            queryset = queryset.filter(area_total__lte=area_max)
        if order_by in {"price", "-price"}:
            queryset = queryset.order_by(order_by)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["post"])
    def geocode(self, request):
        geocoder = YandexGeocoder()
        updated = geocoder.geocode_properties(Property.objects.all())
        return Response({"updated": updated})

    @action(detail=False, methods=["post"])
    def sync(self, request):
        """Backward-compatible alias for the new sync endpoint."""
        return self.sync_external(request)

    @action(detail=False, methods=["post"], url_path="sync-external")
    def sync_external(self, request):
        params = request.data or {}
        try:
            summary = sync_ads_listings(
                city=params.get("city"),
                price_min=self._parse_int(params.get("price_min")),
                price_max=self._parse_int(params.get("price_max")),
                startid=self._parse_int(params.get("startid")),
                limit=self._parse_int(params.get("limit")) or 200,
            )
        except AdsAPIError as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(summary)

    @staticmethod
    def _parse_int(value):
        try:
            if value in (None, "", []):
                return None
            return int(value)
        except (TypeError, ValueError):
            return None
