from django.contrib import admin
from django.contrib.auth import get_user_model
from users.models import Skill

User = get_user_model()

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    ordering = ['name']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'name', 'surname', 'is_active', 'is_staff']
    search_fields = ['email', 'name', 'surname']
    list_filter = ['is_active', 'is_staff']
    fieldsets = (
        ('Основная информация', {
            'fields': ('email', 'name', 'surname', 'avatar', 'about')
        }),
        ('Контакты', {
            'fields': ('phone', 'github_url')
        }),
        ('Навыки', {
            'fields': ('skills',)
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    )
