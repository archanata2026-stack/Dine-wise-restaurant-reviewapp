from rest_framework import serializers
from .models import Restaurant, Review


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'restaurant', 'user', 'username', 'quality_rating',
                  'quantity_rating', 'staff_rating', 'comment', 'created_at']
        read_only_fields = ['restaurant', 'user', 'created_at']


class RestaurantSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'city', 'cuisine', 'food_type',
                  'has_parking', 'description', 'image', 'created_on',
                  'average_rating', 'review_count', 'reviews']

    def get_average_rating(self, obj):
        return obj.average_rating()

    def get_review_count(self, obj):
        return obj.review_count()