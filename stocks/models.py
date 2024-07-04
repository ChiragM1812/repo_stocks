from django.db import models

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.code

class ExchangeRate(models.Model):
    base_currency = models.ForeignKey(Currency, related_name='base_currency', on_delete=models.CASCADE)
    target_currency = models.ForeignKey(Currency, related_name='target_currency', on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=20, decimal_places=10)
    date = models.DateField()
    success = models.BooleanField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.base_currency} to {self.target_currency} rate on {self.date}"
    