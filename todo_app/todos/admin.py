from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from . import models


class TaskResource(resources.ModelResource):
    class Meta:
        model = models.Task


class CategoryResource(resources.ModelResource):
    class Meta:
        model = models.Category


@admin.register(models.Task)
class TaskAdmin(ImportExportModelAdmin):
    resource_class = TaskResource


@admin.register(models.Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
