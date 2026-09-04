from django import forms
from .models import Review,Profile

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['quality_rating', 'quantity_rating', 'staff_rating', 'comment']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['picture']