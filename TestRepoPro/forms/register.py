from django import forms
from TestRepoPro.models import User


class RegistrationForm( forms.ModelForm ):
    """
    Form for registering a new account.
    """
    first_name = forms.CharField(widget=forms.widgets.TextInput,label="First Name:")
    last_name = forms.CharField(widget=forms.widgets.TextInput,label="Last Name:")
    email = forms.EmailField(widget=forms.widgets.TextInput,label="Email:")
    password1 = forms.CharField(widget=forms.widgets.PasswordInput,
                                label="Password:")
    password2 = forms.CharField(widget=forms.widgets.PasswordInput,
                                label="Password (again):")
    role = forms.CharField(widget=forms.widgets.TextInput,label="Role:")
    
    class Meta:
        model = User
        fields = [ 'first_name','last_name','email', 'password1', 'password2', 'role'  ]
        
    def clean( self ):
        self.cleaned_data = super( RegistrationForm, self ).clean()
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError( "Passwords did not match. Please enter both fields again" )
        return self.cleaned_data
    
    def save( self, commit = True ):
        user = super( RegistrationForm, self ).save( commit = False )
        user.set_password( self.cleaned_data['password1'] )
        if commit:
            user.save()
        return user