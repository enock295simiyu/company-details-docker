from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget


class SingUpForm(UserCreationForm):
    phone_number = PhoneNumberField(widget=PhoneNumberPrefixWidget)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SingUpForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.required = True
            visible.field.widget.attrs['class'] = 'form-control'


class PasswordResetForm(forms.Form):
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            if visible.field != 'start' or visible.field != 'end':
                visible.field.required = True

                visible.field.widget.attrs['class'] = 'form-control'


class SignUpFormClient(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, )
    last_name = forms.CharField(max_length=30, required=True, )
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    phone_number = PhoneNumberField(widget=PhoneNumberPrefixWidget)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super(SignUpFormClient, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone Number'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Re-type password'
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class UpdateUserInformationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, )
    last_name = forms.CharField(max_length=30, required=True, )
    phone_number = PhoneNumberField(widget=PhoneNumberPrefixWidget)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number',)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        super(UpdateUserInformationForm, self).__init__(*args, **kwargs)
        try:
            self.fields['phone_number'].initial = self.instance.profile.phone_number
        except:
            pass
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone Number'
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
