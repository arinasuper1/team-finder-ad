import re
from django import forms
from users.models import User
from constants import constants_teamfinder as t_constant
from constants import constants_users as constant


def validation_github_url(url: str):
    if not url:
        raise forms.ValidationError('Ссылка на GitHub обязательна')
    if url and t_constant.GITHUB_URL not in url:
        raise forms.ValidationError(f'Эта ссылка не ведёт на {t_constant.GITHUB_URL}')
    


def validation_phone(phone: str, user_pk=None):
    if not phone:
        return phone
    
    if not re.match(constant.PHONE_PATTERN, phone):
        raise forms.ValidationError('Номер телефона не соответствует формату +7XXXXXXXXXX или 8XXXXXXXXXX')
    
    if phone.startswith('8'):
        phone = '+7' + phone[1:]

    phone_8 = '8' + phone[1:]
    same_phones = User.objects.filter(phone_in=[phone, phone_8])

    if user_pk:
        same_phones = same_phones.exclude(pk=user_pk)

    if same_phones.exists():
        raise forms.ValidationError('Пользователь с таким номером телефона уже существует')
    
    return phone
