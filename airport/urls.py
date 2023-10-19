from django.urls import path, include
from rest_framework import routers

from .views import (
    AirplaneViewSet,
    CrewViewSet
)


router = routers.DefaultRouter()
router.register("airplanes_type", AirplaneViewSet)
router.register("crew", CrewViewSet)


urlpatterns = [path("", include(router.urls))]

app_name = "airport"
