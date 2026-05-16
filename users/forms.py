from django import forms
from users.models import User
from constants.validations import validation_phone, validation_github_url


class RegistrationFormUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']
        widgets = {'password': forms.PasswordInput}

    def save(self, commit=True):
        user: User = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    

class LoginFormUser(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class EditFormUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'phone', 'github_url', 'about', 'avatar']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        return validation_phone(phone, user_pk=self.instance.pk)
    
    def clean_github_url(self):
        github_url = self.cleaned_data.get('github_url')
        return validation_github_url(github_url)
    

class ChangePasswordFormUser(forms.Form):
    old_password = forms.CharField(
        label='Текущий пароль',
        widget=forms.PasswordInput
    )
    new_password = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput
    )
    new_password_confirmation = forms.CharField(
        label='Подтверждение нового пароля',
        widget=forms.PasswordInput
    )

    def clean_password(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirmation = cleaned_data.get('new_password_confirmation')

        if new_password and new_password_confirmation != new_password_confirmation:
            raise forms.ValidationError('Пароли не совпадают')
