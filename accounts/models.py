import datetime

from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.html import mark_safe
from phonenumber_field.modelfields import PhoneNumberField

from .managers import CustomUserManager


gender = (
    ("male", "Իգական"),
    ("female", "Արական"),
)

region = (
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
)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, verbose_name="Օգտանուն", unique=True)
    is_staff = models.BooleanField(default=False, verbose_name="Անձնակազմ")
    is_active = models.BooleanField(default=True, verbose_name="Ակտիվ")
    is_voter = models.BooleanField(default=False, verbose_name="Ընտրող")
    is_candidate = models.BooleanField(default=False, verbose_name="Թեկածու")
    date_joined = models.DateTimeField(
        default=timezone.now, verbose_name="Գրանցման Ժամանակը"
    )
    USERNAME_FIELD = "username"
    objects = CustomUserManager()

    def __str__(self):
        return self.get_username()

    class Meta:
        verbose_name = "Օգտատերեր"
        verbose_name_plural = "Օգտատերեր"


class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, default=None)
    first_name = models.CharField(max_length=100, verbose_name="Անուն")
    last_name = models.CharField(max_length=100, verbose_name="Ազգանուն")
    birthdate = models.DateField(verbose_name="Ծննդյան օր")
    picture = models.ImageField(upload_to="profile_pictures", verbose_name="Նկար")
    gender = models.CharField(max_length=6, choices=gender, verbose_name="Սեռ")
    email = models.EmailField(verbose_name="Էլ․ Հասցե")
    phone_number = PhoneNumberField(verbose_name="Հեռախոսահամար")
    region = models.CharField(max_length=16, choices=region, verbose_name="Տարածաշրջան")
    address = models.CharField(max_length=100, verbose_name="Հասցե")
    facebook_url = models.URLField(
        max_length=300, verbose_name="Facebook Հղում", help_text="Facebook account url"
    )
    youtube_url = models.URLField(
        max_length=300,
        verbose_name="YouTube Հղում",
        help_text="Youtube account url",
        null=True,
        blank=True,
    )
    additional_url = models.URLField(
        max_length=300,
        verbose_name="Լրացուցիչ հղում",
        help_text="Additional url",
        null=True,
        blank=True,
    )
    party = models.CharField(
        max_length=200,
        help_text="Կուսակցություն",
        default="Անկուսակցական",
        verbose_name="Կուսակցություն",
    )
    education = RichTextField(null=True, blank=True, verbose_name="Կրթություն")
    about = RichTextField(
        help_text="here you can write about yourself",
        null=True,
        blank=True,
        verbose_name="Իմ մասին",
    )
    marital_status = RichTextField(
        help_text="here you can  about candidate marital status",
        verbose_name="Ամուսնական կարգավիճակ",
        null=True,
        blank=True,
    )
    work_experience = RichTextField(
        help_text="About work experience",
        verbose_name="Աշխատանքային Փորձ",
        null=True,
        blank=True,
    )
    political_experience = RichTextField(
        help_text="Քաղաքական Փորձ",
        verbose_name="political experience",
        null=True,
        blank=True,
    )

    is_email_verified = models.BooleanField(
        default=False, verbose_name="Էլ․ Հասցեն հատատված է"
    )
    is_cleaned = False

    def get_picture(self):
        return mark_safe(f'<img src={self.picture.url} width="90" height="70"')

    get_picture.short_description = "picture"

    class Meta:
        verbose_name = "Թեկնածուների էջեր"
        verbose_name_plural = "Թեկնածուների էջեր"


class VoterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Օգտատեր")
    first_name = models.CharField(max_length=200, verbose_name="Անուն")
    last_name = models.CharField(max_length=200, verbose_name="Ազգանուն")
    email = models.EmailField(verbose_name="Էլ․ Հասցե")
    phone_number = PhoneNumberField(verbose_name="Հեռախոսահամար")
    birthdate = models.DateField(
        default=datetime.date(1950, 1, 1), verbose_name="Ծննդյան օր"
    )
    address = models.CharField(max_length=100, verbose_name="Հասցե")
    soc_url = models.URLField(max_length=300, verbose_name="Սոցիալական կայքի հղում")
    is_email_verified = models.BooleanField(
        default=False, verbose_name="Էլ․ Հասցեն հատատված է"
    )
    is_paid = models.BooleanField(default=False, verbose_name="ՎՃարել է")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Ընտրողների էջեր"
        verbose_name_plural = "Ընտրողների էջեր"


@receiver(post_save, sender=VoterProfile)
def pre_save_user(sender, instance, created, **kwargs):
    user = instance.user
    if instance.is_email_verified is True and instance.is_paid is True:
        user.is_voter = True
    else:
        user.is_voter = False
    user.save()


class CandidatePost(models.Model):
    profile = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        help_text="choice which profile to post",
        verbose_name="Թոկնածու",
    )
    title = models.CharField(max_length=100, verbose_name="Վերնագիր")
    text = RichTextField("Տեքստ")
    media_path = models.URLField(max_length=300, verbose_name="Տեսահոլովակի հղում")
    photo = models.ImageField(
        upload_to="media/candidate_post_images/", verbose_name="Նկար"
    )
    important = models.BooleanField(default=False, verbose_name="Կարևոր")

    class Meta:
        verbose_name = "Թեկնածուների Փոստեր"
        verbose_name_plural = "Թեկնածուների Փոստեր"

    def __str__(self):
        return "post: {0}:   author:{1}".format(self.title, self.profile.user.username)
