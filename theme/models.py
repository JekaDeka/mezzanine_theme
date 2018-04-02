from django.db import models
from django.conf import settings
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models import Count, Q
from django.db.models.signals import m2m_changed, post_save
from django.contrib.auth.models import User, Group
from mezzanine.core.managers import SearchableManager
from mezzanine.core.fields import FileField, RichTextField
from mezzanine.generic.fields import KeywordsField, CommentsField, RatingField
from mezzanine.core.models import Displayable, Ownable, RichText, Slugged, SitePermission
from mezzanine.pages.models import Page
from mezzanine.blog.models import BlogPost
from mezzanine.utils.models import AdminThumbMixin, upload_to
from mezzanine.utils.models import upload_to
from cartridge.shop.models import Priced, Product, CartItem, Category
from cartridge.shop import managers
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
# from slugify import slugify, Slugify, UniqueSlugify
# from theme.utils import slugify_unicode
from smart_selects.db_fields import ChainedForeignKey, GroupedForeignKey


from datetime import date


def on_custom_sale(self):
    n = now()
    valid_from = self.sale_from is not None and self.sale_from < n
    valid_to = self.sale_to is not None and self.sale_to > n
    return self.sale_price is not None and valid_from and valid_to

Priced.add_to_class("on_custom_sale", on_custom_sale)


@receiver(post_save, sender=User)
def ensure_profile_exists(sender, **kwargs):
    if kwargs.get('created', False):
        user = kwargs.get('instance')
        user.is_staff = True
        # group = Group.objects.get(name='blog_only')
        siteperms = SitePermission.objects.create(user=user)
        siteperms.sites.add(settings.SITE_ID)
        # user.groups.add(group)
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


# class Country(models.Model):

#     class Meta:
#         ordering = ("name",)

#     name = models.CharField(max_length=255, verbose_name=("Страна"))

#     def __str__(self):              # __unicode__ on Python 2
#         return str(self.name)


# class Region(models.Model):

#     class Meta:
#         ordering = ("name",)

#     name = models.CharField(
#         max_length=255, verbose_name=("Регион"))
#     country = models.ForeignKey(Country)

#     def __str__(self):              # __unicode__ on Python 2
#         return str(self.name)


# class City(models.Model):

#     class Meta:
#         ordering = ("name",)

#     name = models.CharField(
#         max_length=255, verbose_name=("Регион"))
#     country = models.ForeignKey(Country)
#     region = models.ForeignKey(Region)

#     def __str__(self):              # __unicode__ on Python 2
#         return str(self.name)


# class UserProfile(models.Model):
#     """docstring for UserPro"""
#     user = models.OneToOneField("auth.User", related_name="profile")
#     first_name = models.CharField(max_length=255, blank=False,
#                                   verbose_name=("Имя"))
#     last_name = models.CharField(max_length=255, blank=True, null=True,
#                                  verbose_name=("Фамилия"))
#     image = models.ImageField(
#         upload_to="tmp_images/", verbose_name=_("Ваше изображение"), blank=False, default="")

#     phone = models.CharField(max_length=255, blank=True,
#                              verbose_name=("Телефон"))

#     allow_blogpost_count = models.PositiveIntegerField(_("Разрешенное количество записей в Блоге"), default=10)
#     allow_product_count = models.PositiveIntegerField(_("Разрешенное количество товаров в магазине"), default=10)
#     country = models.ForeignKey(Country, verbose_name=("Страна"))
#     region = ChainedForeignKey(
#         Region,
#         chained_field="country",
#         chained_model_field="country",
#         show_all=False,
#         auto_choose=True,
#         sort=True, verbose_name=("Регион"))
#     city = ChainedForeignKey(
#         City,
#         chained_field="region",
#         chained_model_field="region",
#         show_all=False,
#         auto_choose=True,
#         sort=True, verbose_name=("Город"))

#     bio = RichTextField(default="", verbose_name=("О себе"), blank=True)

#     def get_full_name(self):
#         full_name = '%s %s' % (self.first_name, self.last_name)
#         return full_name.strip()

#     def get_location(self):
#         location = '%s, %s' % (self.country, self.city)
#         return location.strip()

#     def get_absolute_url(self):
#         url_name = "profile"
#         kwargs = {"username": self.user.username}
#         return reverse(url_name, kwargs=kwargs)


