from django.urls import path
from .views import fetch_exchange_rates, list_exchange_rates

urlpatterns = [
    path('load', fetch_exchange_rates, name='oad'),
    path('get', list_exchange_rates, name='get'),
]
