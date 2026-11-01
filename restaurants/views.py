from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Restaurant
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import ReviewForm,ProfileForm
from django.core.paginator import Paginator
from django.db.models import Avg, F, FloatField, ExpressionWrapper
# Create your views here.

import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))



class RestaurantListView(View):
    def get(selfself,request):
        restaurants = Restaurant.objects.all()
        city = request.GET.get('city')
        cuisine = request.GET.get('cuisine')
        food_type = request.GET.get('food_type')
        if city:
            restaurants = restaurants.filter(city__icontains=city)
        if cuisine:
            restaurants = restaurants.filter(cuisine__icontains=cuisine)
        if food_type:
            restaurants = restaurants.filter(food_type=food_type)

        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        radius = request.GET.get('radius')

        if lat and lng:
            try:
                ulat, ulng = float(lat), float(lng)
                max_km = float(radius) if radius else None
            except ValueError:
                ulat = ulng = max_km = None
            if ulat is not None:
                nearby = []
                located = restaurants.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
                for r in located:
                    d = haversine(ulat, ulng, r.latitude, r.longitude)
                    if max_km is None or d <= max_km:
                        r.distance = round(d, 1)
                        nearby.append(r)
                nearby.sort(key=lambda r: r.distance)
                restaurants = nearby
        elif request.GET.get('sort') == 'rating':
            restaurants = restaurants.annotate(
                avg_rating=ExpressionWrapper(
                    (Avg('reviews__quality_rating') +
                     Avg('reviews__quantity_rating') +
                     Avg('reviews__staff_rating')) / 3,
                    output_field=FloatField()
                )
            ).order_by(F('avg_rating').desc(nulls_last=True))

        paginator = Paginator(restaurants, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'restaurants': page_obj,
            'page_obj' : page_obj,
            'cities': Restaurant.objects.values_list('city', flat=True).distinct(),
            'cuisines': Restaurant.objects.values_list('cuisine', flat=True).distinct(),
            'food_type_choices': Restaurant.FOOD_TYPE_CHOICES,
            'selected_city': city or '',
            'selected_cuisine': cuisine or '',
            'selected_food_type': food_type or '',
        }
        return render(request,'restaurant_list.html', context)


class RestaurantDetailView(View):
    def get(self,request,pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        reviews = restaurant.reviews.all()
        return render(request, 'restaurant_detail.html', {'restaurant':restaurant,'reviews':reviews})

class SignUpView(View):
    def get(self,request):
        form = UserCreationForm()
        return render(request, 'signup.html', {'form':form})

    def post(self,request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('restaurant_list')
        return render(request, 'signup.html', {'form':form})

@method_decorator(login_required, name='dispatch')
class AddReviewView(View):
    def get(self,request,pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        form = ReviewForm()
        return render(request, 'add_review.html', {'restaurant':restaurant,'form':form})

    def post(self,request,pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.restaurant = restaurant
            review.user = request.user
            review.save()
            return redirect('restaurant_detail',pk=restaurant.pk)
        return render(request, 'add_review.html', {'restaurant':restaurant,'form':form})

@method_decorator(login_required, name='dispatch')
class EditProfileView(View):
    def get(self, request):
        form = ProfileForm(instance=request.user.profile)
        return render(request, 'edit_profile.html', {'form': form})

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('restaurant_list')
        return render(request, 'edit_profile.html', {'form': form})

class CuisineListView(View):
    def get(self, request):
        cuisines = (Restaurant.objects.values_list('cuisine', flat=True)
                    .distinct().order_by('cuisine'))
        return render(request, 'cuisine_list.html', {'cuisines': cuisines})