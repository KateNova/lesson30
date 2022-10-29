from rest_framework import serializers

from ads.models import Location, Ad, Selection


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = '__all__'


class AdSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Ad
        fields = (
            'id',
            'name',
            'author',
            'price'
        )


class AdDetailSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Ad
        fields = '__all__'
        read_only_fields = ('image', )


class SelectionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Selection
        fields = ('id', 'name', 'owner', 'items')
        read_only_fields = ('owner', )


class SelectionDetailsSerializer(serializers.ModelSerializer):
    items = AdDetailSerializer(many=True)

    class Meta:
        model = Selection
        fields = ('id', 'name', 'owner', 'items')


class SelectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Selection
        fields = ('id', 'name')
