from rest_framework import serializers
from .models import Category, Product, Land, Input, Service, Video

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    farmer = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ['id', 'farmer', 'category', 'name', 'description', 'price', 'quantity', 'image', 'created_at', 'updated_at']

class LandSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()

    class Meta:
        model = Land
        fields = ['id', 'owner', 'title', 'description', 'size', 'location', 'price', 'is_for_sale', 'image', 'created_at', 'updated_at']

class InputSerializer(serializers.ModelSerializer):
    seller = serializers.StringRelatedField()

    class Meta:
        model = Input
        fields = ['id', 'seller', 'name', 'description', 'price', 'quantity', 'image', 'created_at', 'updated_at']

class ServiceSerializer(serializers.ModelSerializer):
    provider = serializers.StringRelatedField()

    class Meta:
        model = Service
        fields = ['id', 'provider', 'title', 'description', 'price', 'location', 'image', 'created_at', 'updated_at']

class VideoSerializer(serializers.ModelSerializer):
    added_by = serializers.StringRelatedField()

    class Meta:
        model = Video
        fields = ['id', 'title', 'youtube_video_id', 'description', 'added_by', 'created_at', 'updated_at']