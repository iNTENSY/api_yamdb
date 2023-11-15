from django.urls import path, include
from rest_framework import routers

from . import views
from .views import UserViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', views.SignUpAPIView.as_view(), name='signup'),
    path('v1/auth/token/', views.TokenAPIView.as_view(), name='token'),
]