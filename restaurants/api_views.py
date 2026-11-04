from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Restaurant, Review
from .serializers import RestaurantSerializer, ReviewSerializer
from .events import publish_review_event

class RestaurantListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Restaurant.objects.all()
        city = self.request.query_params.get('city')
        cuisine = self.request.query_params.get('cuisine')
        food_type = self.request.query_params.get('food_type')
        if city:
            queryset = queryset.filter(city__icontains=city)
        if cuisine:
            queryset = queryset.filter(cuisine__icontains=cuisine)
        if food_type:
            queryset = queryset.filter(food_type=food_type)
        return queryset


class RestaurantDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(restaurant_id=self.kwargs['restaurant_pk'])

    def perform_create(self, serializer):
        restaurant = Restaurant.objects.get(pk=self.kwargs['restaurant_pk'])
        review = serializer.save(user=self.request.user, restaurant=restaurant)
        publish_review_event(review)
        serializer.save(user=self.request.user, restaurant=restaurant)


class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(restaurant_id=self.kwargs['restaurant_pk'])

    def perform_update(self, serializer):
        review = self.get_object()
        if review.user != self.request.user:
            raise PermissionDenied("You can only edit your own reviews.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own reviews.")
        instance.delete()