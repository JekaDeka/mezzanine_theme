from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
# from django.utils.text import Truncator

from django.contrib.auth.models import User, Group
from mezzanine.core.fields import FileField, RichTextField
from mezzanine.generic.fields import KeywordsField, RatingField


from mezzanine.utils.models import AdminThumbMixin, upload_to
from mezzanine.utils.models import upload_to


from django.utils.timezone import now

from smart_selects.db_fields import ChainedForeignKey, GroupedForeignKey


class Country(models.Model):

    class Meta:
        ordering = ("name",)

    name = models.CharField(max_length=255, verbose_name=("Страна"))

    def __str__(self):              # __unicode__ on Python 2
        return str(self.name)


class Region(models.Model):

    class Meta:
        ordering = ("name",)

    name = models.CharField(
        max_length=255, verbose_name=("Регион"))
    country = models.ForeignKey(Country)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.name)


class City(models.Model):

    class Meta:
        ordering = ("name",)

    name = models.CharField(
        max_length=255, verbose_name=("Регион"))
    country = models.ForeignKey(Country)
    region = models.ForeignKey(Region)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.name)


USER_PROFILE_STATUS_CHOICES = (
    (0, "Покупатель"),
    (1, "Мастер"),
)

class UserProfile(models.Model):
    """docstring for UserPro"""
    user = models.OneToOneField("auth.User", related_name="profile")
    first_name = models.CharField(max_length=255, blank=False,
                                  verbose_name=("Имя"))
    last_name = models.CharField(max_length=255, blank=True, null=True,
                                 verbose_name=("Фамилия"))
    image = FileField(upload_to=upload_to("profiles.UserProfile.image", "profiles"),
                      verbose_name=_("Ваше изображение"), format="Image", max_length=255, blank=False, default="", help_text="Загрузите Ваше изображение.")
    background = FileField(upload_to=upload_to("profiles.UserProfile.background", "profiles"),
                           verbose_name=_("Обложка профиля"), format="Image", max_length=255, blank=False, default="",
                           help_text="Загрузите обложку профиля.")

    phone = models.CharField(max_length=255, blank=True,
                             verbose_name=("Телефон"))

    allow_blogpost_count = models.PositiveIntegerField(_("Разрешенное количество записей в Блоге"), default=10)
    allow_product_count = models.PositiveIntegerField(_("Разрешенное количество товаров в магазине"), default=10)
    allow_ordertable_count = models.PositiveIntegerField(_("Разрешенное количество заявок для Стола заказов"), default=10)
    status = models.IntegerField(
        _("Тип профиля"),
        choices=USER_PROFILE_STATUS_CHOICES,
        blank=False,
        default=USER_PROFILE_STATUS_CHOICES[0][0], help_text="Будучи мастером вы сможете получать персональные заказ")


    country = models.ForeignKey(Country, verbose_name=("Страна"))

    # likes = GenericRelation(Like)
    rating = RatingField()

    region = ChainedForeignKey(
        Region,
        chained_field="country",
        chained_model_field="country",
        show_all=False,
        auto_choose=True,
        sort=True, verbose_name=("Регион"))
    city = ChainedForeignKey(
        City,
        chained_field="region",
        chained_model_field="region",
        show_all=False,
        auto_choose=True,
        sort=True, verbose_name=("Город"))

    bio = RichTextField(default="", verbose_name=("О себе"), blank=True)

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_location(self):
        location = '%s, %s' % (self.country, self.city)
        return location.strip()

    def get_absolute_url(self):
        url_name = "profile-detail"
        kwargs = {"slug": self.user.username}
        return reverse(url_name, kwargs=kwargs)

    # def get_truncated_bio(self):
    #     return Truncator(self.bio).words(20, truncate='<a href="#">Подробнее</a>', html=True)