# class UserShop(models.Model):
#     """docstring for UserShop"""
#     class Meta:
#         verbose_name = "Магазин"
#         verbose_name_plural = _("Все магазины")

#     user = models.OneToOneField("auth.User", related_name="shop", verbose_name="Владелец")
#     image = models.ImageField(
#         upload_to="tmp_images/", verbose_name=_("Логотип магазина"), blank=False, default="")

#     background = models.ImageField(
#         upload_to="tmp_images/", verbose_name=_("Обложка магазина"), blank=False, default="")

#     shopname = models.CharField(max_length=255, blank=False, unique=True,
#                                 verbose_name=("Название магазина"))
#     slug = models.URLField(editable=False, default='')
#     bio = RichTextField(default="", verbose_name=("Описание"), blank=True,
#                         help_text="Расскажите миру о Вашем творчестве, опишите свой продукт. \
#                         Ваш бренд и то, что вы создаете своим трудом, являются единственными в своем роде - скажите, почему! \
#                         Расскажите о себе, чем вы были воодушевлены, когда начали заниматься своим делом, что повлияло на ваш выбор, как развивается ваше творчество сейчас. \
#                         Какие техники, материалы вы используете для своих изделий, каких принципов придерживаетесь при создании своего бренда. \
#                         Ваш рассказ должен быть интересным, лаконичным, информативным и убедительным. Можете упомянуть любимую цитату или вдохновляющую идею. \
#                         Не стоит злоупотреблять смайликами и прочими символами.")

#     # objects = SearchableManager()
#     # search_fields = ("shopname", "bio")
#     # phone = models.CharField(max_length=255, blank=True,
#     #                          verbose_name=("Телефон"))

#     # country = models.ForeignKey(Country, verbose_name=("Страна"))
#     # region = ChainedForeignKey(
#     #     Region,
#     #     chained_field="country",
#     #     chained_model_field="country",
#     #     show_all=False,
#     #     auto_choose=True,
#     #     sort=True, verbose_name=("Регион"))
#     # city = ChainedForeignKey(
#     #     City,
#     #     chained_field="region",
#     #     chained_model_field="region",
#     #     show_all=False,
#     #     auto_choose=True,
#     #     sort=True, verbose_name=("Город"))

#     express_point = models.BooleanField(
#         default=False, verbose_name=("Получение в вашем пункте выдачи"))
#     express_point_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
#                                               help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.",
#                                               validators=[MinValueValidator(0)])
#     express_city = models.BooleanField(
#         default=False, verbose_name=("Курьером по г. Москва"))
#     express_city_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
#                                              help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.",
#                                              validators=[MinValueValidator(0)])
#     express_country = models.BooleanField(default=False, verbose_name=(
#         "Курьером по стране (Российская Федерация)"))
#     express_country_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
#                                                 help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.",
#                                                 validators=[MinValueValidator(0)])
#     express_world = models.BooleanField(
#         default=False, verbose_name=("Курьером по миру"))
#     express_world_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
#                                               help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.",
#                                               validators=[MinValueValidator(0)])
#     express_mail = models.BooleanField(
#         default=False, verbose_name=("Почта России"))
#     express_mail_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
#                                              help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.",
#                                              validators=[MinValueValidator(0)])
#     express_personal = models.BooleanField(
#         default=False, verbose_name=("Личная встреча"))
#     express_personal_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
#                                                  help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.",
#                                                  validators=[MinValueValidator(0)])

#     express_other = RichTextField(default="", blank=True,
#                                   verbose_name=(
#                                       "Дополнительная информация о доставке"),
# help_text="Адреса, по которым покупатель сможет забрать товар
# самостоятельно. Любые другие нюансы и условия по доставке.")

#     payment_personal = models.BooleanField(
#         default=False, verbose_name=("Наличными при получении"))
#     payment_bank_transfer = models.BooleanField(
#         default=False, verbose_name=("Банковский перевод"))
#     payment_card_transfer = models.BooleanField(
#         default=False, verbose_name=("Банковская карта"))

#     payment_other = RichTextField(default="", blank=True,
#                                   verbose_name=(
#                                       "Дополнительная информация об оплате"),
# help_text="Опишите любые другие условия и важные моменты по оплате —
# покупателю будет проще принять решение о покупке в вашем магазине.")

