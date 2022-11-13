from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import APIException

from accounts.models import CandidatePost, CandidateProfile, User, VoterProfile


__all__ = (
    "CreateUserSerializer",
    "VoterProfileSerializer",
    "CandidateProfileSerializer",
    "CandidatePostSerializer",
    "LoginSerializer",
)


class PasswordsMismatch(APIException):
    status_code = 403
    default_detail = "Passwords mismatch"


class CreateUserSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "password_confirm"]
        wro_settings = {"write_only": True}
        extra_kwargs = {"password": wro_settings, "password_confirm": wro_settings}

    def create(self, validated_data):
        if validated_data["password"] == validated_data["password_confirm"]:
            user = User(
                username=validated_data["username"],
                is_active=True,
            )
            user.set_password(validated_data["password"])
            user.save()
            return user
        else:
            raise PasswordsMismatch()


class VoterProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoterProfile
        exclude = ("is_email_verified", "is_paid")

    def create(self, validated_data):
        voter_profile = VoterProfile(**validated_data)
        voter_profile.save()
        return voter_profile

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance


class CandidatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidatePost
        exclude = ("id",)

    def create(self, validated_data):
        post = CandidatePost(**validated_data)
        post.save()
        return post

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance


class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        exclude = ("is_email_verified",)

    def create(self, validated_data):
        candidate_profile = CandidateProfile(**validated_data)
        candidate_profile.save()
        return candidate_profile

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        try:
            user = User.objects.get(username=attrs["username"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not  Exist")
        if user.is_active:
            user = authenticate(username=attrs["username"], password=attrs["password"])
            if user is None:
                raise serializers.ValidationError("Incorrect username or password.")
        else:
            raise serializers.ValidationError("access denied")
        return {"user": user}
