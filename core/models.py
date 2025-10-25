from django.db import models

class Country(models.Model):
    # this model is for storing cached country data.
    
    name = models.CharField(max_length=255, unique=True, db_index=True)
    capital = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    population = models.BigIntegerField() # we use BigIntegerField for large populations
    # currency_code can be null based on the refresh logic
    currency_code = models.CharField(max_length=10, null=True, blank=True, db_index=True)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True) # using DecimalField for precision
    estimated_gdp = models.DecimalField(max_digits=30, decimal_places=6, null=True, blank=True)
    flag_url = models.URLField(max_length=500, null=True, blank=True)
    # this timestamp updates every time the record is saved (created or updated)
    last_refreshed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name

class RefreshLog(models.Model):
    # model to store the timestamp of the last successful global refresh. We will only ever have one entry in this table.
    last_refreshed_at = models.DateTimeField()
    total_countries = models.IntegerField(default=0)

    def __str__(self):
        return f"Last refresh at {self.last_refreshed_at} with {self.total_countries} countries"