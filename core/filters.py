from rest_framework.filters import BaseFilterBackend
from django_filters import rest_framework as django_filters
from .models import Country

class CountryFilter(django_filters.FilterSet):
    # this maps the query param 'currency' to the model field 'currency_code'
    # and performs a case-insensitive match (iexact).
    currency = django_filters.CharFilter(
        field_name='currency_code', 
        lookup_expr='iexact'
    )

    # this maps 'region' to 'region' (iexact)
    region = django_filters.CharFilter(
        field_name='region', 
        lookup_expr='iexact'
    )

    class Meta:
        model = Country
        fields = ['region', 'currency']


class CustomSortFilter(BaseFilterBackend):
    # filter to handle the 'sort=gdp_desc' parameter.
    def filter_queryset(self, request, queryset, view):
        sort_param = request.query_params.get('sort')

        if sort_param == 'gdp_desc':
            return queryset.order_by('-estimated_gdp')
        
        return queryset