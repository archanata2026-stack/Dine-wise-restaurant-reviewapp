from django.urls import path
from .views import RestaurantListView, RestaurantDetailView, SignUpView, AddReviewView, EditProfileView, CuisineListView, SearchView
urlpatterns = [
    path('', RestaurantListView.as_view(), name='restaurant_list'),
    path('restaurant/<int:pk>/', RestaurantDetailView.as_view(), name='restaurant_detail'),
    path('restaurant/<int:pk>/review/', AddReviewView.as_view(), name='add_review'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('cuisine/', CuisineListView.as_view(), name='cuisine_list'),
    path('search/', SearchView.as_view(), name='search'),
]