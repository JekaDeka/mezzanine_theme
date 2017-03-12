from django.db import models
from django.utils.translation import ugettext_lazy as _
from mezzanine.core.fields import FileField, RichTextField
from mezzanine.utils.models import upload_to
from cartridge.shop.models import Priced
from django.utils.timezone import now

def on_custom_sale(self):
    n = now()
    valid_from = self.sale_from is not None and self.sale_from < n
    valid_to = self.sale_to is not None and self.sale_to > n
    return self.sale_price is not None and valid_from and valid_to

Priced.add_to_class("on_custom_sale", on_custom_sale)


class MyProfile(models.Model):
    user = models.OneToOneField("auth.User")
    image = FileField(upload_to=upload_to("theme.MyProfile.image", "myprofile"), 
        verbose_name=_("Изображение профиля"), format="Image", max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, blank=True,
                            verbose_name=("Расположение"))
    phone = models.CharField(max_length=255, blank=True,
                             verbose_name=("Телефон"))
    bio = RichTextField(default="", verbose_name=("Расскажите о себе"))


class Slider(models.Model):
    title = models.CharField(max_length=255, blank=False,
                             verbose_name=("Название"))

    class Meta:
        verbose_name = _("Слайдер")
        verbose_name_plural = _("Слайдеры")


class SliderItem(models.Model):
    '''
    An individual Slider item, should be nested under a Slider
    '''

    featured_image = FileField(verbose_name=_("Изображение"),
                               upload_to=upload_to(
                                   "theme.SliderItem.featured_image", "slider"),
                               format="Image", max_length=255, null=True, blank=True)
    short_description = RichTextField(blank=True)
    href = models.CharField(verbose_name=_("Ссылка"), max_length=2000, blank=True,
                            help_text="Ссылка куда будет ввести данный слайд. Например /blog/")

    slider = models.ForeignKey(Slider, related_name="images")

    def __str__(self):              # __unicode__ on Python 2
        return str(self.featured_image)

    class Meta:
        verbose_name = _("Элемент слайдера")
        verbose_name_plural = _("Элементы слайдера")

