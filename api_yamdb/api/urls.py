from django.urls import path, include

from rest_framework.routers import DefaultRouter
from api.views import GenreViewSet, CategoryViewSet, TitleViewSet


router = DefaultRouter()
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('', include(router.urls)),
]
