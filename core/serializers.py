from rest_framework import serializers
from .models import Country, RefreshLog

class CountrySerializer(serializers.ModelSerializer):
    # serializer for the Country model.
    class Meta:
        model = Country
        fields = [
            'id',
            'name',
            'capital',
            'region',
            'population',
            'currency_code',
            'exchange_rate',
            'estimated_gdp',
            'flag_url',
            'last_refreshed_at'
        ]
        extra_kwargs = {
            'name': {'required': True},
            'population': {'required': True},
            'currency_code': {'required': True, 'allow_null': False} 
        }


class RefreshLogSerializer(serializers.ModelSerializer):
    # serializer for the GET /status endpoint.
    class Meta:
        model = RefreshLog
        fields = ['total_countries', 'last_refreshed_at']