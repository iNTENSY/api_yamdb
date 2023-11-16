from django.urls import path, include
from rest_framework import routers

from .views import UserViewSet, SignUpAPIView, TokenAPIView, GenreViewSet, CategoryViewSet, TitleViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'titles', TitleViewSet, basename='titles')


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', SignUpAPIView.as_view(), name='signup'),
    path('v1/auth/token/', TokenAPIView.as_view(), name='token'),
]