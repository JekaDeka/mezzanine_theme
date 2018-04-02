from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from mezzanine.conf import settings
from mezzanine.utils.models import AdminThumbMixin, upload_to
from mezzanine.core.fields import FileField, RichTextField
from mezzanine.generic.fields import KeywordsField, CommentsField, RatingField

from cartridge.shop.models import Category

from theme.utils import slugify_unicode

from shops import managers

from profiles.models import UserProfile
from datetime import datetime


class UserShop(models.Model):
    """docstring for UserShop"""
    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = _("Все магазины")

    user = models.OneToOneField(
        "auth.User", related_name="shop", verbose_name="Владелец")
    image = FileField(upload_to=upload_to("shops.UserShop.image", "shops"),
                      verbose_name=_("Обложка магазина"), format="Image", max_length=255, blank=False, default="",
                      help_text="Загрузите логотип магазина.")

    background = FileField(upload_to=upload_to("shops.UserShop.image", "shops"),
                           verbose_name=_("Обложка магазина"), format="Image", max_length=255, blank=False, default="",
                           help_text="Загрузите обложку магазина.")

    shopname = models.CharField(max_length=255, blank=False, unique=True,
                                verbose_name=("Название магазина"))
    slug = models.URLField(editable=False, default='')
    bio = RichTextField(default="", verbose_name=("Описание"), blank=True,
                        help_text="Расскажите миру о Вашем творчестве, опишите свой продукт. \
                        Ваш бренд и то, что вы создаете своим трудом, являются единственными в своем роде - скажите, почему! \
                        Расскажите о себе, чем вы были воодушевлены, когда начали заниматься своим делом, что повлияло на ваш выбор, как развивается ваше творчество сейчас. \
                        Какие техники, материалы вы используете для своих изделий, каких принципов придерживаетесь при создании своего бренда. \
                        Ваш рассказ должен быть интересным, лаконичным, информативным и убедительным. Можете упомянуть любимую цитату или вдохновляющую идею. \
                        Не стоит злоупотреблять смайликами и прочими символами.")
    express_point = models.BooleanField(
        default=False, verbose_name=("Получение в вашем пункте выдачи"))
    express_point_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
                                              help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.",
                                              validators=[MinValueValidator(0)])
    express_city = models.BooleanField(
        default=False, verbose_name=("Курьером по г. Москва"))
    express_city_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
                                             help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.",
                                             validators=[MinValueValidator(0)])
    express_country = models.BooleanField(default=False, verbose_name=(
        "Курьером по стране (Российская Федерация)"))
    express_country_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
                                                help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.",
                                                validators=[MinValueValidator(0)])
    express_world = models.BooleanField(
        default=False, verbose_name=("Курьером по миру"))
    express_world_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
                                              help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.",
                                              validators=[MinValueValidator(0)])
    express_mail = models.BooleanField(
        default=False, verbose_name=("Почта России"))
    express_mail_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
                                             help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.",
                                             validators=[MinValueValidator(0)])
    express_personal = models.BooleanField(
        default=False, verbose_name=("Личная встреча"))
    express_personal_price = models.DecimalField(_("Цена доставки"), max_digits=8, decimal_places=0, default='', blank=True, null=True,
                                                 help_text="Оставляйте поле пустым, если стоимость будет рассчитана по запросу.",
                                                 validators=[MinValueValidator(0)])

    express_other = RichTextField(default="", blank=True,
                                  verbose_name=(
                                      "Дополнительная информация о доставке"),
                                  help_text="Адреса, по которым покупатель сможет забрать товар самостоятельно. Любые другие нюансы и условия по доставке.")

    payment_personal = models.BooleanField(
        default=False, verbose_name=("Наличными при получении"))
    payment_bank_transfer = models.BooleanField(
        default=False, verbose_name=("Банковский перевод"))
    payment_card_transfer = models.BooleanField(
        default=False, verbose_name=("Банковская карта"))

    payment_other = RichTextField(default="", blank=True,
                                  verbose_name=(
                                      "Дополнительная информация об оплате"),
                                  help_text="Опишите любые другие условия и важные моменты по оплате — покупателю будет проще принять решение о покупке в вашем магазине.")

    rules = RichTextField(default="", blank=True,
                          verbose_name=(
                              "Дополнительная информация об оплате"),
                          help_text="Обозначьте условия возврата товаров. В течение какого времени после получения товара покупатель может обратиться? \
                          Если вы не принимаете возвраты или обмены, чётко укажите на это, чтобы избежать споров в случае желания покупателя отказаться от покупки.")

    on_vacation = models.BooleanField(
        default=False, verbose_name=("На каникулах"), editable=False)

    # comments = CommentsField()

    def get_express_fields(self):
        choices = []
        for f in self._meta.fields:
            fname = f.name
            if fname.endswith('_price') and (f.name not in ('express_other'),):
                try:
                    value = getattr(self, fname)
                except AttributeError:
                    value = None
                try:
                    label_name = self._meta.get_field(fname[:-6]).verbose_name
                except AttributeError:
                    label_name = None
                if value and label_name:
                    choices.insert(0, (label_name, label_name + ' - ' +  str(value) + 'руб') )
        return choices

    # def price_fields_validate(self, end_with):
    #     fields = []
    #     for f in self._meta.fields:
    #         fname = f.name
            # try:
            #     value = getattr(self, fname)
            # except AttributeError:
            #     value = None

    #         if fname.endswith(end_with) and f.editable and value and (f.name not in ('id', 'user', 'express_other')):
    #             fields.append(
    #                 {
    #                     'label': f.verbose_name,
    #                     'name': f.name,
    #                     'value': value,
    #                 }
    #             )
    #     return fields

    def save(self, request=False, *args, **kwargs):
        self.slug = slugify_unicode(self.shopname)
        super(UserShop, self).save(*args, **kwargs)

    def get_products_count(self):
        return ShopProduct.objects.annotate(product_count=models.Count("id")).filter(shop=self.id)

    def get_last_product(self):
        return ShopProduct.objects.filter(shop=self.id).last()

    def get_active_orders(self):
        return 0

    def get_absolute_url(self):
        url_name = "shop-view"
        kwargs = {"slug": self.slug}
        return reverse(url_name, kwargs=kwargs)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.shopname)


