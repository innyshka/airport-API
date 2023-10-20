from django.urls import path, include
from rest_framework import routers

from .views import (
    AirplaneViewSet,
    CrewViewSet,
    AirplaneTypeViewSet,
    AirportViewSet,
    RouteViewSet,
    FlightViewSet,
    OrderViewSet,
)


router = routers.DefaultRouter()
router.register("airplanes_types", AirplaneTypeViewSet)
router.register("crews", CrewViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)


urlpatterns = [path("", include(router.urls))]

app_name = "airport"
