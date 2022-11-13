from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.safestring import mark_safe

from accounts.models import CandidateProfile, User, VoterProfile


class MarkModel(models.Model):
    """A model for creating texts and marks for evaluating candidates"""

    content = RichTextField()
    mark = models.SmallIntegerField(
        validators=[MinValueValidator(-2), MaxValueValidator(5)]
    )

    class Meta:
        verbose_name = "Voting Content"


class EvaluateModel(models.Model):
    """Evaluating Candidates"""

    voter = models.ForeignKey(
        VoterProfile,
        on_delete=models.CASCADE,
        related_name="voter",
        verbose_name="voter",
    )
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="candidate",
        verbose_name="candidate",
    )
    poll = models.ForeignKey(MarkModel, on_delete=models.CASCADE)

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


class News(models.Model):
    title = models.CharField(max_length=1000)
    text = RichTextField(blank=True, null=True)
    picture = models.ImageField(upload_to="media/news/", blank=True, null=True)
    media_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_picture(self):
        return mark_safe(f'<img src={self.picture.url} width="90" height="70"')

    get_picture.short_description = "picture"

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"
