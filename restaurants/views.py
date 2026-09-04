from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Restaurant
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import ReviewForm,ProfileForm
from django.core.paginator import Paginator

# Create your views here.

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

        paginator = Paginator(restaurants, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'restaurants': restaurants,
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