#     rules = RichTextField(default="", blank=True,
#                           verbose_name=(
#                               "Дополнительная информация об оплате"),
#                           help_text="Обозначьте условия возврата товаров. В течение какого времени после получения товара покупатель может обратиться? \
# Если вы не принимаете возвраты или обмены, чётко укажите на это, чтобы
# избежать споров в случае желания покупателя отказаться от покупки.")

#     on_vacation = models.BooleanField(
#         default=False, verbose_name=("На каникулах"), editable=False)

#     comments = CommentsField()

#     # def price_fields_validate(self, end_with):
#     #     fields = []
#     #     for f in self._meta.fields:
#     #         fname = f.name
#     #         try:
#     #             value = getattr(self, fname)
#     #         except AttributeError:
#     #             value = None

#     #         if fname.endswith(end_with) and f.editable and value and (f.name not in ('id', 'user', 'express_other')):
#     #             fields.append(
#     #                 {
#     #                     'label': f.verbose_name,
#     #                     'name': f.name,
#     #                     'value': value,
#     #                 }
#     #             )
#     #     return fields

#     def save(self, request=False, *args, **kwargs):
#         self.slug = slugify_unicode(self.shopname)
#         super(UserShop, self).save(*args, **kwargs)

#     def get_products_count(self):
#         return Product.objects.filter(shop=self.id).count()

#     def get_last_product(self):
#         return Product.objects.filter(shop=self.id).last()

#     def get_active_orders(self):
#         return 0

#     def get_absolute_url(self):
#         url_name = "shop-view"
#         kwargs = {"slug": self.slug}
#         return reverse(url_name, kwargs=kwargs)

#     def __str__(self):              # __unicode__ on Python 2
#         return str(self.shopname)


# class UserShopDeliveryOption(models.Model):
#     shop = models.ForeignKey(UserShop, related_name="deliveryoptions", verbose_name=_("Магазин"))
#     active = models.BooleanField(default=False)
#     label = models.CharField(_("Вид доставки"), max_length=255, null=False)
#     price = models.PositiveIntegerField(_("Цена"), null=True)

#     def __str__(self):              # __unicode__ on Python 2
#         return self.label


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
    href = models.ForeignKey(BlogPost,
                             verbose_name=_("Ссылка"),
                             blank=True, null=True, help_text="Ссылка куда будет ввести данный слайд.")

    slider = models.ForeignKey(Slider, related_name="images")

    def __str__(self):              # __unicode__ on Python 2
        return str(self.featured_image)

    class Meta:
        verbose_name = _("Элемент слайдера")
        verbose_name_plural = _("Элементы слайдера")


class RulesPage(Page):
    """docstring for RulesPage."""
    class Meta:
        verbose_name = _("Правила сайта")
        verbose_name_plural = _("Правила сайта")

    content = RichTextField(verbose_name=_("Правила"), blank=True)



# class OrderTableItem(models.Model):

#     class Meta:
#         verbose_name = _("Заказы")
#         verbose_name_plural = _("Мои заявки")
#         ordering = ("-created",)
#         permissions = (
#             ('view_ordertableitem', 'View order item'),
#         )

#     title = models.CharField(_("Название"), max_length=500, null=False)
#     active = models.BooleanField(_("Открыт"), default=True, editable=False)
#     created = models.DateField(
#         _("Дата добавления"), editable=False, default=date.today)
#     ended = models.DateField(
#         _("Крайний срок"), null=True, editable=True, blank=True, help_text="Оставьте пустым, если срок неограничен.", validators=[MinValueValidator(date.today())])
#     price = models.DecimalField(
#         _("Бюджет"), max_digits=8, decimal_places=0, default=0, blank=True, null=True,
#         help_text="Если Вы не представляете, сколько подобная работа могла бы стоить, оставьте поле незаполненным.", validators=[MinValueValidator(0)])
#     # count = models.PositiveIntegerField(_("Количество"),
#     # default=1, validators=[MinValueValidator(1)])
#     count = models.DecimalField(
#         _("Количество"), max_digits=8, decimal_places=0, default=1, validators=[MinValueValidator(1)])
#     color_suggest = models.CharField(
#         _("Пожелания к цвету"), max_length=500, blank=True, default="",
#         help_text="Пример: «небесно-голубой» или «любой».")
#     size_suggest = models.CharField(
#         _("Пожелания к размерам"), max_length=500, blank=True, default="",
#         help_text="Пример: «с футбольный мяч» или «длина - 30 см».")
#     material_suggest = models.CharField(
#         _("Пожелания к материалам"), max_length=500, blank=True, default="",
#         help_text="Пример: шерсть")
#     lock_in_region = models.BooleanField(
#         default=False, verbose_name=("Только мой регион"), help_text="Мастера из других регионов не получат уведомление о Вашем заказе")
#     description = RichTextField(
#         default="", verbose_name=("Подробное описание"),
#         help_text="Как можно более подробно опишите желаемое изделие.")

