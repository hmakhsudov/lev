from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from real_estate.models import Property
from real_estate.serializers import PropertySerializer

from .serializers import QuerySerializer
from .services import AssistantClientError, parse_query_with_openrouter


class QueryParseView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = QuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data["query"]
        try:
            ai_response = parse_query_with_openrouter(query)
        except AssistantClientError as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        summary = ai_response.get("summary") or "Подобранные фильтры ниже."
        filters = ai_response.get("filters") or ai_response

        properties = self.get_matching_properties(filters)
        serialized = PropertySerializer(properties, many=True).data
        return Response(
            {"summary": summary, "filters": filters, "results": serialized, "count": len(serialized)}
        )

    def get_matching_properties(self, filters):
        qs = Property.objects.all()
        rooms = self._to_int(filters.get("rooms"))
        price_max = self._to_int(filters.get("price_max"))
        area_min = self._to_float(filters.get("area_min"))
        area_max = self._to_float(filters.get("area_max"))
        district = filters.get("district")
        city = filters.get("city")
        property_type = filters.get("property_type")

        if rooms is not None:
            qs = qs.filter(rooms=rooms)
        if price_max is not None:
            qs = qs.filter(price__lte=price_max)
        if area_min is not None:
            qs = qs.filter(area_total__gte=area_min)
        if area_max is not None:
            qs = qs.filter(area_total__lte=area_max)
        if district:
            qs = qs.filter(district__icontains=district)
        if city:
            qs = qs.filter(city__icontains=city)
        if property_type:
            qs = qs.filter(property_type=property_type)

        return qs.order_by("-created_at")[:10]

    @staticmethod
    def _to_int(value):
        try:
            if value is None:
                return None
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_float(value):
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None
