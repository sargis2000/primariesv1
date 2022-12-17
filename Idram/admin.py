from django.contrib import admin
from .models import PayForEvaluate

# Register your models here.


@admin.register(PayForEvaluate)
class PayAdmin(admin.ModelAdmin):
    readonly_fields = (
        "EDP_BILL_NO",
        "EDP_AMOUNT",
        "EDP_REC_ACCOUNT",
        "for_what",
        "confirmed",
        "profile",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
