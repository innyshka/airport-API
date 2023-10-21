from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Flight, AirplaneType, Airplane, Airport, Route, Crew, JobPosition, Country, City
from airport.serializers import (
    FlightSerializers,
    FlightListSerializer,
    FlightDetailSerializer
)


def sample_crew(**params):
    index = Crew.objects.count() + 1
    position = JobPosition.objects.create(
        title=f"Test{index}"
    )
    defaults = {
        "first_name": f"first_name{index}",
        "last_name": f"first_name{index}",
        "position": position
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


def sample_airplane_type(**params):
    index = AirplaneType.objects.count() + 1
    defaults = {
        "name": f"airplane_type{index}",
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):
    index = Airplane.objects.count() + 1
    defaults = {
        "name": f"airplane{index}",
        "rows": 50,
        "seats_in_row": 10,
        "airplane_type": sample_airplane_type()
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def sample_airport(**params):
    index = Airport.objects.count() + 1
    country = Country.objects.create(name=f"Test{index}")
    city = City.objects.create(name=f"Test{index}", country=country)

    defaults = {
        "name": f"airport{index}",
        "closest_big_city": city,
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


def sample_route(**params):
    defaults = {
        "source": sample_airport(),
        "destination": sample_airport(),
        "distance": 600,
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_flight(**params):
    defaults = {
        "route": sample_route(),
        "airplane": sample_airplane(),
        "departure_time": timezone.now() + timedelta(hours=1),
        "arrival_time": timezone.now() + timedelta(hours=3)
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)


def flight_detail_url(pk: int):
    return reverse("airport:flight-detail", args=[pk])


FLIGHT_LIST_URL = reverse("airport:flight-list")


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_flight_list_required(self):
        res = self.client.get(FLIGHT_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_flight_detail_required(self):
        flight = sample_flight()
        res = self.client.get(flight_detail_url(flight.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAdminMixin(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.source1 = sample_airport(name="Borispol")
        self.source2 = sample_airport(name="Kharkiv")

        self.destination = sample_airport(name="Odessa")

        self.route1 = sample_route(source=self.source1,
                                   destination=self.destination)
        self.route2 = sample_route(source=self.source2,
                                   destination=self.destination)

        self.flight1 = sample_flight(route=self.route1)
        self.flight2 = sample_flight(route=self.route2)
        self.flight3 = sample_flight()

        self.serializer1 = FlightListSerializer(self.flight1)
        self.serializer2 = FlightListSerializer(self.flight2)
        self.serializer3 = FlightListSerializer(self.flight3)

        self.list_serializer = FlightListSerializer(
            Flight.objects.order_by("id"), many=True
        )


class AuthenticatedFlightApiTests(AuthenticatedAdminMixin):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_flights(self):
        sample_flight()
        res = self.client.get(FLIGHT_LIST_URL)
        flights = Flight.objects.order_by("id")
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, self.list_serializer.data)

    def test_retrieve_flight_detail(self):
        url = flight_detail_url(self.flight1.id)
        res = self.client.get(url)

        serializer = FlightDetailSerializer(self.flight1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_flight_forbidden(self):
        payload = {
            "route": sample_route(),
            "airplane": sample_airplane(),
            "departure_time": timezone.now() + timedelta(hours=2),
            "arrival_time": timezone.now() + timedelta(hours=7)
        }
        res = self.client.post(FLIGHT_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTests(AuthenticatedAdminMixin):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_flight(self):
        route = sample_route()
        airplane = sample_airplane()
        crew = sample_crew()

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": timezone.now() + timedelta(hours=2),
            "arrival_time": timezone.now() + timedelta(hours=7),
            "crew": [crew.id]
        }

        res = self.client.post(FLIGHT_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        flight = Flight.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(flight, key))
