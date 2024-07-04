from rest_framework import serializers
from .models import Currency, ExchangeRate

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['code']

class ExchangeRateSerializer(serializers.ModelSerializer):
    base_currency_code = serializers.CharField(source='base_currency.code')
    target_currency_code = serializers.CharField(source='target_currency.code')

    class Meta:
        model = ExchangeRate
        fields = [
            'base_currency_code', 'target_currency_code', 'rate', 'date',
            'success', 'timestamp'
        ]

    def create(self, validated_data):
        base_currency_code = validated_data.pop('base_currency')['code']
        target_currency_code = validated_data.pop('target_currency')['code']

        base_currency, _ = Currency.objects.get_or_create(code=base_currency_code)
        target_currency, _ = Currency.objects.get_or_create(code=target_currency_code)

        return ExchangeRate.objects.create(base_currency=base_currency, target_currency=target_currency, **validated_data)