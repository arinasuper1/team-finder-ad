from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner', 'status', 'created_at']
    search_fields = ['name', 'description', 'owner__email', 'owner__name']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'status')
        }),
        ('Автор и участники', {
            'fields': ('owner', 'participants')
        }),
        ('Дополнительно', {
            'fields': ('github_url', 'created_at')
        }),
    )
