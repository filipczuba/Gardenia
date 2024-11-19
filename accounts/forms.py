from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class UserProfileRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    name = forms.CharField(required=True, label="Nome")
    surname = forms.CharField(required=True, label="Cognome")
    address = forms.CharField(required=False, label="Indirizzo")
    description = forms.CharField(widget=forms.Textarea, required=False, label="Descrizione")
    phone_number = forms.CharField(required=False, label="Numero di telefono")
    user_type = forms.ChoiceField(choices=[('landlord', 'Landlord'), ('renter', 'Renter')], label="Tipo di utente")

    class Meta:
        model = CustomUser  # Use CustomUser model instead of User
        fields = ['email', 'password1', 'password2', 'name', 'surname', 'user_type', 'address', 'description', 'phone_number']

    def save(self, commit=True):
        # Save the CustomUser instance
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()  # Save user to database
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser  # Use CustomUser instead of UserProfile
        fields = ['name', 'surname', 'address', 'description', 'phone_number', 'profile_picture']
        labels = {
            'name': 'Nome',
            'surname': 'Cognome',
            'address': 'Indirizzo',
            'description': 'Descrizione',
            'phone_number': 'Numero di telefono',
            'profile_picture': 'Immagine del profilo',
        }