from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Ticket,
    Route,
    Order,
    Flight
)
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import (
    AirplaneTypeSerializer,
    CrewSerializer,
    CrewDetailSerializer,
    CrewImageSerializer
)


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CrewDetailSerializer

        if self.action == "upload_image":
            return CrewImageSerializer

        return CrewSerializer

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

