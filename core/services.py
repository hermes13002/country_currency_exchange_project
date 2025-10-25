import requests
import random
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.utils import timezone
from .models import Country, RefreshLog
from django.conf import settings

from .image_generator import generate_summary_image

COUNTRIES_API_URL = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
RATES_API_URL = "https://open.er-api.com/v6/latest/USD"

class ExternalApiException(Exception):
    # exception for external API failures
    def __init__(self, message, api_name):
        super().__init__(message)
        self.api_name = api_name


def _fetch_countries_data():
    # fetches raw country data from the restcountries API
    try:
        response = requests.get(COUNTRIES_API_URL, timeout=10)
        response.raise_for_status() 
        return response.json()
    except requests.RequestException as e:
        # catch connection errors, timeouts, and HTTP errors
        raise ExternalApiException(str(e), "restcountries.com")

def _fetch_exchange_rates():
    # fetches the latest USD exchange rates from open.er-api
    try:
        response = requests.get(RATES_API_URL, timeout=10)
        response.raise_for_status()
        return response.json().get('rates', {})
    except requests.RequestException as e:
        raise ExternalApiException(str(e), "open.er-api.com")

def _calculate_gdp(population, exchange_rate):
    # calculates the estimated GDP using a new random multiplier
    multiplier = Decimal(random.randint(1000, 2000))
    pop = Decimal(population)
    rate = Decimal(exchange_rate)

    if rate == 0:
        return None

    gdp = (pop * multiplier) / rate

    # round to 6 decimal places
    return gdp.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)

def run_country_refresh():
    print("Starting country data refresh service...")
    
    countries_data = _fetch_countries_data()
    rates_data = _fetch_exchange_rates()
    
    print(f"Fetched {len(countries_data)} countries and {len(rates_data)} exchange rates.")
    
    processed_countries_count = 0
    
    # save to DB in an atomic transaction
    # this ensures that if any country fails to save, the entire refresh is rolled back. No partial updates.
    try:
        with transaction.atomic():
            for country_raw in countries_data:
                
                name = country_raw.get('name')
                population = country_raw.get('population')

                if not name or population is None:
                    print(f"Skipping record with missing name or population: {country_raw.get('name')}")
                    continue

                currency_code = None
                exchange_rate = None
                estimated_gdp = None
                
                currencies = country_raw.get('currencies', [])
                
                if currencies and isinstance(currencies, list) and len(currencies) > 0:
                    first_currency = currencies[0]
                    if first_currency and isinstance(first_currency, dict):
                         currency_code = first_currency.get('code')

                if currency_code:
                    exchange_rate = rates_data.get(currency_code)

                if exchange_rate:
                    estimated_gdp = _calculate_gdp(population, exchange_rate)
                elif not currency_code:
                    estimated_gdp = 0
                Country.objects.update_or_create(
                    name__iexact=name,
                    defaults={
                        'name': name,
                        'capital': country_raw.get('capital'),
                        'region': country_raw.get('region'),
                        'population': population,
                        'flag_url': country_raw.get('flag'),
                        'currency_code': currency_code,
                        'exchange_rate': exchange_rate,
                        'estimated_gdp': estimated_gdp,
                        # 'last_refreshed_at' is updated automatically by auto_now=True
                    }
                )
                processed_countries_count += 1
            
            # delete any old log and create the new one
            RefreshLog.objects.all().delete()
            RefreshLog.objects.create(
                last_refreshed_at=timezone.now(),
                total_countries=processed_countries_count
            )
            print(f"Database transaction successful. Processed {processed_countries_count} countries.")

    except Exception as e:
        print(f"Database transaction failed: {e}")
        raise Exception(f"Database update failed: {e}")

    try:
        print("Generating summary image...")
        generate_summary_image()
        print("Summary image generation complete.")
    except Exception as e:
        print(f"Warning: Data refresh successful, but summary image generation failed: {e}")

    return processed_countries_count