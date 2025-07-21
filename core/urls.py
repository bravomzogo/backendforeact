# core/urls.py
from django.urls import path
from .views import (
    CategoryList, CategoryDetail,
    ProductList, ProductDetail,
    LandList, LandDetail,
    InputList, InputDetail,
    ServiceList, ServiceDetail,
    VideoList, VideoDetail,
    VideoYouTubeSearch,
    RegisterView, VerifyEmailView, LoginView, LogoutView, UserDetail,
    ResendVerificationView,CsrfTokenView
)

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/get-csrf/', CsrfTokenView.as_view(), name='get-csrf'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    path('api/user/', UserDetail.as_view(), name='user-detail'),
    path('api/categories/', CategoryList.as_view(), name='category-list'),
    path('api/categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),
    path('api/products/', ProductList.as_view(), name='product-list'),
    path('api/products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('api/land/', LandList.as_view(), name='land-list'),
    path('api/land/<int:pk>/', LandDetail.as_view(), name='land-detail'),
    path('api/inputs/', InputList.as_view(), name='input-list'),
    path('api/inputs/<int:pk>/', InputDetail.as_view(), name='input-detail'),
    path('api/services/', ServiceList.as_view(), name='service-list'),
    path('api/services/<int:pk>/', ServiceDetail.as_view(), name='service-detail'),
    path('api/videos/', VideoList.as_view(), name='video-list'),
    path('api/videos/<int:pk>/', VideoDetail.as_view(), name='video-detail'),
    path('api/videos/youtube_search/', VideoYouTubeSearch.as_view(), name='video-youtube-search'),
]