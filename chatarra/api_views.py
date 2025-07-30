from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, CharFilter
from cataliticos.models import ProductoChatarra
from .serializers import ProductoChatarraSerializer

class ProductoChatarraFilter(FilterSet):
    categoria = CharFilter(field_name='categoria', lookup_expr='icontains')
    precio_min = NumberFilter(field_name='precio_kg', lookup_expr='gte')
    precio_max = NumberFilter(field_name='precio_kg', lookup_expr='lte')
    search = CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            nombre__icontains=value
        ) | queryset.filter(
            codigo__icontains=value
        )

    class Meta:
        model = ProductoChatarra
        fields = ['categoria', 'precio_min', 'precio_max', 'search']

from rest_framework.pagination import PageNumberPagination

class CatalogoChatarraPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CatalogoChatarraAPI(generics.ListAPIView):
    queryset = ProductoChatarra.objects.all().order_by('nombre')
    serializer_class = ProductoChatarraSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProductoChatarraFilter
    ordering_fields = ['precio_kg', 'nombre']
    pagination_class = CatalogoChatarraPagination
