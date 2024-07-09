from django.urls import path
from .views import fetch_exchange_rates, list_exchange_rates, save_exchange_rates

urlpatterns = [
    path('load', fetch_exchange_rates, name='load'),
    path('save', save_exchange_rates, name='save_exchange_rates'),
    path('get', list_exchange_rates, name='get'),
]