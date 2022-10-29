from rest_framework import serializers

from ads.models import Location
from user.models import User


class UserCommonSerializer(serializers.ModelSerializer):
    locations = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'role',
            'age',
            'locations',
        )


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    locations = serializers.SlugRelatedField(
        required=False,
        many=True,
        queryset=Location.objects.all(),
        slug_field='name'
    )

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'first_name',
            'last_name',
            'role',
            'age',
            'locations',
        )

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def is_valid(self, raise_exception=False):
        self._locations = self.initial_data.pop('locations')
        return super().is_valid(raise_exception=raise_exception)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()

        for location in self._locations:
            location_instance, _ = Location.objects.get_or_create(name=location)
            user.locations.add(location_instance)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()

        for location in self._locations:
            location_instance, _ = Location.objects.get_or_create(name=location)
            instance.locations.add(location_instance)
        return instance
