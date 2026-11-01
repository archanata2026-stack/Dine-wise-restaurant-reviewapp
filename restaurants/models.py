from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
class Restaurant(models.Model):
    VEG = 'VEG'
    NON_VEG = 'NON_VEG'
    BOTH = 'BOTH'
    FOOD_TYPE_CHOICES = [(VEG,'Vegetarian Only'),(NON_VEG,'Non-Vegetarian Only'),(BOTH,'Both Veg and Non-Veg')]

    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    cuisine = models.CharField(max_length=200)
    food_type = models.CharField(choices=FOOD_TYPE_CHOICES, max_length=20, default=BOTH)
    has_parking = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='restaurant_pics/', blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name

    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return None
        avg = reviews.aggregate(
            avg_quality=Avg('quality_rating'),
            avg_quantity=Avg('quantity_rating'),
            avg_staff=Avg('staff_rating'),
        )
        overall = (avg['avg_quality'] + avg['avg_quantity'] + avg['avg_staff']) / 3
        return round(overall, 1)

    def review_count(self):
        return self.reviews.count()


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1,6)]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quality_rating = models.IntegerField(choices=RATING_CHOICES)
    quantity_rating = models.IntegerField(choices=RATING_CHOICES)
    staff_rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s review of {self.restaurant.name}"

    def average_rating(self):
        return round(
            (self.quality_rating + self.quantity_rating + self.staff_rating) / 3,
            1
        )

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png')

    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()