#     categories = models.ForeignKey("OrderTableItemCategory",
#                                    verbose_name=_("Виды работ"),
#                                    blank=False, null=False, related_name="ordertableitems")

#     # featured_image = models.ForeignKey(
#     #     "OrderTableItemImage", related_name="orderimages")
#     author = models.ForeignKey(
#         "auth.User", on_delete=models.CASCADE, blank=True, null=True, related_name="orders_author")

#     performer = models.ForeignKey(
#         'auth.User', on_delete=models.SET_NULL, blank=True, null=True, related_name="orders_perfmoer")

#     # objects = SearchableManager()
#     # search_fields = ("title", "description")

#     def __str__(self):              # __unicode__ on Python 2
#         return str(self.title)

#     def get_absolute_url(self):
#         url_name = "order_detail"
#         kwargs = {"pk": self.pk}
#         return reverse(url_name, kwargs=kwargs)

#     def save(self, request=False, *args, **kwargs):
#         if self.price == 0:
#             self.price = None
#         super(OrderTableItem, self).save(*args, **kwargs)

#     @property
#     def lifespan(self):
#         return '%s - present' % self.ended.strftime('%m/%d/%Y')


# class OrderTableItemImage(models.Model):
#     file = FileField(verbose_name=_("Изображение"),
#                      upload_to=upload_to(
#         "theme.OrderTableItem.image", "orders"),
#         format="Image", max_length=255, null=True, blank=True,
#         help_text="Загрузите фотографии эскизов или примеров, которые помогут мастерам точнее понять Ваш заказ.")
#     description = models.CharField(
#         _("Описание"), blank=True, max_length=100)

#     ordertableitem = models.ForeignKey(OrderTableItem, related_name='images')

#     class Meta:
#         verbose_name = _("Изображение")
#         verbose_name_plural = _("Изображения")

#     def __str__(self):
#         value = self.description
#         if not value:
#             value = self.file.name
#         if not value:
#             value = ""
#         return value


# class OrderTableItemRequest(models.Model):
#     """Each order item can have many users that requested to complete this order.
#     Such that each author can choose specific user to compelte his order."""
#     class Meta:
#         verbose_name = _("Отклики")
#         verbose_name_plural = _("Отклики на заявки")
#         ordering = ("order",)
#         unique_together = ('order', 'performer',)

#     order = models.ForeignKey(
#         OrderTableItem, on_delete=models.CASCADE, related_name="order_requests", verbose_name=("Заказы"))
#     performer = models.ForeignKey(
#         'auth.User', on_delete=models.CASCADE, related_name="order_performers", verbose_name=("Исполнители"))


# class OrderTableItemCategory(Slugged):
#     """
#     A category for grouping Order items into a series.
#     """

#     class Meta:
#         verbose_name = _("Вид работы")
#         verbose_name_plural = _("Виды работ")
#         ordering = ("title",)

#     @models.permalink
#     def get_absolute_url(self):
#         return ("order_list_category", (), {"category": self.slug})


# class ShopProduct(models.Model):

#     class Meta:
#         verbose_name = "Товар"
#         verbose_name_plural = _("Мои товары")

#     shop = models.ForeignKey(UserShop, on_delete=models.CASCADE, related_name="products", verbose_name=("Магазин"))

