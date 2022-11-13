# Generated by Django 4.1.1 on 2022-11-11 19:23

import datetime

import ckeditor.fields
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        max_length=30, unique=True, verbose_name="Օգտատեր"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(default=False, verbose_name="Անձնակազմ"),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Ակտիվ")),
                ("is_voter", models.BooleanField(default=False, verbose_name="Ընտրող")),
                (
                    "is_candidate",
                    models.BooleanField(default=False, verbose_name="Թեկածու"),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Գրանցման Ժամանակը",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="VoterProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(max_length=200, verbose_name="First name"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=200, verbose_name="Last name"),
                ),
                ("email", models.EmailField(max_length=254)),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, region=None
                    ),
                ),
                ("birthdate", models.DateField(default=datetime.date(1950, 1, 1))),
                ("address", models.CharField(max_length=50, verbose_name="Address")),
                (
                    "soc_url",
                    models.URLField(
                        help_text="Social account url",
                        max_length=300,
                        verbose_name="URL",
                    ),
                ),
                ("is_email_verified", models.BooleanField(default=False)),
                ("is_paid", models.BooleanField(default=False)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CandidateProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=100, verbose_name="Անուն")),
                (
                    "last_name",
                    models.CharField(max_length=100, verbose_name="Ազգանուն"),
                ),
                ("birthdate", models.DateField(verbose_name="Ծննդյան օր")),
                (
                    "picture",
                    models.ImageField(
                        upload_to="profile_pictures", verbose_name="Նկար"
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        choices=[("male", "male"), ("female", "female")],
                        max_length=6,
                        verbose_name="Սեռ",
                    ),
                ),
                ("email", models.EmailField(max_length=254, verbose_name="Էլ․ Հասցե")),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, region=None, verbose_name="Հեռախոսահամար"
                    ),
                ),
                (
                    "region",
                    models.CharField(
                        choices=[
                            ("Աջափնյակ", "Աջափնյակ"),
                            ("Ավան", "Ավան"),
                            ("Արաբկիր", "Արաբկիր"),
                            ("Դավթաշեն", "Դավթաշեն"),
                            ("Էրեբունի", "Էրեբունի"),
                            ("Կենտրոն", "Կենտրոն"),
                            ("Մալաթիա-Սեբաստիա", "Մալաթիա-Սեբաստիա"),
                            ("Նոր Նորք", "Նոր Նորք"),
                            ("Նուբարաշեն", "Նուբարաշեն"),
                            ("Շենգավիթ", "Շենգավիթ"),
                            ("Քանաքեռ-Զեյթուն", "Քանաքեռ-Զեյթուն"),
                        ],
                        max_length=16,
                        verbose_name="Տարածաշրջան",
                    ),
                ),
                ("address", models.CharField(max_length=50, verbose_name="Հասցե")),
                (
                    "facebook_url",
                    models.URLField(
                        help_text="Facebook account url",
                        max_length=300,
                        verbose_name="Facebook Հղում",
                    ),
                ),
                (
                    "youtube_url",
                    models.URLField(
                        help_text="Youtube account url",
                        max_length=300,
                        verbose_name="Youtube Հղում",
                    ),
                ),
                (
                    "additional_url",
                    models.URLField(
                        blank=True,
                        help_text="Additional url",
                        max_length=300,
                        null=True,
                        verbose_name="Լրացուցիչ հղում",
                    ),
                ),
                (
                    "party",
                    models.CharField(
                        default="Անկուսակցական",
                        help_text="Կուսակցություն",
                        max_length=200,
                        verbose_name="Կուսակցություն",
                    ),
                ),
                (
                    "education",
                    ckeditor.fields.RichTextField(
                        blank=True, null=True, verbose_name="Կրթություն"
                    ),
                ),
                (
                    "about",
                    ckeditor.fields.RichTextField(
                        blank=True,
                        help_text="here you can write about yourself",
                        null=True,
                        verbose_name="Իմ մասին",
                    ),
                ),
                (
                    "marital_status",
                    ckeditor.fields.RichTextField(
                        blank=True,
                        help_text="here you can  about candidate marital status",
                        null=True,
                        verbose_name="Ամուսնական կարգավիճակ",
                    ),
                ),
                (
                    "work_experience",
                    ckeditor.fields.RichTextField(
                        blank=True,
                        help_text="About work experience",
                        null=True,
                        verbose_name="Աշխատանքային Փորձ",
                    ),
                ),
                (
                    "political_experience",
                    ckeditor.fields.RichTextField(
                        blank=True,
                        help_text="Քաղաքական Փորձ",
                        null=True,
                        verbose_name="political experience",
                    ),
                ),
                (
                    "is_email_verified",
                    models.BooleanField(
                        default=False, verbose_name="Էլ․ Հասցեն հատատված է"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Candidate Profile",
                "verbose_name_plural": "Candidate Profiles",
            },
        ),
        migrations.CreateModel(
            name="CandidatePost",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                ("text", ckeditor.fields.RichTextField()),
                (
                    "media_path",
                    models.URLField(
                        help_text="Social account url",
                        max_length=300,
                        verbose_name="media_URL",
                    ),
                ),
                ("photo", models.ImageField(upload_to="media/candidate_post_images/")),
                ("important", models.BooleanField(default=False)),
                (
                    "profile",
                    models.ForeignKey(
                        help_text="choice which profile to post",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.candidateprofile",
                    ),
                ),
            ],
        ),
    ]