class UserShopDeliveryOption(models.Model):
    shop = models.ForeignKey(
        UserShop, related_name="deliveryoptions", verbose_name=_("Магазин"))
    active = models.BooleanField(default=False)
    label = models.CharField(_("Вид доставки"), max_length=255, null=False)
    price = models.PositiveIntegerField(_("Цена"), null=True)

    def __str__(self):              # __unicode__ on Python 2
        return self.label


class ShopProduct(models.Model):

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = _("Мои товары")

    shop = models.ForeignKey(UserShop, on_delete=models.CASCADE,
                             related_name="products", verbose_name=("Магазин"))

    available = models.BooleanField(_("Доступен для заказа"), default=False)
    categories = models.ManyToManyField(Category, blank=True, verbose_name=_(
        "Категория"), help_text="Разместить работу можно только в одной категории.")
    date_added = models.DateTimeField(
        _("Добавлено"), auto_now_add=True, null=True)
    title = models.CharField(_("Название"), max_length=255, blank=False, default="",
                             help_text="Название должно быть уникальным и описывать особенность товара.")
    price = models.PositiveIntegerField(_("Цена"), default=0)
    material = models.CharField(_("Материал"), max_length=255, blank=True, default="",
                                help_text="В точности как на бирке")
    description = RichTextField(
        default="", verbose_name=("Подробное описание"),
        help_text="Как можно более подробно опишите товар.")
    condition = models.CharField(
        _("Состояние"),
        choices=settings.PRODUCT_STATUS_TYPE_CHOICES,
        max_length=255,
        blank=False,
        default=settings.PRODUCT_STATUS_TYPE_CHOICES[0][0], help_text="Готовая работа - работа уже ждет покупателя. Под заказ - Вы можете выполнить точно такую же работу, но потребуется некоторое время. Для примера - повторить работу точь-в-точь невозможно.")

    pre_order = models.BooleanField(
        _("Удалить"),
        default=False,
        help_text="Удалить поле")

    main_image = models.CharField(
        _("Изображение"), max_length=255, blank=True, default="")

    keywords = KeywordsField()
    # objects = SearchableManager()
    # search_fields = ("title", "description")

    # like fields

    slug = models.URLField(editable=False, default='')

    def save(self, request=False, *args, **kwargs):
        self.slug = slugify_unicode(self.title + str(self.id))
        img = self.images.first()
        if img:
            self.main_image = img.file
        else:
            self.main_image = ""
        super(ShopProduct, self).save(*args, **kwargs)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.title)

    def get_absolute_url(self):
        url_name = "product-detail"
        kwargs = {"slug": self.slug}
        return reverse(url_name, kwargs=kwargs)

    def get_categories(self):
        return self.categories.all().order_by('id')


