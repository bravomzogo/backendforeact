from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Product, Land, Input, Service, Video

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_email_verified']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.generate_verification_code()
        return user

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    user = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ['id', 'user', 'category', 'name', 'description', 'price', 'quantity', 'image', 'created_at', 'updated_at']

class LandSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Land
        fields = ['id', 'user', 'title', 'description', 'size', 'location', 'price', 'is_for_sale', 'image', 'created_at', 'updated_at']

class InputSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Input
        fields = ['id', 'user', 'name', 'description', 'price', 'quantity', 'image', 'created_at', 'updated_at']

class ServiceSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Service
        fields = ['id', 'user', 'title', 'description', 'price', 'location', 'image', 'created_at', 'updated_at']

class VideoSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Video
        fields = ['id', 'title', 'youtube_video_id', 'description', 'user', 'created_at', 'updated_at']