from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Ticket,
    Route,
    Order,
    Flight,
    JobPosition,
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class JobPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosition
        fields = ("id", "title")


class CrewSerializer(serializers.ModelSerializer):
    position = serializers.CharField(source="position.title")

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name", "position")


class CrewDetailSerializer(CrewSerializer):
    flights_count = serializers.IntegerField()

    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "position",
            "flights_count",
            "image"
        )


class CrewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "image")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
        )


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type_name = serializers.CharField(
        source="airplane_type.name", read_only=True
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type_name",
        )


class AirplaneDetailSerializer(serializers.ModelSerializer):
    airplane_type_name = serializers.CharField(
        source="airplane_type.name", read_only=True
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type_name",
            "image",
        )


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "image")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class AirportListSerializer(AirportSerializer):
    pass


class AirportDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city", "image")


class AirportImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "image")


class RouteSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(RouteSerializer, self).validate(attrs=attrs)
        Route.validate_time(
            attrs["source"], attrs["destination"], ValidationError
        )
        return data

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source_name = serializers.CharField(source="source.name", read_only=True)
    destination_name = serializers.CharField(
        source="destination.name", read_only=True
    )

    class Meta:
        model = Route
        fields = ("id", "source_name", "destination_name", "distance")


class RouteDetailSerializer(RouteSerializer):
    source = AirportListSerializer(many=False, read_only=True)
    destination = AirportDetailSerializer(many=False, read_only=True)


class FlightSerializers(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(FlightSerializers, self).validate(attrs=attrs)
        Flight.validate_time(
            attrs["departure_time"], attrs["arrival_time"], ValidationError
        )
        return data

    departure_time = serializers.DateTimeField(format="%H:%M:%S %d-%m-%Y")
    arrival_time = serializers.DateTimeField(format="%H:%M:%S %d-%m-%Y")

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crews",
            "departure_time",
            "arrival_time"
        )


class FlightListSerializer(FlightSerializers):
    route = RouteListSerializer(many=False, read_only=True)
    airplane_name = serializers.CharField(
        source="airplane.name", read_only=True
    )
    airplane_capacity = serializers.CharField(
        source="airplane.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)
    crews = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane_name",
            "crews",
            "airplane_capacity",
            "departure_time",
            "arrival_time",
            "tickets_available",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError,
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class FlightDetailSerializer(FlightListSerializer):
    route = RouteDetailSerializer(many=False, read_only=True)
    airplane = AirplaneDetailSerializer(many=False, read_only=True)
    taken_places = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )
    crews = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crews",
            "departure_time",
            "arrival_time",
            "taken_places",
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
