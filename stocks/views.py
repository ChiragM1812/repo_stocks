from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
from .models import Currency, ExchangeRate
from .serializers import ExchangeRateSerializer, CurrencySerializer
from datetime import datetime
from decimal import Decimal, InvalidOperation

@api_view(['GET'])
def fetch_exchange_rates(request):
    access_key = 'f638ce07b446f7a900ded80b837af730'
    url = f"http://api.exchangeratesapi.io/v1/latest?access_key={access_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'rates' in data:
            # Change base currency code to USD
            base_currency_code = 'USD'
            base_currency, created = Currency.objects.get_or_create(code=base_currency_code)
            if created:
                base_currency.save()

            date = data['date']
            timestamp = datetime.utcfromtimestamp(data['timestamp']) if 'timestamp' in data else datetime.now()
            success = data.get('success', False)

            rates = data['rates']
            eur_to_usd_rate = rates.get('USD', None)

            if eur_to_usd_rate is None:
                return Response({"error": "USD rate not available in the API response"}, status=status.HTTP_400_BAD_REQUEST)

            # Clear old data
            ExchangeRate.objects.all().delete()

            for code, rate in rates.items():
                try:
                    if code == 'USD':
                        converted_rate = Decimal(rate)
                    else:
                        converted_rate = Decimal(rate) / Decimal(eur_to_usd_rate)
                    
                    target_currency, created = Currency.objects.get_or_create(code=code)
                    if created:
                        target_currency.save()
                    
                    ExchangeRate.objects.create(
                        base_currency=base_currency,
                        target_currency=target_currency,
                        rate=converted_rate,
                        date=date,
                        success=success,
                        timestamp=timestamp,
                    )
                except InvalidOperation:
                    continue

            return Response({"message": "Exchange rates fetched and saved successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Unexpected API response format"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": f"API request failed with status code {response.status_code}"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def list_exchange_rates(request):
    exchange_rates = ExchangeRate.objects.all()
    serializer = ExchangeRateSerializer(exchange_rates, many=True)
    return Response(serializer.data)

