from django.urls import path, include
from rest_framework import routers

from .views import (
    AirplaneViewSet,
    CrewViewSet,
    AirplaneTypeViewSet,
    AirportViewSet,
    RouteViewSet,
    FlightViewSet
)


router = routers.DefaultRouter()
router.register("airplanes_type", AirplaneTypeViewSet)
router.register("crew", CrewViewSet)
router.register("airplane", AirplaneViewSet)
router.register("airport", AirportViewSet)
router.register("route", RouteViewSet)
router.register("flight", FlightViewSet)


urlpatterns = [path("", include(router.urls))]

app_name = "airport"
