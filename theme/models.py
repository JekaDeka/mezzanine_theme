from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models import Count, Q
from django.db.models.signals import m2m_changed, post_save
from django.contrib.auth.models import User, Group
from mezzanine.core.fields import FileField, RichTextField
from mezzanine.core.models import Displayable, Ownable, RichText, Slugged, SitePermission
from mezzanine.utils.models import AdminThumbMixin, upload_to
from mezzanine.utils.models import upload_to
from cartridge.shop.models import Priced, Product
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from slugify import slugify, Slugify, UniqueSlugify
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


@receiver(post_save, sender=User)
def ensure_profile_exists(sender, **kwargs):
    if kwargs.get('created', False):
        user = kwargs.get('instance')
        user.is_staff = True
        group = Group.objects.get(name='blog_only')
        siteperms = SitePermission.objects.create(user=user)
        siteperms.sites.add(settings.SITE_ID)
        user.groups.add(group)
        user.save()  # save staff status and permissions
# def user_postsave_handler(sender, instance, **kwargs):
#     if not instance.is_staff:
#         try:
#             group = Group.objects.get(name='custom')
#             siteperms = SitePermission.objects.create(user=instance)
#             siteperms.sites.add(settings.SITE_ID)
#             instance.groups.add(group)
#         except:
#             pass
#         else:
#             instance.save()


class UserProfile(models.Model):
    """docstring for UserPro"""
    user = models.OneToOneField("auth.User")
    image = models.ImageField(
        upload_to="profile_images/", verbose_name=_("Ваше изображение"), blank=False, default="")

    phone = models.CharField(max_length=255, blank=True,
                             verbose_name=("Телефон"))
    country = models.CharField(max_length=255, blank=False,
                               verbose_name=("Страна"), default="")
    city = models.CharField(max_length=255, blank=False,
                            verbose_name=("Город"), default="")

    bio = RichTextField(default="", verbose_name=("Описание"),
                        help_text="Расскажите о себе.")


class UserShop(models.Model):
    """docstring for UserShop"""
    user = models.OneToOneField("auth.User")
    image = models.ImageField(
        upload_to="tmp_images/", verbose_name=_("Логотип магазина"), blank=False, default="")

    background = models.ImageField(
        upload_to="tmp_images/", verbose_name=_("Обложка магазина"), blank=False, default="")

    shopname = models.CharField(max_length=255, blank=False, unique=True,
                                verbose_name=("Название магазина"))
    slug = models.URLField(editable=False, default='')
    bio = RichTextField(default="", verbose_name=("Описание"),
                        help_text="Расскажите миру о Вашем творчестве, опишите свой продукт. Ваш бренд и то, что вы создаете своим трудом, являются единственными в своем роде - скажите, почему! Расскажите о себе, чем вы были воодушевлены, когда начали заниматься своим делом, что повлияло на ваш выбор, как развивается ваше творчество сейчас. Какие техники, материалы вы используете для своих изделий, каких принципов придерживаетесь при создании своего бренда. Ваш рассказ должен быть интересным, лаконичным, информативным и убедительным. Можете упомянуть любимую цитату или вдохновляющую идею. Не стоит злоупотреблять смайликами и прочими символами.")

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

    def save(self, request=False, *args, **kwargs):
        self.slug = slugify(self.shopname, to_lower=True)
        super(UserShop, self).save(*args, **kwargs)

    def get_products_count(self):
        return Product.objects.filter(user=self.user).count()

    def get_last_product(self):
        return Product.objects.filter(user=self.user).last()

    def get_active_orders(self):
        return 0


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
    short_description = RichTextField(verbose_name=_("Описание"), blank=True)
    href = models.CharField(verbose_name=_("Ссылка"), max_length=2000, blank=True,
                            help_text="Ссылка куда будет ввести данный слайд. Например /blog/")

    slider = models.ForeignKey(Slider, related_name="images")

    def __str__(self):              # __unicode__ on Python 2
        return str(self.featured_image)

    class Meta:
        verbose_name = _("Элемент слайдера")
        verbose_name_plural = _("Элементы слайдера")


class OrderItem(models.Model):

    class Meta:
        verbose_name = _("Заказы")
        verbose_name_plural = _("Мои заявки")
        ordering = ("-created",)

    title = models.CharField(_("Название"), max_length=500, null=False)
    active = models.BooleanField(_("Открыт"), default=True, editable=False)
    created = models.DateField(
        _("Дата добавления"), editable=False, default=date.today)
    ended = models.DateField(
        _("Крайний срок"), null=True, editable=True, blank=True, help_text="Оставьте пустым, если срок неограничен.")
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

    categories = models.ForeignKey("OrderItemCategory",
                                   verbose_name=_("Виды работ"),
                                   blank=False, null=False, related_name="orderitems")

    featured_image = FileField(verbose_name=_("Изображение"),
                               upload_to=upload_to(
                                   "theme.OrderItem.image", "orders"),
                               format="Image", max_length=255, null=True, blank=True,
                               help_text="Загрузите фотографии эскизов или примеров, которые помогут мастерам точнее понять Ваш заказ.")
    author = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, default=None, editable=False, null=True, related_name="author")

    performer = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, editable=False, null=True)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.title)

    def get_absolute_url(self):
        url_name = "order_detail"
        kwargs = {"pk": self.pk}
        return reverse(url_name, kwargs=kwargs)

    @property
    def lifespan(self):
        return '%s - present' % self.ended.strftime('%m/%d/%Y')


class OrderItemRequest(models.Model):
    """Each order item can have many users that requested to complete this order.
    Such that each author can choose specific user to compelte his order."""
    class Meta:
        verbose_name = _("Отклики")
        verbose_name_plural = _("Отклики на заявки")
        ordering = ("order",)
        unique_together = ('order', 'performer',)

    order = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name="order", verbose_name=("Заказы"))
    performer = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, verbose_name=("Исполнители"))


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
