from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator


class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("model category title"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Priority(models.TextChoices):
    LOW = "LOW", _("priority low")
    MIDDLE = "MIDDLE", _("priority middle")
    HIGH = "HIGH", _("priority high")


class Status(models.TextChoices):
    NOT_COMPLETED = "NOT_COMPLETED", _("status not completed")
    PROGRESS = "PROGRESS", _("status progress")
    COMPLETED = "COMPLETED", _("status completed")


class Task(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("model task title"))
    progress = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("model task progress"),
        default=0,
    )
    status = models.CharField(
        max_length=50,
        choices=Status,
        default=Status.NOT_COMPLETED,
        verbose_name=_("model task status"),
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority,
        default=Priority.LOW,
        verbose_name=_("model task priority"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("model task category"),
    )
    description = models.TextField(blank=True, verbose_name=_("model task description"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(
        null=False, blank=False, verbose_name=_("model task start_date")
    )
    due_date = models.DateTimeField(
        null=False, blank=False, verbose_name=_("model task due_date")
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
