from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.safestring import mark_safe

from accounts.models import CandidateProfile, User, VoterProfile


class MarkModel(models.Model):
    """A model for creating texts and marks for evaluating candidates"""

    content = RichTextField(verbose_name="Տեքստ")
    mark = models.SmallIntegerField(
        validators=[MinValueValidator(-2), MaxValueValidator(5)],
        verbose_name="Գնահատական",
    )

    class Meta:
        verbose_name = "Վստահություն հայտնելու Ընտրանք"
        verbose_name_plural = "Վստահություն հայտնելու Ընտրանքներ"


class EvaluateModel(models.Model):
    """Evaluating Candidates"""

    voter = models.ForeignKey(
        VoterProfile,
        on_delete=models.CASCADE,
        related_name="voter",
        verbose_name="Ընտրող",
    )
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="candidate",
        verbose_name="Թեկնածու",
    )
    poll = models.ForeignKey(
        MarkModel, on_delete=models.CASCADE, verbose_name="Ինչպես է գնահատել՞"
    )

    def clean(self):
        """
            Check if requested user candidate
        :return: if requested user not  candidate  raise error
        """
        if self.candidate.user not in User.objects.filter(is_candidate=True):
            raise ValidationError("Can vote only for candidates")

    def save(self, *args, **kwargs):
        self.full_clean()
        super(EvaluateModel, self).save(*args, **kwargs)

    class Meta:
        unique_together = (
            "voter",
            "candidate",
        )
        verbose_name = "Վստահություն Քվեարկում"
        verbose_name_plural = "Վստահություն Քվեարկում"


class News(models.Model):
    title = models.CharField(max_length=1000, verbose_name="Վերնագիր")
    text = RichTextField(blank=True, null=True, verbose_name="Տեքստ")
    picture = models.ImageField(
        upload_to="media/news/", blank=True, null=True, verbose_name="Նկար"
    )
    media_url = models.URLField(blank=True, null=True, verbose_name="Մեդյա հղում")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ստեղծվել է")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Փոփոխվել է")

    def get_picture(self):
        return mark_safe(f'<img src={self.picture.url} width="90" height="70"')

    get_picture.short_description = "picture"

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Նորություններ"
        verbose_name_plural = "Նորություններ"
