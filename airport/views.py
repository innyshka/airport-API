from datetime import datetime
from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, mixins, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Route,
    Order,
    Flight,
    JobPosition,
    Country,
    City,
)
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import (
    AirplaneTypeSerializer,
    CrewSerializer,
    CrewDetailSerializer,
    CrewImageSerializer,
    AirplaneSerializer,
    AirplaneImageSerializer,
    AirplaneDetailSerializer,
    AirplaneListSerializer,
    AirportSerializer,
    AirportListSerializer,
    AirportDetailSerializer,
    AirportImageSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    FlightSerializers,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
    JobPositionSerializer,
    CrewListSerializer,
    CountrySerializer,
    CitySerializer,
    CityListSerializer,
)


def _params_to_ints(qs) -> list:
    """Converts a list of string IDs to a list of integers"""
    return [int(str_id) for str_id in qs.split(",")]


class UploadImageViewSet(mixins.CreateModelMixin, GenericViewSet):
    upload_serializer_class = None
    permission_classes = [IsAdminUser]

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific movie"""
        crew = self.get_object()
        serializer = self.get_serializer(crew, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class JobPositionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = JobPosition.objects.all()
    serializer_class = JobPositionSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CrewViewSet(
    UploadImageViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = (
        Crew.objects.all().prefetch_related("flights")
        .select_related("position")
    )
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        if self.action == "retrieve":
            return self.queryset.annotate(
                flights_count=Count("flights")
            )
        positions = self.request.query_params.get("positions")
        if positions:
            positions_ids = _params_to_ints(positions)
            return self.queryset.filter(position_id__in=positions_ids)
        return self.queryset

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        if self.action == "retrieve":
            return CrewDetailSerializer

        if self.action == "upload_image":
            return CrewImageSerializer

        return self.serializer_class


class AirplaneViewSet(
    UploadImageViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Airplane.objects.all().select_related("airplane_type")
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        name = self.request.query_params.get("name")
        airplane_types = self.request.query_params.get("airplane_types")
        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)
        if airplane_types:
            airplane_types_ids = _params_to_ints(airplane_types)
            queryset = queryset.filter(airplane_type_id__in=airplane_types_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneDetailSerializer
        if self.action == "upload_image":
            return AirplaneImageSerializer

        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "airplane_types",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by airplane_type id "
                            "(ex. ?airplane_types=2,5)",
            ),
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by airplane name (ex. ?name=test)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CountryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CityViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = City.objects.all().select_related("country")
    serializer_class = CitySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return CityListSerializer
        return self.serializer_class


class AirportViewSet(
    UploadImageViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.all().select_related("closest_big_city")
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        name = self.request.query_params.get("name")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportDetailSerializer
        if self.action == "upload_image":
            return AirportImageSerializer

        return self.serializer_class


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        queryset = self.queryset

        if source:
            source_ids = _params_to_ints(source)
            queryset = queryset.filter(source__id__in=source_ids)
        if destination:
            destination_ids = _params_to_ints(destination)
            queryset = queryset.filter(destination__id__in=destination_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by source id (ex. ?source=2,5)",
            ),
            OpenApiParameter(
                "destination",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by destination id (ex. ?destination=2,5)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FlightPagination(PageNumberPagination):
    page_size = 3
    max_page_size = 100


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all()
        .select_related(
            "airplane__airplane_type",
            "route__source",
            "route__destination",
        ).prefetch_related("crews")
        .annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        )
    )
    serializer_class = FlightSerializers
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = FlightPagination

    def get_queryset(self):
        departure_time = self.request.query_params.get("departure_time")
        arrival_time = self.request.query_params.get("arrival_time")
        route_id = self.request.query_params.get("route")

        queryset = self.queryset

        if departure_time:
            departure_time = datetime.strptime(
                departure_time,
                "%H:%M:%S %d-%m-%Y"
            ).date()
            queryset = queryset.filter(departure_time__date=departure_time)

        if arrival_time:
            arrival_time = datetime.strptime(
                arrival_time,
                "%H:%M:%S %d-%m-%Y"
            ).date()
            queryset = queryset.filter(arrival_time__date=arrival_time)

        if route_id:
            queryset = queryset.filter(route_id=int(route_id))
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "departure_time",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by departure time of Flight "
                    "(ex. ?departure_time=16:59:11 19-10-2023)"
                ),
            ),
            OpenApiParameter(
                "arrival_time",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by arrival time of Flight "
                    "(ex. ?arrival_time=16:59:11 19-10-2023)"
                ),
            ),
            OpenApiParameter(
                "route",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by route id (ex. ?route=2,5)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 2
    max_page_size = 100


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__airplane",
        "tickets__flight__route",
    )
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
