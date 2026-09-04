from django.contrib import admin
from .models import Restaurant,Review,Profile
# Register your models here.
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name','city','cuisine','food_type','has_parking','image')
    list_filter = ('city','food_type','has_parking')
    search_fields = ('name','city','cuisine')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant','user','quantity_rating','quality_rating','staff_rating','created_at')
    list_filter = ('restaurant','quality_rating')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'picture')