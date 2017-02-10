from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.fields import FileField, RichTextField
from mezzanine.utils.models import upload_to


class MyProfile(models.Model):
    user = models.OneToOneField("auth.User")
    image = models.ImageField(
        upload_to='users/avatars/', blank=True, verbose_name=("Изображение"))
    city = models.CharField(max_length=255, blank=True,
                            verbose_name=("Расположение"))
    phone = models.CharField(max_length=255, blank=True,
                             verbose_name=("Телефон"))
    bio = RichTextField(default="", verbose_name=("Биография"))


class Slider(models.Model):
    title = models.CharField(max_length=255, blank=True,
                             verbose_name=("Название"))

    class Meta:
        verbose_name = _("Slider")
        verbose_name_plural = _("Sliders")


class SliderItem(models.Model):
    '''
    An individual Slider item, should be nested under a Slider
    '''

    featured_image = FileField(verbose_name=_("Featured Image"),
                               upload_to=upload_to(
                                   "theme.SliderItem.featured_image", "slider"),
                               format="Image", max_length=255, null=True, blank=True)
    short_description = RichTextField(blank=True)
    href = models.CharField(max_length=2000, blank=True,
                            help_text="A link to the finished project (optional)")

    slider = models.ForeignKey(Slider, related_name="images")

    class Meta:
        verbose_name = _("Slider item")
        verbose_name_plural = _("Slider items")
