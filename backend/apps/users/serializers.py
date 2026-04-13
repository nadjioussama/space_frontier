from rest_framework import serializers
from .models import ParentAccount, Player


class PlayerProfileSerializer(serializers.ModelSerializer):
    safe_display_name = serializers.CharField(read_only=True)
    needs_parental_consent = serializers.BooleanField(read_only=True)

    class Meta:
        model = Player
        fields = (
            "id", "username", "display_name", "safe_display_name",
            "display_name_status", "age_group", "avatar_config",
            "is_under_13", "coppa_consent_given", "needs_parental_consent",
        )
        read_only_fields = ("id", "username", "display_name_status",
                            "coppa_consent_given")


class ParentRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=200)


class ConsentGrantSerializer(serializers.Serializer):
    parent_email = serializers.EmailField()
    player_id = serializers.IntegerField()


class NameChangeSerializer(serializers.Serializer):
    display_name = serializers.CharField(max_length=50, min_length=2)
