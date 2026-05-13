from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from PIL import Image, ImageDraw, ImageFont
import random
import io
from django.core.files.base import ContentFile
from constants import constants_user as constant


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, surname, password=None,
                         **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, surname, password, **extra_fields)


class Skill(models.Model):
    name = models.CharField(
        verbose_name='Название навыка',
        max_length=constant.MAX_LENGTH_NAME_SKILL
    )
    
    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True
    )
    name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=constant.MAX_LENGTH_NAME_USER
    )
    surname = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=constant.MAX_LENGTH_SURNAME_USER
    )
    avatar = models.ImageField(
        verbose_name='Аватарка пользователя',
        upload_to='avatars/'
    )
    phone = models.CharField(
        verbose_name='Номер телефона',
        max_length=constant.MAX_LENGTH_PHONE_USER
    )
    github_url = models.URLField(
        verbose_name='Ссылка на Github',
        blank=True
    )
    about = models.TextField(
        verbose_name='Описание профиля',
        max_length=constant.MAX_LENGTH_ABOUT_USER,
        blank=True
    )
    is_active = models.BooleanField(
        verbose_name='Активный пользователь',
        default=True
    )
    is_staff = models.BooleanField(
        verbose_name='Администратор',
        default=False
    )
    skills = models.ManyToManyField(
        Skill,
        verbose_name='Навыки пользователя',
        related_name='users',
        blank=True
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = self.generate_avatar()
        super().save(*args, **kwargs)
    
    def generate_avatar(self):        
        bg_color = random.choice(constant.AVATARS_COLORS)
        
        img = Image.new('RGB', (constant.SIZE_IMG, constant.SIZE_IMG), bg_color)
        draw = ImageDraw.Draw(img)
        
        letter = self.name[0].upper() if self.name else '?'
        font = ImageFont.load_default()
        
        bbox = draw.textbbox(constant.BBOX, letter, font=font)
        t_width = bbox[2] - bbox[0]
        t_height = bbox[3] - bbox[1]
        x = (constant.SIZE_IMG - t_width) / 2
        y = (constant.SIZE_IMG - t_height) / 2 - bbox[1]
        
        draw.text((x, y), letter, fill='white', font=font)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        filename = f'avatar_{self.email}.png'

        return ContentFile(buffer.getvalue(), filename)
