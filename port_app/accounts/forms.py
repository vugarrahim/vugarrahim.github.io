from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm  # fill in custom user info then save it
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, ReadOnlyPasswordHashField
from authtools import forms as authtoolsforms
from django.contrib.auth import forms as authforms
from django.forms.models import inlineformset_factory
from .models import *
from django.contrib.auth import (
    get_user_model, password_validation,
)

User = get_user_model()


class MyUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter Password'}),
                                help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "telephone", "passport")

    def __init__(self, *args, **kwargs):
        super(MyUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.TextInput(attrs={
            'placeholder': 'Email *'})
        self.fields['first_name'].widget = forms.TextInput(attrs={
            'placeholder': 'First name *'})
        self.fields['last_name'].widget = forms.TextInput(attrs={
            'placeholder': 'Last name *'})
        self.fields['telephone'].widget = forms.TextInput(attrs={
            'placeholder': 'Telephone'})
        self.fields['passport'].widget = forms.TextInput(attrs={
            'placeholder': 'Passport'})

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2

    def save(self, commit=True):
        user = super(MyUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class MyUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=_("Raw passwords are not stored, so there is no way to see "
                                                     "this user's password, but you can change the password "
                                                     "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MyUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserRegistrationForm(MyUserCreationForm):
    accept = forms.BooleanField(initial=False, label=_('Qaydalar'),
                                error_messages={'required': _('You must accept the rules')})


class MyAuthenticationForm(AuthenticationForm):
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def __init__(self, *args, **kwargs):
        super(MyAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={
            'placeholder': 'Email'})


class PasswordResetForm(authtoolsforms.FriendlyPasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.TextInput(attrs={
            'placeholder': 'Email'})


class SetPasswordForm(authforms.SetPasswordForm):
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput(attrs={'placeholder': 'New password'}),
                                    )
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput(attrs={'placeholder': 'New password confirmation'}))


class PasswordChangeForm(authforms.PasswordChangeForm):
    old_password = forms.CharField(label=_("Old password"),
                                   widget=forms.PasswordInput(attrs={'placeholder': 'Old password'}))

    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput(attrs={'placeholder': 'New password'}),
                                    )
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput(attrs={'placeholder': 'New password confirmation'}))


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "telephone", "passport", 'is_active')

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.TextInput(attrs={
            'placeholder': 'Email'})
        self.fields['first_name'].widget = forms.TextInput(attrs={
            'placeholder': 'First name'})
        self.fields['last_name'].widget = forms.TextInput(attrs={
            'placeholder': 'Last name'})
        self.fields['telephone'].widget = forms.TextInput(attrs={
            'placeholder': 'Telephone'})
        self.fields['passport'].widget = forms.TextInput(attrs={
            'placeholder': 'Passport'})


class SelfUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "telephone", "passport",)


class AgentForm(forms.ModelForm):
    def __init__(self, *arg, **kwarg):
        super(AgentForm, self).__init__(*arg, **kwarg)
        self.empty_permitted = False

    class Meta:
        model = Agent
        fields = ('name', 'description')

AgentFormSet = inlineformset_factory(User, Agent, form=AgentForm, can_delete=False)
