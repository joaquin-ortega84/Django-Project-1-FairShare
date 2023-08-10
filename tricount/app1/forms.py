from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class ExtendedUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

class ParticipantForm(forms.Form):
    name = forms.CharField(max_length=100)

class GroupForm(forms.Form):
    group_name = forms.CharField(max_length=20)
    description = forms.CharField(widget=forms.Textarea)
    category = forms.CharField(max_length=50)
    # Other fields...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        currency_info = self._get_top_currency_info()  # Fetch top currencies
        self.fields['currency'] = forms.ChoiceField(choices=currency_info)

    def _get_top_currency_info(self):
        # Your logic to fetch top 5 currencies
        # Return a list of tuples: [(code1, name1), (code2, name2), ...]
        # Example:
        top_currencies = [
            ('USD', 'United States Dollar'),
            ('EUR', 'Euro'),
            ('JPY', 'Japanese Yen'),
            ('GBP', 'British Pound'),
            ('AUD', 'Australian Dollar'),
        ]
        return top_currencies
