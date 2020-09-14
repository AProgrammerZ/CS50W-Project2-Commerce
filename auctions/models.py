from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

def testing_function():
    pass

class Auction(models.Model):
    username = models.CharField(max_length=50)
    title = models.CharField(max_length=64)
    price = models.CharField(max_length=64)
    description = models.CharField(max_length=100)
    creation_date = models.DateTimeField()
    photo = models.FileField(null=True, blank=True)
    category = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    winner = models.CharField(max_length=50, blank=True)

class Bids(models.Model):
    listing = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="b_listing")
    username = models.CharField(max_length=50)
    bid_price = models.DecimalField(decimal_places=2, max_digits=20)    

class Comments(models.Model):
    listing = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="c_listing")
    username = models.CharField(max_length=50)
    date = models.DateTimeField()
    text = models.CharField(max_length=500)

class Watchlist(models.Model):
    username = models.CharField(max_length=50)
    listing = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="w_listing")

                        # AFTER EACH CHANGE:

# python3 manage.py makemigrations
# python3 manage.py migrate
