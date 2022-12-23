from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Categories(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return self.category

class Listings(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=200)
    starting_bid = models.FloatField()
    image = models.CharField(max_length=600)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='user')
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, blank=True, related_name='categories')
    watchlist = models.ManyToManyField(User, blank=True, related_name='user_watchlist')

    def __str__(self):
        return self.title

class Bids(models.Model):
    bid = models.FloatField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='bid_author')
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, blank=True, related_name='bid_listing')

    def __str__(self):
        return self.bid

class Comments(models.Model):
    comment = models.CharField(max_length=300)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='comment_author')
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, blank=True, related_name='comment_listing')

    def __str__(self):
        return self.comment
