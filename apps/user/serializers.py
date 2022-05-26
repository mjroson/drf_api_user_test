import uuid

from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import Group

from rest_framework import serializers

from .services.subscription import SubscriptionService

User = get_user_model()


class BaseUserModelSerializer(serializers.ModelSerializer):
    """
        Common handler user serializer.
    """
    repeat_password = serializers.CharField(write_only=True, max_length=128, required=False)

    def validate(self, data):
        passwd = data.get('password')
        repeat_password = data.get('repeat_password')

        if passwd != repeat_password:
            raise serializers.ValidationError("Passwords do not match")

        if passwd:
            password_validation.validate_password(passwd)

        return data

    def create(self, data):
        data.pop('repeat_password')

        # Generate uuid to represent de ID for the new user.
        new_uuid = uuid.uuid4()
        # Esto tiene sentido ? Como una subscripcion puede ser activa de un uuid que se acaba de generar?
        subscription = SubscriptionService.is_user_suscribed(new_uuid)

        user = User.objects.create_user(subscription=subscription, id=new_uuid, **data)

        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)

        passwd = validated_data.get("password")
        if passwd:
            instance.set_password(passwd)

        instance.save()
        return instance

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "repeat_password"
        ]
        extra_kwargs = {
            'password': {'write_only': True, "required": False}
        }


class GroupListField(serializers.ListField):
    """
        ListField to handler groups list nested UserSerializer.
    """
    def to_representation(self, value):
        return value.values_list("name", flat=True)


class UserModelSerializer(BaseUserModelSerializer):
    """
        Serializer to handler API user for staff user or superuser
    """
    groups = GroupListField(
        child=serializers.CharField(min_length=1, max_length=150)
    )

    def create(self, data):
        groups = data.pop('groups')

        user = super().create(data)

        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

        return user

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        groups = validated_data.get("groups", [])

        instance.groups.clear()

        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            instance.groups.add(group)

        return instance

    class Meta:
        model = User
        fields = BaseUserModelSerializer.Meta.fields + [
            "groups",
            "created",
            "subscription",
            "updated",
        ]
        extra_kwargs = {'password': {'write_only': True}}


class MinimalUserModelSerializer(BaseUserModelSerializer):
    """
        Serializer to handler API user for common user
    """
    old_password = serializers.CharField(write_only=True, max_length=128)

    def validate(self, data):
        if data.get("passwd"):
            # assume self instance is not null because
            # this serializer not use for create an user.
            if not self.instance.check_password(data["old_password"]):
                raise serializers.ValidationError("The old password is incorrect.")

        super().validate(data)

        return data

    class Meta:
        model = User
        fields = BaseUserModelSerializer.Meta.fields + ["old_password"]
        extra_kwargs = {'password': {'write_only': True}}
