from django.urls import path, include
from rest_framework import routers

from . import views


app_name = 'api'

router = routers.DefaultRouter()



urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', views.SignUpAPIView.as_view(), name='signup'),
    path('v1/auth/token/', views.TokenAPIView.as_view(), name='token'),
]