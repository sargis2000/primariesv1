from django import forms
from django.contrib import admin
from django.utils.html import strip_tags

from .models import EvaluateModel, MarkModel, News, GlobalConfigs


@admin.register(GlobalConfigs)
class VotingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MarkModel)
class VotingAdmin(admin.ModelAdmin):
    """Mark model admin"""

    @staticmethod
    def text(obj):
        return strip_tags(obj.content)[:30] + "..."

    list_display = (
        "text",
        "mark",
    )
    search_fields = ("mark",)

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(VotingAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "content":
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield


@admin.register(EvaluateModel)
class PollingAdmin(admin.ModelAdmin):
    """Evaluate model admin"""

    list_display = (
        "voter",
        "candidate",
    )
    list_filter = (
        "voter",
        "candidate",
    )
    search_fields = (
        "voter",
        "candidate",
    )


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)
