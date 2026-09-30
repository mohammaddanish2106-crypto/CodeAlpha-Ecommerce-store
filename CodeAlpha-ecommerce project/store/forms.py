from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Order, Product, Category, UserProfile


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last name'}))
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email address'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=30, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last name'}))
    email = forms.EmailField(required=False,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email address'}))

    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city']
        widgets = {
            'phone':   forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone number'}),
            'address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Street address'}),
            'city':    forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
        }


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'address', 'city', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full name'}),
            'address':   forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Delivery address'}),
            'city':      forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'phone':     forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone number'}),
        }


class ProductForm(forms.ModelForm):
    """Used by staff/admin to create or edit products."""
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock', 'image']
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Product name'}),
            'category':    forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Description'}),
            'price':       forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.00', 'step': '0.01'}),
            'stock':       forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0'}),
            'image':       forms.ClearableFileInput(attrs={'class': 'form-input-file'}),
        }


class OrderStatusForm(forms.ModelForm):
    """Used by staff/admin to update order status."""
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-input'}),
        }
