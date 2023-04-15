from django.db import models


class Deal(models.Model):
    customer = models.CharField(max_length=30)
    date = models.DateTimeField()
    item = models.CharField(max_length=30)
    quantity = models.IntegerField()
    total = models.IntegerField()

    def __str__(self):
    	return self.customer
