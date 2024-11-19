# posts/forms.py
from django import forms
from .models import Post, RentRequest
from django.forms.widgets import DateInput
from django.core.exceptions import ValidationError

from datetime import date

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Row,Column,Layout


from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title', 'description', 'address', 'image', 'max_people','price_per_person',
            'wifi', 'bathroom', 'bbq', 'pool', 
            'kid_friendly', 'parking', 'electricity'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'title',
            'description',
            'address',
            'image',
            'max_people',
            'price_per_person',
            Row(
                Column('wifi', css_class='form-group col-md-4 mb-0'),
                Column('bathroom', css_class='form-group col-md-4 mb-0'),
                Column('bbq', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('pool', css_class='form-group col-md-4 mb-0'),
                Column('kid_friendly', css_class='form-group col-md-4 mb-0'),
                Column('parking', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('electricity', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Save', css_class='btn btn-primary')
        )
        

class RentRequestForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Data di inizio'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Data di fine'
    )

    class Meta:
        model = RentRequest
        fields = ['start_date', 'end_date']

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        today = date.today()

        # Ensure the start date is not in the past
        if start_date and start_date < today:
            raise ValidationError("La data di inizio non può essere nel passato.")
        
        return start_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Ensure the end date is not before the start date
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', "La data di fine non può essere prima della data di inizio.")
        
        return cleaned_data