from django.urls import path
from .views import EnergyForecastAPI

urlpatterns = [
    path('energy-forecast/', EnergyForecastAPI.as_view(), name='energy_forecast'),
]
