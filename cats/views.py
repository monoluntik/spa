from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import SpyCat, Mission, Target
from cats.serializers import (
    SpyCatSerializer,
    MissionSerializer,
    MissionCreateSerializer,
    TargetSerializer,
    TargetUpdateSerializer,
    AssignCatSerializer
)


class SpyCatViewSet(viewsets.ModelViewSet):
    queryset = SpyCat.objects.all()
    serializer_class = SpyCatSerializer

    def update(self, request, *args, **kwargs):
        """Only allow updating salary"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Only allow salary updates
        allowed_fields = {'salary'}
        data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Spy cat deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return MissionCreateSerializer
        return MissionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mission = serializer.save()
        
        # Return full mission data
        response_serializer = MissionSerializer(mission)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if mission is assigned to a cat
        if instance.cat is not None:
            return Response(
                {"error": "Cannot delete a mission that is assigned to a cat"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(instance)
        return Response(
            {"message": "Mission deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['post'])
    def assign_cat(self, request, pk=None):
        """Assign a cat to a mission"""
        mission = self.get_object()
        
        if mission.cat is not None:
            return Response(
                {"error": "Mission is already assigned to a cat"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AssignCatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cat = get_object_or_404(SpyCat, id=serializer.validated_data['cat_id'])
        mission.cat = cat
        mission.save()
        
        response_serializer = MissionSerializer(mission)
        return Response(response_serializer.data)

    @action(detail=True, methods=['patch'])
    def update_target(self, request, pk=None):
        """Update a specific target's notes or completion status"""
        mission = self.get_object()
        target_id = request.data.get('target_id')
        
        if not target_id:
            return Response(
                {"error": "target_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        target = get_object_or_404(Target, id=target_id, mission=mission)
        
        serializer = TargetUpdateSerializer(
            data=request.data,
            context={'target': target}
        )
        serializer.is_valid(raise_exception=True)
        
        # Update target
        if 'notes' in serializer.validated_data:
            target.notes = serializer.validated_data['notes']
        
        if 'complete' in serializer.validated_data:
            target.complete = serializer.validated_data['complete']
        
        target.save()
        
        # Check if mission should be marked as complete
        mission.check_completion()
        
        # Return updated mission
        response_serializer = MissionSerializer(mission)
        return Response(response_serializer.data)