class ShopProductImage(models.Model):
    file = FileField(verbose_name=_("Изображение"),
                     upload_to=upload_to(
        "theme.shopproduct.image", "orders"),
        format="Image", max_length=255, null=True, blank=True,
        help_text="Загрузите фотографии вашего товара.")

    description = models.CharField(
        _("Описание"), blank=True, max_length=100)

    product = models.ForeignKey(ShopProduct, related_name='images')

    class Meta:
        verbose_name = _("Изображение")
        verbose_name_plural = _("Изображения")

    def __str__(self):
        value = self.description
        if not value:
            value = self.file.name
        if not value:
            value = ""
        return value


class SelectedProduct(models.Model):
    """
    Abstract model representing a "selected" product in a cart or order.
    """
    sku = models.IntegerField(_("true_product_id"), default=0)
    title = models.CharField(_("Название"), max_length=255)
    quantity = models.IntegerField(_("Количество"), default=0)
    price = models.PositiveIntegerField(_("Цена"), default=0)
    total_price = models.PositiveIntegerField(_("Общая сумма"), default=0)
    image = models.CharField(max_length=200, null=True)
    url = models.CharField(max_length=2000)

    # shop_id = models.IntegerField(_("shop_id"), default=0)
    # shop_image = models.CharField(max_length=200, null=True)
    # shop_slug = models.CharField(max_length=255)
    # shop_name = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return ""

    # def shop_fields(self):
    #     return "%s,%s" % (self.shop_name, self.shop_slug, self.shop_name)

    def get_absolute_url(self):
        return self.url

    def save(self, *args, **kwargs):
        """
        Set the total price based on the given quantity. If the
        quantity is zero, which may occur via the cart page, just
        delete it.
        """
        if not self.id or self.quantity > 0:
            self.total_price = self.price * self.quantity
            super(SelectedProduct, self).save(*args, **kwargs)
        else:
            self.delete()


class Order(models.Model):
    """docstring for Order."""
    status = models.IntegerField(_("Status"),
                                 choices=settings.SHOP_ORDER_STATUS_CHOICES,
                                 default=settings.SHOP_ORDER_STATUS_CHOICES[0][0])
    time = models.DateTimeField(_("Time"), auto_now_add=True, null=True)
    shop = models.ForeignKey("UserShop", related_name="orders")

    user_id = models.IntegerField(blank=True, null=True)
    user_first_name = models.CharField(_("First name"), max_length=255)
    user_middle_name = models.CharField(_("Отчество"), max_length=255, blank=True)
    user_last_name = models.CharField(_("Last name"), max_length=255)
    user_phone = models.CharField(_("Phone"), max_length=20)
    user_email = models.EmailField(_("Email"), max_length=255)

    user_country = models.CharField(_("Country"), max_length=100)
    user_city = models.CharField(_("City/Suburb"), max_length=100)
    user_region = models.CharField("Регион", max_length=100)


    shipping_type = models.CharField(_("Доставка"), max_length=255, default="")
    shipping_price = models.PositiveIntegerField(_("Цена доставки"), default=0)

    user_address =  models.CharField(_("Адрес"), max_length=255, blank=True, help_text="Улица, дом, подъезд, квартира")
    user_postcode = models.CharField(_("Zip/Postcode"), max_length=15, blank=True)
    user_additional_info = models.TextField("Пожелания по заказку", blank=True)

    item_total = models.PositiveIntegerField(_("Сумма заказа"), default=0)
    total = models.PositiveIntegerField(_("Всего"), default=0)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = _("Все заказы")
        ordering = ("-id",)

    def __str__(self):
        return "%s %s" % (self.billing_name(), self.time)

    def billing_name(self):
        return "%s %s" % (self.user_first_name,
                          self.user_last_name)

    def complete(self, request, form):
        self.shop = form.shop
        if request.user.is_authenticated():
            self.user_id = request.user.id
        else:
            pass
            ### create user -> activate -> send_email -> #create_profile

        self.item_total = request.cart.total_price_for_shop(form.shop.id)
        self.total = self.item_total + self.shipping_price
        self.save()
        for item in request.cart.get_shop_items(form.shop.id):
            product_fields = [f.name for f in SelectedProduct._meta.fields]
            item = dict([(f, getattr(item, f)) for f in product_fields])
            self.items.create(**item)

        request.cart.items.filter(shop_id=form.shop.id).delete()



