from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from mezzanine.core.fields import FileField, RichTextField
from mezzanine.core.models import Displayable, Ownable, RichText, Slugged
from mezzanine.utils.models import AdminThumbMixin, upload_to
from mezzanine.utils.models import upload_to
from cartridge.shop.models import Priced
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from datetime import date


def on_custom_sale(self):
    n = now()
    valid_from = self.sale_from is not None and self.sale_from < n
    valid_to = self.sale_to is not None and self.sale_to > n
    return self.sale_price is not None and valid_from and valid_to

Priced.add_to_class("on_custom_sale", on_custom_sale)


# class UserProfile(models.Model):
#     user = models.OneToOneField("auth.User")
#     firstname = models.CharField(max_length=255, blank=False,
#                                  verbose_name=("Имя"))
#     lastname = models.CharField(max_length=255, blank=False,
#                                 verbose_name=("Фамилия"))


class UserShop(models.Model):
    """docstring for UserShop"""
    user = models.OneToOneField("auth.User")
    image = models.ImageField(
        upload_to="tmp_images/", verbose_name=_("Логотип магазина"), blank=False, default="")

    background = models.ImageField(
        upload_to="tmp_images/", verbose_name=_("Обложка магазина"), blank=False, default="")

    shopname = models.CharField(max_length=255, blank=False, unique=True,
                                verbose_name=("Название магазина"))
    bio = RichTextField(default="", verbose_name=("Описание"),
                        help_text="Расскажите интересные факты о создании своего бренда, опишите его особенности и преимущества. Перечислите свои флагманские вещи, расскажите кратко про производство, материалы. Напишите как минимум три предложения о себе. Главная страница магазина будет выглядеть красивее, а мы это учитываем, когда отбираем магазины в раздел «Лучшее» и в редакционные подборки.")

    phone = models.CharField(max_length=255, blank=True,
                             verbose_name=("Телефон"))

    country = models.CharField(max_length=255, blank=False,
                               verbose_name=("Страна"), default="")
    city = models.CharField(max_length=255, blank=False,
                            verbose_name=("Город"), default="")

    express_point = models.BooleanField(
        default=False, verbose_name=("Получение в вашем пункте выдачи"))
    express_point_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
                                              help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.")
    express_city = models.BooleanField(
        default=False, verbose_name=("Курьером по г. Москва"))
    express_city_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
                                             help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.")
    express_country = models.BooleanField(default=False, verbose_name=(
        "Курьером по стране (Российская Федерация)"))
    express_country_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
                                                help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.")
    express_world = models.BooleanField(
        default=False, verbose_name=("Курьером по миру"))
    express_world_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
                                              help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.")
    express_mail = models.BooleanField(
        default=False, verbose_name=("Почта России"))
    express_mail_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
                                             help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.")
    express_personal = models.BooleanField(
        default=False, verbose_name=("Личная встреча"))
    express_personal_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
                                                 help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.")

    express_other = RichTextField(default="",
                                  verbose_name=(
                                      "Дополнительная информация о доставке"),
                                  help_text="Адреса, по которым покупатель сможет забрать товар самостоятельно. Любые другие нюансы и условия по доставке.")

    payment_personal = models.BooleanField(
        default=False, verbose_name=("Наличными при получении"))
    payment_bank_transfer = models.BooleanField(
        default=False, verbose_name=("Банковский перевод"))
    payment_card_transfer = models.BooleanField(
        default=False, verbose_name=("Банковской картой"))

    payment_other = RichTextField(default="",
                                  verbose_name=(
                                      "Дополнительная информация об оплате"),
                                  help_text="Опишите любые другие условия и важные моменты по оплате — покупателю будет проще принять решение о покупке в вашем магазине.")

    rules = RichTextField(default="",
                          verbose_name=(
                              "Дополнительная информация об оплате"),
                          help_text="Обозначьте условия возврата товаров. В течение какого времени после получения товара покупатель может обратиться? Если вы не принимаете возвраты или обмены, чётко укажите на это, чтобы избежать споров в случае желания покупателя отказаться от покупки.")

    def get_express_fields(self):
        fields = []
        for f in self._meta.fields:
            fname = f.name
            try:
                value = getattr(self, fname)
            except AttributeError:
                value = None

            if fname.startswith('express') and f.editable and value and (f.name not in ('id', 'user', 'express_other')):
                fields.append(
                    {
                        'label': f.verbose_name,
                        'name': f.name,
                        'value': value,
                    }
                )
        return fields


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


class OrderItem(models.Model):
    title = models.CharField(_("Название"), max_length=500, null=False)
    active = models.BooleanField(_("Активен"), default=True, editable=False)
    created = models.DateField(
        _("Дата добавления"), editable=False, default=date.today)
    ended = models.DateTimeField(
        _("Крайний срок"), null=True, editable=True, blank=True, help_text="оставьте пустым, если срок неограничен.")
    price = models.DecimalField(
        _("Бюджет"), max_digits=8, decimal_places=2, default=0, blank=True,
        help_text="Если Вы не представляете, сколько подобная работа могла бы стоить, оставьте поле незаполненным.")
    count = models.DecimalField(
        _("Количество"), max_digits=8, decimal_places=0, default=1)
    color_suggest = models.CharField(
        _("Пожелания к цвету"), max_length=500, blank=True, default="",
        help_text="Пример: «небесно-голубой» или «любой».")
    size_suggest = models.CharField(
        _("Пожелания к размерам"), max_length=500, blank=True, default="",
        help_text="Пример: «с футбольный мяч» или «длина - 30 см».")
    material_suggest = models.CharField(
        _("Пожелания к материалам"), max_length=500, blank=True, default="",
        help_text="Пример: шерсть")
    description = RichTextField(
        default="", verbose_name=("Подробное описание"),
        help_text="Как можно более подробно опишите желаемое изделие.")

    categories = models.ManyToManyField("OrderItemCategory",
                                        verbose_name=_("Виды работ"),
                                        blank=True, related_name="orderitems")

    featured_image = FileField(verbose_name=_("Изображение"),
                               upload_to=upload_to(
                                   "theme.OrderItem.image", "orders"),
                               format="Image", max_length=255, null=True, blank=True,
                               help_text="Загрузите фотографии эскизов или примеров, которые помогут мастерам точнее понять Ваш заказ.")
    author = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, default=None, editable=False, null=True)

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Мои заказы")
        ordering = ("-created",)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.title)

    def get_absolute_url(self):
        url_name = "order_detail"
        kwargs = {"pk": self.pk}
        return reverse(url_name, kwargs=kwargs)


class OrderItemCategory(Slugged):
    """
    A category for grouping Order items into a series.
    """

    class Meta:
        verbose_name = _("Вид работы")
        verbose_name_plural = _("Виды работ")
        ordering = ("title",)

    @models.permalink
    def get_absolute_url(self):
        return ("order_list_category", (), {"category": self.slug})
