from django.urls import path
from . import views

urlpatterns = [
    # POST /api/countries/refresh
    path(
        'countries/refresh', 
        views.RefreshCountriesView.as_view(), 
        name='country-refresh'
    ),
    
    # GET /api/countries
    path(
        'countries', 
        views.CountryListView.as_view(), 
        name='country-list'
    ),
    
    # GET /api/countries/image
    path(
        'countries/image', 
        views.SummaryImageView.as_view(), 
        name='summary-image'
    ),

    # GET, DELETE /api/countries/:name
    path(
        'countries/<str:name>', 
        views.CountryDetailView.as_view(), 
        name='country-detail'
    ),
    
    # GET /api/status
    path(
        'status', 
        views.StatusView.as_view(), 
        name='status'
    ),
]