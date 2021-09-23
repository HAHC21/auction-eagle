from typing import Optional
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import AutoField


class User(AbstractUser):
    id = models.AutoField(primary_key=True)

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"Category: {self.name}"

class Listing(models.Model):
    identifier = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    title = models.CharField(max_length=256)
    category = models.ForeignKey(Category, blank=True, on_delete=models.CASCADE, default=None)
    description = models.CharField(max_length=1024)
    starting_bid = models.FloatField(default=0)
    current_bid = models.FloatField(default=0)
    current_winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="highest_bidder")
    listing_status = models.IntegerField(default=1)
    image_url = models.CharField(max_length=100, blank=True, default=None)

    def __str__(self):
        return f"Listing #{self.identifier}: '{self.title}' by {self.author}"

class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default=None)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    amount = models.FloatField()

    def __str__(self):
        return f"Bid by {self.bidder} on Listing ID {self.listing}"

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default=None)
    text = models.CharField(max_length=512)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return f"Comment by {self.author} on Listing ID {self.listing}"

class Watchlist(models.Model):
    id = models.AutoField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default=None)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return f"Watchlist Item #{self.id}, User: {self.author}, Listing: {self.listing}"