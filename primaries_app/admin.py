from django.contrib import admin
from django.utils.html import strip_tags

from .models import EvaluateModel, MarkModel, News


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