class OrderItem(SelectedProduct):
    """docstring for OrderProduct."""
    order = models.ForeignKey("Order", related_name="items")
    product = models.ForeignKey(
        ShopProduct, related_name="in_orders", null=True, on_delete=models.SET_NULL)


class Cart(models.Model):
    """docstring for Cart."""

    last_updated = models.DateTimeField(
        _("Last updated"), null=True, auto_now=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    user = models.OneToOneField(
        "auth.User", related_name="cart", verbose_name="Покупатель", null=True)
    objects = managers.CartManager()

    def __iter__(self):
        """
        Allow the cart to be iterated giving access to the cart's items,
        ensuring the items are only retrieved once and cached.
        """
        if not hasattr(self, "_cached_items"):
            self._cached_items = self.items.all()
        return iter(self._cached_items)

    def add_item(self, product, quantity, shop_name):
        """
        Increase quantity of existing item if id matches, otherwise create
        new.
        """
        self.last_updated = now()
        self.save()
        kwargs = {"sku": int(product.id), "price": int(
            product.price), "product": product}
        item, created = self.items.get_or_create(**kwargs)
        if created:
            item.sku = int(product.id)
            item.title = force_text(product.title)
            item.price = int(product.price)
            item.url = product.get_absolute_url()
            item.image = force_text(product.main_image)

            item.shop_id = int(product.shop.id)
            item.shop_image = force_text(product.shop.image)
            item.shop_slug = force_text(product.shop.slug)
            item.shop_name = force_text(product.shop.shopname)
            # item.product = int(product.pk)

        item.quantity += quantity
        item.save()

    def has_items(self):
        """
        Template helper function - does the cart have items?
        """
        return len(list(self)) > 0

    def get_shop_data(self, shop_id=None):
        shop_name = ""
        shop_slug = ""
        shop_image = ""
        quantity = 0
        total_price = 0
        for item in self:
            if item.shop_id == shop_id:
                shop_name = item.shop_name
                shop_slug = item.shop_slug
                shop_image = item.shop_image
                quantity += item.quantity
                total_price += item.total_price
        return [shop_name, shop_slug, shop_image, quantity, total_price]

    def get_shop_items(self, shop_id=None):
        return [item for item in self if item.shop_id == shop_id]

    def total_quantity_for_shop(self, shop_id=None):
        return sum([item.quantity for item in self if item.shop_id == shop_id])

    def total_price_for_shop(self, shop_id=None):
        return sum([item.total_price for item in self if item.shop_id == shop_id])

    def total_quantity(self):
        """
        Template helper function - sum of all item quantities.
        """
        return sum([item.quantity for item in self])

    def total_price(self):
        """
        Template helper function - sum of all costs of item quantities.
        """
        return sum([item.total_price for item in self])


class CartItem(SelectedProduct):
    """docstring for CartItem."""
    cart = models.ForeignKey("Cart", related_name="items")
    shop_id = models.IntegerField(_("shop_id"), default=0)
    shop_image = models.CharField(max_length=200, null=True)
    shop_slug = models.CharField(max_length=255)
    shop_name = models.CharField(max_length=255)
    product = models.ForeignKey(
        ShopProduct, related_name="in_cart", on_delete=models.CASCADE)

    def shop_fields(self):
        return "%s,%s" % (self.shop_name, self.shop_slug, self.shop_name)
