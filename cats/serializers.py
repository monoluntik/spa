import requests
from rest_framework import serializers
from cats.models import SpyCat, Mission, Target


class SpyCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpyCat
        fields = ['id', 'name', 'years_of_experience', 'breed', 'salary', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_breed(self, value):
        """Validate breed using TheCatAPI"""
        try:
            response = requests.get(
                f'https://api.thecatapi.com/v1/breeds/search?q={value}',
                timeout=5
            )
            response.raise_for_status()
            breeds = response.json()
            
            
            if breeds == []:
                raise serializers.ValidationError(
                    f"Invalid breed. Please use a valid cat breed from TheCatAPI."
                )
            
            return value
        except requests.RequestException as e:
            raise serializers.ValidationError(
                f"Unable to validate breed at this time. Please try again later."
            )


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['id', 'name', 'country', 'notes', 'complete', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        # Check if target or mission is complete when updating notes
        if self.instance:
            is_updating_notes = 'notes' in data and data['notes'] != self.instance.notes
            
            if is_updating_notes:
                if self.instance.complete:
                    raise serializers.ValidationError(
                        "Cannot update notes for a completed target."
                    )
                if self.instance.mission.complete:
                    raise serializers.ValidationError(
                        "Cannot update notes for a target in a completed mission."
                    )
        
        return data


class TargetUpdateSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
    complete = serializers.BooleanField(required=False)

    def validate(self, data):
        target = self.context.get('target')
        
        if 'notes' in data and target:
            if target.complete:
                raise serializers.ValidationError(
                    "Cannot update notes for a completed target."
                )
            if target.mission.complete:
                raise serializers.ValidationError(
                    "Cannot update notes for a target in a completed mission."
                )
        
        return data


class MissionSerializer(serializers.ModelSerializer):
    targets = TargetSerializer(many=True, read_only=True)
    cat_details = SpyCatSerializer(source='cat', read_only=True)

    class Meta:
        model = Mission
        fields = ['id', 'cat', 'cat_details', 'complete', 'targets', 'created_at', 'updated_at']
        read_only_fields = ['id', 'complete', 'created_at', 'updated_at']


class MissionCreateSerializer(serializers.ModelSerializer):
    targets = TargetSerializer(many=True, write_only=True)

    class Meta:
        model = Mission
        fields = ['cat', 'targets']

    def validate_targets(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Mission must have at least 1 target.")
        if len(value) > 3:
            raise serializers.ValidationError("Mission cannot have more than 3 targets.")
        return value

    def validate_cat(self, value):
        if value and value.has_active_mission():
            raise serializers.ValidationError(
                f"Cat '{value.name}' already has an active mission."
            )
        return value

    def create(self, validated_data):
        targets_data = validated_data.pop('targets')
        mission = Mission.objects.create(**validated_data)
        
        for target_data in targets_data:
            Target.objects.create(mission=mission, **target_data)
        
        return mission


class AssignCatSerializer(serializers.Serializer):
    cat_id = serializers.IntegerField()

    def validate_cat_id(self, value):
        try:
            cat = SpyCat.objects.get(id=value)
            if cat.has_active_mission():
                raise serializers.ValidationError(
                    f"Cat '{cat.name}' already has an active mission."
                )
            return value
        except SpyCat.DoesNotExist:
            raise serializers.ValidationError("Cat not found.")