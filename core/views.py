import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import User, Category, Product, Land, Input, Service, Video
from .serializers import (
    RegisterSerializer, VerifyEmailSerializer, UserSerializer,
    CategorySerializer, ProductSerializer, LandSerializer,
    InputSerializer, ServiceSerializer, VideoSerializer
)

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate verification code
            verification_code = user.generate_verification_code()
            
            # Send email
            subject = 'Verify Your KilimoPesa Account'
            message = f"""
            Hello {user.username},
            
            Your verification code is: {verification_code}
            
            Enter this code in the app to complete your registration.
            
            The KilimoPesa Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            return Response({
                'message': 'Verification code sent to your email',
                'email': user.email,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            
            try:
                user = User.objects.get(email=email)
                if user.verification_code == code:
                    user.is_email_verified = True
                    user.verification_code = None
                    user.save()
                    return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
                return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class ProductList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            # Ensure the user can only update their own products
            if product.user != request.user:
                return Response({'error': 'You do not have permission to update this product'}, 
                              status=status.HTTP_403_FORBIDDEN)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        if product.user != request.user:
            return Response({'error': 'You do not have permission to delete this product'}, 
                          status=status.HTTP_403_FORBIDDEN)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LandList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        lands = Land.objects.all()
        serializer = LandSerializer(lands, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LandDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Land, pk=pk)

    def get(self, request, pk):
        land = self.get_object(pk)
        serializer = LandSerializer(land)
        return Response(serializer.data)

    def put(self, request, pk):
        land = self.get_object(pk)
        serializer = LandSerializer(land, data=request.data, partial=True)
        if serializer.is_valid():
            if land.user != request.user:
                return Response({'error': 'You do not have permission to update this land'}, 
                              status=status.HTTP_403_FORBIDDEN)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        land = self.get_object(pk)
        if land.user != request.user:
            return Response({'error': 'You do not have permission to delete this land'}, 
                          status=status.HTTP_403_FORBIDDEN)
        land.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class InputList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        inputs = Input.objects.all()
        serializer = InputSerializer(inputs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InputSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InputDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Input, pk=pk)

    def get(self, request, pk):
        input_item = self.get_object(pk)
        serializer = InputSerializer(input_item)
        return Response(serializer.data)

    def put(self, request, pk):
        input_item = self.get_object(pk)
        serializer = InputSerializer(input_item, data=request.data, partial=True)
        if serializer.is_valid():
            if input_item.user != request.user:
                return Response({'error': 'You do not have permission to update this input'}, 
                              status=status.HTTP_403_FORBIDDEN)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        input_item = self.get_object(pk)
        if input_item.user != request.user:
            return Response({'error': 'You do not have permission to delete this input'}, 
                          status=status.HTTP_403_FORBIDDEN)
        input_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ServiceList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Service, pk=pk)

    def get(self, request, pk):
        service = self.get_object(pk)
        serializer = ServiceSerializer(service)
        return Response(serializer.data)

    def put(self, request, pk):
        service = self.get_object(pk)
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            if service.user != request.user:
                return Response({'error': 'You do not have permission to update this service'}, 
                              status=status.HTTP_403_FORBIDDEN)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        service = self.get_object(pk)
        if service.user != request.user:
            return Response({'error': 'You do not have permission to delete this service'}, 
                          status=status.HTTP_403_FORBIDDEN)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class VideoList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VideoDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Video, pk=pk)

    def get(self, request, pk):
        video = self.get_object(pk)
        serializer = VideoSerializer(video)
        return Response(serializer.data)

    def put(self, request, pk):
        video = self.get_object(pk)
        serializer = VideoSerializer(video, data=request.data, partial=True)
        if serializer.is_valid():
            if video.user != request.user:
                return Response({'error': 'You do not have permission to update this video'}, 
                              status=status.HTTP_403_FORBIDDEN)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        video = self.get_object(pk)
        if video.user != request.user:
            return Response({'error': 'You do not have permission to delete this video'}, 
                          status=status.HTTP_403_FORBIDDEN)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

class CategoryDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Category, pk=pk)

    def get(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

class VideoYouTubeSearch(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        query = request.query_params.get('q', 'agriculture')
        url = 'https://www.googleapis.com/youtube/v3/search'
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'key': settings.YOUTUBE_API_KEY,
            'maxResults': 10
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return Response(response.json())
        return Response({'error': 'Failed to fetch YouTube videos'}, status=response.status_code)
    



    