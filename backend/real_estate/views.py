from django.shortcuts import get_object_or_404
from rest_framework import pagination, parsers, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAgentOrAdmin, IsPropertyOwnerOrAdmin
from integrations.ads_api_client import AdsAPIError
from .models import Favorite, Property
from .serializers import PropertySerializer, PropertyWriteSerializer
from .services import YandexGeocoder, sync_ads_listings


class PropertyPagination(pagination.PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 60


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all().order_by("-created_at")
    serializer_class = PropertySerializer
    pagination_class = PropertyPagination
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            permission_classes = [permissions.AllowAny]
        elif self.action in {"update", "partial_update", "destroy"}:
            permission_classes = [
                permissions.IsAuthenticated,
                IsAgentOrAdmin,
                IsPropertyOwnerOrAdmin,
            ]
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
        city = params.get("city")
        property_type = params.get("property_type")
        area_min = params.get("area_min")
        area_max = params.get("area_max")
        order_by = params.get("order_by")
        mine = params.get("mine")

        if mine in {"1", "true", "True"} and self.request.user.is_authenticated:
            queryset = queryset.filter(created_by=self.request.user)

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if rooms:
            queryset = queryset.filter(rooms=rooms)
        if city:
            queryset = queryset.filter(city__icontains=city)
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        read_serializer = PropertySerializer(
            serializer.instance,
            context=self.get_serializer_context(),
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        read_serializer = PropertySerializer(
            serializer.instance,
            context=self.get_serializer_context(),
        )
        return Response(read_serializer.data)

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


class FavoriteListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        properties = (
            Property.objects.filter(favorited_by__user=request.user)
            .distinct()
            .order_by("-favorited_by__created_at")
        )
        serializer = PropertySerializer(
            properties,
            many=True,
            context={"request": request},
        )
        return Response({"results": serializer.data, "count": properties.count()})

    def post(self, request):
        listing_id = request.data.get("listing_id") or request.data.get("property_id")
        if not listing_id:
            return Response(
                {"listing_id": ["Укажите объект для добавления в избранное."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        property_obj = get_object_or_404(Property, pk=listing_id)
        Favorite.objects.get_or_create(user=request.user, property=property_obj)
        return Response({"favorited": True}, status=status.HTTP_201_CREATED)


class FavoriteDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, listing_id):
        Favorite.objects.filter(user=request.user, property_id=listing_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
