from rest_framework import serializers
from .models import Car, CarImage, Feature

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'name', 'icon_name']


class CarImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CarImage
        fields = ['id', 'image', 'image_url', 'is_cover', 'order', 'caption']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class CarSerializer(serializers.ModelSerializer):
    images = CarImageSerializer(many=True, read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    formatted_price = serializers.ReadOnlyField()
    formatted_mileage = serializers.ReadOnlyField()
    cover_image_url = serializers.SerializerMethodField()
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    transmission_display = serializers.CharField(source='get_transmission_display', read_only=True)
    fuel_display = serializers.CharField(source='get_fuel_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Car
        fields = [
            'id', 'make', 'model', 'year', 'price', 'formatted_price',
            'mileage', 'formatted_mileage', 'condition', 'condition_display',
            'transmission', 'transmission_display', 'fuel_type', 'fuel_display',
            'body_type', 'engine', 'exterior_color', 'interior_color',
            'location', 'status', 'status_display', 'is_featured',
            'description', 'vin', 'slug', 'features', 'images',
            'cover_image_url', 'created_at', 'updated_at'
        ]

    def get_cover_image_url(self, obj):
        cover = obj.get_cover_image()
        if cover and cover.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(cover.image.url)
            return cover.image.url
        return None
