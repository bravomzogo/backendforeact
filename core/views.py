# core/views.py
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import User, Category, Product, Land, Input, Service, Video
from .serializers import (
    RegisterSerializer, VerifyEmailSerializer, UserSerializer,
    CategorySerializer, ProductSerializer, LandSerializer,
    InputSerializer, ServiceSerializer, VideoSerializer
)
import logging
import requests

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    def post(self, request):
        logger.debug(f"Register request received: {request.data}")
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False  # User can't login until email is verified
            verification_code = user.generate_verification_code()
            
            # Prepare email content
            subject = 'Verify Your KilimoPesa Account'
            html_message = render_to_string('email/verification_email.html', {
                'username': user.username,
                'verification_code': verification_code,
            })
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                logger.info(f"Verification email sent to {user.email}")
                return Response({
                    'message': 'Verification code sent to your email',
                    'email': user.email,
                    'username': user.username
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"Failed to send email to {user.email}: {str(e)}")
                user.delete()
                return Response(
                    {'error': f'Failed to send verification email: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    def post(self, request):
        logger.debug(f"Verify email request received: {request.data}")
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code'].strip()
            
            try:
                user = User.objects.get(email=email)
                
                if user.is_email_verified:
                    return Response(
                        {'error': 'Email is already verified'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if not user.verification_code:
                    return Response(
                        {'error': 'No verification code exists for this user'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if user.verification_code == code:
                    user.is_email_verified = True
                    user.is_active = True
                    user.verification_code = None
                    user.save()
                    
                    login(request, user)
                    logger.info(f"Email verified for {user.email}")
                    return Response({
                        'message': 'Email verified successfully',
                        'user': UserSerializer(user).data
                    }, status=status.HTTP_200_OK)
                
                logger.error(f"Invalid verification code for {email}")
                return Response(
                    {'error': 'Invalid verification code'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            except User.DoesNotExist:
                logger.error(f"User with email {email} not found")
                return Response(
                    {'error': 'User with this email does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        logger.debug(f"Login request received: {request.data}")
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            logger.error("Email or password missing")
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user = authenticate(request, email=email, password=password)
        
        if user is None:
            logger.error(f"Invalid credentials for {email}")
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        if not user.is_email_verified:
            logger.error(f"Unverified email for {email}")
            return Response(
                {'error': 'Please verify your email first'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        login(request, user)
        logger.info(f"Login successful for {email}")
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logger.info(f"Logout request for {request.user.email}")
        logout(request)
        return Response({
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)

class ResendVerificationView(APIView):
    def post(self, request):
        logger.debug(f"Resend verification request: {request.data}")
        email = request.data.get('email')
        if not email:
            logger.error("Email missing for resend verification")
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            user = User.objects.get(email=email)
            
            if user.is_email_verified:
                logger.error(f"Email already verified for {email}")
                return Response(
                    {'error': 'Email is already verified'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            verification_code = user.generate_verification_code()
            
            subject = 'Your New Verification Code'
            html_message = render_to_string('email/verification_email.html', {
                'username': user.username,
                'verification_code': verification_code,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Resent verification email to {email}")
            return Response({
                'message': 'New verification code sent',
                'email': user.email
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            logger.error(f"User with email {email} not found")
            return Response(
                {'error': 'User with this email does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

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
    



# core/views.py
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

class CsrfTokenView(APIView):
    def get(self, request):
        logger.debug("Fetching CSRF token")
        csrf_token = get_token(request)
        return Response({'csrfToken': csrf_token}, status=status.HTTP_200_OK)