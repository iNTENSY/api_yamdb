from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters

from reviews.models import Genre, Category, Title

from .serializers import GenreSerializer, CategorySerializer, TitleSerializer
from .permissions import IsAdminOrReadOnly


class GenreViewSet(viewsets.ModelViewSet):
    '''Вьюсет модели Genre'''
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = None
    search_fields = ('genre__name')

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = None
    search_fields = ('category__name')


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    filterset_fields = (
        'category__slug', 'genre__slug', 'name', 'year'
    )