#     available = models.BooleanField(_("Доступен для заказа"), default=False)
#     categories = models.ManyToManyField(Category, blank=True, verbose_name=_("Категория"))
#     date_added = models.DateTimeField(_("Добавлено"), auto_now_add=True, null=True)
#     title = models.CharField(_("Название"), max_length=255, blank=False, default="",
#                              help_text="Название должно быть уникальным и описывать особенность товара.")
#     price = models.PositiveIntegerField(_("Цена"), default=0)
#     material = models.CharField(_("Материал"), max_length=255, blank=True, default="",
#                                 help_text="В точности как на бирке")
#     description = RichTextField(
#         default="", verbose_name=("Подробное описание"),
#         help_text="Как можно более подробно опишите товар.")
#     condition = models.CharField(
#         _("Материал"),
#         choices=settings.PRODUCT_STATUS_TYPE_CHOICES,
#         max_length=255,
#         blank=False,
#         default="Новое")

#     pre_order = models.BooleanField(
#         _("Для примера"),
#         default=False,
#         help_text="Отметьте, если данный товар может отличаться от итогового варианта.")

#     keywords = KeywordsField()
#     # objects = SearchableManager()
#     # search_fields = ("title", "description")

#     # like fields

#     slug = models.URLField(editable=False, default='')

#     def save(self, request=False, *args, **kwargs):
#         self.slug = slugify_unicode(self.title + str(self.id))
#         super(ShopProduct, self).save(*args, **kwargs)

#     def __str__(self):              # __unicode__ on Python 2
#         return str(self.title)

#     def get_absolute_url(self):
#         url_name = "product-detail"
#         kwargs = {"slug": self.slug}
#         return reverse(url_name, kwargs=kwargs)


# class ShopProductImage(models.Model):
#     file = FileField(verbose_name=_("Изображение"),
#                      upload_to=upload_to(
#         "theme.shopproduct.image", "orders"),
#         format="Image", max_length=255, null=True, blank=True,
#         help_text="Загрузите фотографии вашего товара.")

#     description = models.CharField(
#         _("Описание"), blank=True, max_length=100)

#     product = models.ForeignKey(ShopProduct, related_name='images')

#     class Meta:
#         verbose_name = _("Изображение")
#         verbose_name_plural = _("Изображения")

#     def __str__(self):
#         value = self.description
#         if not value:
#             value = self.file.name
#         if not value:
#             value = ""
#         return value


# class ShopRealtedCart(Cart):
#     """remove item's quantity and provide shop"""
#     objects = managers.CartManager()

#     def __iter__(self):
#         """
#         Allow the cart to be iterated giving access to the cart's items,
#         ensuring the items are only retrieved once and cached.
#         """
#         if not hasattr(self, "_cached_items"):
#             self._cached_items = self.cart_items.all()
#         return iter(self._cached_items)

#     def add_item(self, product, shop, quantity):
#         """
#         Increase quantity of existing item if SKU matches, otherwise create
#         new.
#         """
#         if not self.pk:
#             self.save()
#         print(product.actions)
#         kwargs = {"sku": product.id, "unit_price": product.price(), "shop": shop}
#         item, created = self.cart_items.get_or_create(**kwargs)
#         if created:
#             item.description = force_text(product)
#             item.unit_price = product.price()
#             item.url = product.get_absolute_url()
#             image = product.image
#             if image is not None:
#                 item.image = force_text(image)
#             product.actions.added_to_cart()
#         item.quantity += quantity
#         item.save()


# class ShopRealtedCartItem(SelectedProduct):

#     cart = models.ForeignKey("ShopRealtedCart", related_name="cart_items")
#     shop = models.ForeignKey(UserShop)

#     def get_absolute_url(self):
#         return self.url

#     def save(self, *args, **kwargs):
#         super(ShopRealtedCartItem, self).save(*args, **kwargs)

#         # Check if this is the last cart item being removed
#         if self.quantity == 0 and not self.cart.cart_items.exists():
#             self.cart.delete()

# class ShopRelatedCartItem(models.Model):

#     cart_item = models.ForeignKey(CartItem, related_name="cart_items")
#     cart_shop = models.ForeignKey(UserShop, related_name="cart_shop")

#     def save(self, *args, **kwargs):
#         super(ShopRelatedCartItem, self).save(*args, **kwargs)

#         # Check if this is the last cart item being removed
#         if self.quantity == 0 and not self.cart.items.exists():
#             self.cart.delete()
