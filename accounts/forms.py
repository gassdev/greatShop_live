from django import forms
from .models import Account, UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number',
                  'email', 'password', 'confirm_password']
        
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match"
            )
            
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number']
        
class UserProfileForm(forms.ModelForm):
    picture = forms.ImageField(required=False, error_messages={'Invalid':("Image files only")},
                               widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 
                  'country', 'picture']