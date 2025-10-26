from django.urls import path
from . import views

urlpatterns = [
    # POST /countries/refresh
    path(
        'countries/refresh', 
        views.RefreshCountriesView.as_view(), 
        name='country-refresh'
    ),
    
    # GET /countries
    path(
        'countries', 
        views.CountryListView.as_view(), 
        name='country-list'
    ),
    
    # GET /countries/image
    path(
        'countries/image', 
        views.SummaryImageView.as_view(), 
        name='summary-image'
    ),

    # GET, DELETE /countries/:name
    path(
        'countries/<str:name>', 
        views.CountryDetailView.as_view(), 
        name='country-detail'
    ),
    
    # GET /status
    path(
        'status', 
        views.StatusView.as_view(), 
        name='status'
    ),
]