from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
from .models import Currency, ExchangeRate
from .serializers import ExchangeRateSerializer, CurrencySerializer
from datetime import datetime
from decimal import Decimal, InvalidOperation

# Global variable to temporarily hold fetched data
temp_data = {}

@api_view(['GET'])
def fetch_exchange_rates(request):
    global temp_data
    access_key = 'f638ce07b446f7a900ded80b837af730'
    url = f"http://api.exchangeratesapi.io/v1/latest?access_key={access_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'rates' in data:
            base_currency_code = 'USD'
            date = data['date']
            timestamp = datetime.utcfromtimestamp(data['timestamp']) if 'timestamp' in data else datetime.now()
            success = data.get('success', False)

            rates = data['rates']
            eur_to_usd_rate = rates.get('USD', None)

            if eur_to_usd_rate is None:
                return Response({"error": "USD rate not available in the API response"}, status=status.HTTP_400_BAD_REQUEST)

            fetched_data = []

            for code, rate in rates.items():
                try:
                    if code == 'USD':
                        converted_rate = Decimal(rate)
                    else:
                        converted_rate = Decimal(rate) / Decimal(eur_to_usd_rate)
                    
                    fetched_data.append({
                        'base_currency': base_currency_code,
                        'target_currency': code,
                        'rate': str(converted_rate),
                        'date': date,
                        'success': success,
                        'timestamp': timestamp,
                    })
                except InvalidOperation:
                    continue

            temp_data['exchange_rates'] = fetched_data
            return Response({"message": "Exchange rates fetched successfully", "data": fetched_data}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Unexpected API response format"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": f"API request failed with status code {response.status_code}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def save_exchange_rates(request):
    global temp_data

    user_response = request.data.get('response')
    if user_response is None:
        return Response({"error": "User response not provided"}, status=status.HTTP_400_BAD_REQUEST)

    if user_response.lower() == 'yes':
        try:
            ExchangeRate.objects.all().delete()
            for rate_data in temp_data.get('exchange_rates', []):
                base_currency, _ = Currency.objects.get_or_create(code=rate_data['base_currency'])
                target_currency, _ = Currency.objects.get_or_create(code=rate_data['target_currency'])

                ExchangeRate.objects.create(
                    base_currency=base_currency,
                    target_currency=target_currency,
                    rate=rate_data['rate'],
                    date=rate_data['date'],
                    success=rate_data['success'],
                    timestamp=rate_data['timestamp'],
                )

            temp_data = {}
            return Response({"message": "Exchange rates saved successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed to save exchange rates: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif user_response.lower() == 'no':
        temp_data = {}
        return Response({"message": "Exchange rates discarded"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid user response"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_exchange_rates(request):
    exchange_rates = ExchangeRate.objects.all()
    serializer = ExchangeRateSerializer(exchange_rates, many=True)
    return Response(serializer.data)
