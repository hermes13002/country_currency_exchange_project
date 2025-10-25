import os
from django.conf import settings
from django.http import Http404, FileResponse
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters import rest_framework as django_filters

from .models import Country, RefreshLog
from .serializers import CountrySerializer, RefreshLogSerializer
from .services import run_country_refresh, ExternalApiException
from .filters import CountryFilter, CustomSortFilter

class RefreshCountriesView(APIView):
    def post(self, request, *args, **kwargs):
        try:
        
            count = run_country_refresh()
            return Response(
                {"status": "success", "message": f"Successfully refreshed {count} countries."},
                status=status.HTTP_200_OK
            )
        except ExternalApiException as e:
            return Response(
                {"error": "External data source unavailable", "details": f"Could not fetch data from {e.api_name}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CountryListView(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    
    filter_backends = [django_filters.DjangoFilterBackend, CustomSortFilter]
    filterset_class = CountryFilter


class CountryDetailView(generics.RetrieveDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    

    lookup_field = 'name' 

    def get_object(self):
        name = self.kwargs.get(self.lookup_field)
        try:
        
            obj = Country.objects.get(name__iexact=name)
            return obj
        except Country.DoesNotExist:
        
            raise Http404({"error": "Country not found"})


class StatusView(APIView):
    def get(self, request, *args, **kwargs):
        log = RefreshLog.objects.first()
        
        if not log:
            return Response(
                {"error": "No refresh has been performed yet."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = RefreshLogSerializer(log)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SummaryImageView(APIView):
    def get(self, request, *args, **kwargs):
        image_path = settings.SUMMARY_IMAGE_PATH
    
        if not os.path.exists(image_path):
            return Response(
                {"error": "Summary image not found"},
                status=status.HTTP_404_NOT_FOUND
            )        
        try:
            return FileResponse(open(image_path, 'rb'), content_type='image/png')
        except Exception as e:
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )