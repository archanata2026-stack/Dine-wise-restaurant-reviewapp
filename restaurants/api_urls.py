from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .api_views import (
    RestaurantListCreateAPIView, RestaurantDetailAPIView,
    ReviewListCreateAPIView, ReviewDetailAPIView
)

urlpatterns = [
    path('restaurants/', RestaurantListCreateAPIView.as_view(), name='api_restaurant_list'),
    path('restaurants/<int:pk>/', RestaurantDetailAPIView.as_view(), name='api_restaurant_detail'),
    path('restaurants/<int:restaurant_pk>/reviews/', ReviewListCreateAPIView.as_view(), name='api_review_list'),
    path('restaurants/<int:restaurant_pk>/reviews/<int:pk>/', ReviewDetailAPIView.as_view(), name='api_review_detail'),
    path('token/', obtain_auth_token, name='api_token_auth'),
]