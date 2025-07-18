from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core.views import (
    CategoryList, CategoryDetail,
    ProductList, ProductDetail,
    LandList, LandDetail,
    InputList, InputDetail,
    ServiceList, ServiceDetail,
    VideoList, VideoDetail, VideoYouTubeSearch,    RegisterView, VerifyEmailView, UserDetail,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('user/', UserDetail.as_view(), name='user-detail'),
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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)