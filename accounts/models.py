import datetime
from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe
from phonenumber_field.modelfields import PhoneNumberField
from .managers import CustomUserManager

gender = (
    ("male", "male"),
    ("female", "female"),
)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, verbose_name="username", unique=True)
    is_staff = models.BooleanField(default=False, verbose_name="is stuff")
    is_active = models.BooleanField(default=True, verbose_name="is active")
    is_voter = models.BooleanField(default=False, verbose_name="is voter")
    is_candidate = models.BooleanField(default=False, verbose_name="is candidate")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="date joined")
    USERNAME_FIELD = "username"
    objects = CustomUserManager()

    def __str__(self):
        return self.get_username()


class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, default=None)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    party = models.CharField(
        max_length=200, help_text="Կուսակցություն", default="Անկուսակցական"
    )
    picture = models.ImageField(upload_to="profile_pictures")
    email = models.EmailField()
    phone_number = PhoneNumberField()
    birthdate = models.DateField()
    address = models.CharField(max_length=50, verbose_name="Address")
    soc_url = models.URLField(
        max_length=300, verbose_name="URL", help_text="Social account url"
    )
    gender = models.CharField(max_length=6, choices=gender)
    education = RichTextField(null=True, blank=True)
    about = RichTextField(
        help_text="here you can write about yourself", null=True, blank=True
    )
    marital_status = RichTextField(
        help_text="here you can  about candidate marital status",
        verbose_name="marital status",
        null=True,
        blank=True,
    )
    work_experience = RichTextField(
        help_text="About work experience",
        verbose_name="work experience",
        null=True,
        blank=True,
    )
    political_experience = RichTextField(
        help_text="About political experience",
        verbose_name="political experience",
        null=True,
        blank=True,
    )

    is_email_verified = models.BooleanField(default=False)
    is_cleaned = False

    def get_picture(self):
        return mark_safe(f'<img src={self.picture.url} width="90" height="70"')

    get_picture.short_description = "picture"

    class Meta:
        verbose_name = "Candidate Profile"
        verbose_name_plural = "Candidate Profiles"


class VoterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    phone_number = PhoneNumberField()
    birthdate = models.DateField(default=datetime.date(1950, 1, 1))
    address = models.CharField(max_length=50, verbose_name="Address")
    soc_url = models.URLField(
        max_length=300, verbose_name="URL", help_text="Social account url"
    )
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class CandidatePost(models.Model):
    profile = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        help_text="choice which profile to post",
        null=True,
    )
    title = models.CharField(max_length=100)
    text = RichTextField()
    media_path = models.URLField(
        max_length=300, verbose_name="media_URL", help_text="Social account url"
    )
    photo = models.ImageField(upload_to="media/candidate_post_images/")
    important = models.BooleanField(default=False)

    def __str__(self):
        return "post: {0}:   author:{1}".format(self.title, self.profile.user.username)
