from django.db import models
from django.conf import settings
from constants import constants_projects as constant


class Project(models.Model):
    name = models.CharField(
        verbose_name='Название проекта',
        max_length=constant.MAX_LENGTH_NAME_PROJECT
    )
    description = models.TextField(
        verbose_name='Описание проекта',
        blank=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор проекта',
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания проекта',
        auto_now_add=True
    )
    github_url = models.URLField(
        verbose_name='Ссылка на Github',
        blank=True
    )
    status = models.CharField(
        verbose_name='Статус проекта',
        max_length=6,
        choices=constant.STATUS_CHOICES,
        default='open'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='Участники проекта',
        related_name='participated_projects',
        blank=True
    )
    
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
