from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

# Форма для создания пользователя
class CustomUserCreationForm(UserCreationForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('login', 'first_name', 'last_name', 'patronymic', 'is_student', 'is_teacher', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Хэшируем пароль
        if commit:
            user.save()
        return user


# Форма для изменения пользователя
class CustomUserChangeForm(UserChangeForm):
    password = forms.CharField(label="Новый пароль", widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('login', 'first_name', 'last_name', 'patronymic', 'is_student', 'is_teacher', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)  # Хэшируем новый пароль
        if commit:
            user.save()
        return user


