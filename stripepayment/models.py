from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    prod_image = models.ImageField(upload_to='products/', null=True)
    price = models.IntegerField()

    def __str__(self):
        return self.name
    






