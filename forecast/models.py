from django.db import models


class StockData(models.Model):
    ticket = models.CharField('ticket', max_length=350)
    period = models.CharField('period', max_length=2)
    date = models.DateField('date')
    time = models.TimeField('time')
    open = models.DecimalField(max_digits=21, decimal_places=10)
    high = models.DecimalField(max_digits=21, decimal_places=10)
    low = models.DecimalField(max_digits=21, decimal_places=10)
    close = models.DecimalField(max_digits=21, decimal_places=10)
    volume = models.DecimalField(max_digits=21, decimal_places=10)

    class Meta:
        unique_together = [['ticket', 'period', 'date', 'time']]



