from django import forms
from django.shortcuts import get_object_or_404
from .models import Review, RentRequest

from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
    
    def __init__(self, *args, **kwargs):
        self.rent_request_id = kwargs.pop('rent_request_id', None)
        self.renter = kwargs.pop('renter', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        
        if not self.rent_request_id:
            raise forms.ValidationError("ID di richiesta di affitto mancante.")
        
        rent_request = get_object_or_404(RentRequest, pk=self.rent_request_id)
        
        if not self.renter:
            raise forms.ValidationError("Mancano informazioni sull'affittuario.")
        
        if Review.objects.filter(rent_request=rent_request, renter=self.renter).exists():
            raise forms.ValidationError("Hai già recensito questa proprietà.")
        
        return cleaned_data

class ReviewEditForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']