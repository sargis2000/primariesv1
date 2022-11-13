from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialToken
from django import forms
from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import TokenProxy

from .models import CandidatePost, CandidateProfile, User, VoterProfile


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. All the required
    fields are plus repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("username",)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    make_inactive.short_description = "Set inactive to selected  users"

    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    make_active.short_description = "Set active to selected  users"

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Statuses",
            {
                "fields": (
                    "is_superuser",
                    "is_staff",
                    "is_active",
                    "is_voter",
                    "is_candidate",
                )
            },
        ),
        (None, {"fields": ("date_joined",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
    search_fields = ("username",)
    list_filter = ("is_voter", "is_candidate", "is_active")
    list_display = ("username", "is_voter", "is_candidate", "is_active")
    readonly_fields = ("date_joined",)
    actions = (
        "make_inactive",
        "make_active",
        "delete_selected",
    )


@admin.register(CandidatePost)
class PostAdmin(admin.ModelAdmin):
    model = CandidatePost
    list_display = ("title", "text", "get_user")
    list_filter = ("profile",)
    search_fields = ("title",)

    @display(ordering="profile__user", description="user")
    def get_user(self, obj):
        user = obj.profile.user
        return user.username


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    @staticmethod
    def full_name(obj):
        return "{0} profile".format(obj.user.username)

    list_display = (
        "full_name",
        "email",
        "gender",
        "phone_number",
        "get_picture",
    )
    list_filter = ("gender", "party")
    search_fields = (
        "email",
        "phone_number",
        "username",
        "first_name",
        "last_name",
        "party",
    )


@admin.register(VoterProfile)
class VoterProfile(admin.ModelAdmin):
    @staticmethod
    def full_name(obj):
        return "{0} profile".format(obj.user.username)

    list_display = ("email", "phone_number", "address", "is_email_verified")
    search_fields = (
        "email",
        "phone_number",
    )
    list_filter = ("is_email_verified", "is_paid")


admin.site.unregister(Group)
admin.site.unregister(EmailAddress)
admin.site.unregister(SocialToken)
admin.site.unregister(TokenProxy)
