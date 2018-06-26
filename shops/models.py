from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from mezzanine.conf import settings
from mezzanine.utils.models import AdminThumbMixin, upload_to
from mezzanine.utils.urls import unique_slug
from mezzanine.core.fields import FileField, RichTextField
from mezzanine.generic.fields import KeywordsField, CommentsField, RatingField

from cartridge.shop.models import Category

from theme.utils import slugify_unicode

from shops import managers

from profiles.models import UserProfile, Country, Region, City
from smart_selects.db_fields import ChainedForeignKey, GroupedForeignKey
from datetime import datetime


import random
import string
# Sample of an ID generator - could be any string/number generator
# For a 6-char field, this one yields 2.1 billion unique IDs


def id_generator(size=7, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class UserShop(models.Model):
    """docstring for UserShop"""
    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = _("Все магазины")

    user = models.OneToOneField(
        "auth.User", related_name="shop", verbose_name="Владелец", on_delete=models.CASCADE)
    image = FileField(upload_to=upload_to("shops.UserShop.image", "shops"),
                      verbose_name=_("Обложка магазина"), format="Image", max_length=255, blank=False, default="",
                      help_text="Загрузите логотип магазина.")

    background = FileField(upload_to=upload_to("shops.UserShop.image", "shops"),
                           verbose_name=_("Обложка магазина"), format="Image", max_length=255, blank=False, default="",
                           help_text="Загрузите обложку магазина.")

    shopname = models.CharField(max_length=255, blank=False, unique=True,
                                verbose_name=("Название магазина"))
    slug = models.URLField(editable=False, default='')
    bio = models.TextField(default="", verbose_name=("Описание"), blank=True,
                        help_text="Расскажите миру о Вашем творчестве, опишите свой продукт. \
                        Ваш бренд и то, что вы создаете своим трудом, являются единственными в своем роде - скажите, почему! \
                        Расскажите о себе, чем вы были воодушевлены, когда начали заниматься своим делом, что повлияло на ваш выбор, как развивается ваше творчество сейчас. \
                        Какие техники, материалы вы используете для своих изделий, каких принципов придерживаетесь при создании своего бренда. \
                        Ваш рассказ должен быть интересным, лаконичным, информативным и убедительным. Можете упомянуть любимую цитату или вдохновляющую идею. \
                        Не стоит злоупотреблять смайликами и прочими символами.")

    delivery_options = models.ManyToManyField(
        'UserShopDelivery', through='UserShopDeliveryOption')
    delivery_other = models.TextField(default="", blank=True,
                                   verbose_name=(
                                       "Дополнительная информация о доставке"),
                                   help_text="Адреса, по которым покупатель сможет забрать товар самостоятельно. Любые другие нюансы и условия по доставке.")

    payment_options = models.ManyToManyField(
        'UserShopPayment', verbose_name=_("Способы оплаты"), help_text="")

    payment_other = models.TextField(default="", blank=True,
                                  verbose_name=(
                                      "Дополнительная информация об оплате"),
                                  help_text="Опишите любые другие условия и важные моменты по оплате — покупателю будет проще принять решение о покупке в вашем магазине.")

    rules = models.TextField(default="", blank=True,
                          verbose_name=(
                              "Правила возврата и обмена"),
                          help_text="Обозначьте условия возврата товаров. В течение какого времени после получения товара покупатель может обратиться? \
                          Если вы не принимаете возвраты или обмены, чётко укажите на это, чтобы избежать споров в случае желания покупателя отказаться от покупки.")

    on_vacation = models.BooleanField(
        default=False, verbose_name=("На каникулах"), editable=False)

    def save(self, request=False, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super(UserShop, self).save(*args, **kwargs)

    def generate_unique_slug(self):
        """
        Create a unique slug by passing the result of get_slug() to
        utils.urls.unique_slug, which appends an index if necessary.
        """
        # For custom content types, use the ``Page`` instance for
        # slug lookup.
        slug_qs = UserShop.objects.exclude(id=self.id)
        return unique_slug(slug_qs, "slug", self.get_slug())

    def get_slug(self):
        """
        Allows subclasses to implement their own slug creation logic.
        """
        return slugify_unicode(self.shopname)

    def get_products_count(self):
        return self.products.count()

    def get_last_product(self):
        return self.products.last()

    def get_active_orders(self):
        return 0

    def get_related_products(self):
        return self.products.only(
            'id',
            'available',
            'slug',
            'price',
            'shop__id',
            'condition',
            'title',

        ).filter(available=True).prefetch_related('images')[:settings.SHOP_MAX_RELATED_PRODUCTS]

    def get_delivery_options(self):
        return self.delivery_options.values('label', 'usershopdeliveryoption__price').all()

    def get_delivery_options_for_form(self):
        return self.delivery_options.values('id', 'label', 'usershopdeliveryoption__price')

    def get_absolute_url(self):
        url_name = "shop-view"
        kwargs = {"slug": self.slug}
        return reverse(url_name, kwargs=kwargs)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.shopname)


class UserShopPayment(models.Model):
    class Meta:
        verbose_name = "Способ оплаты"
        verbose_name_plural = _("Способы оплаты")
    label = models.CharField(_("Способ доставки"), max_length=255, null=False)

    def __str__(self):              # __unicode__ on Python 2
        return self.label


class UserShopDelivery(models.Model):
    class Meta:
        verbose_name = "Способ доставки"
        verbose_name_plural = _("Способы доставки")
    label = models.CharField(_("Способ доставки"), max_length=255, null=False)

    def __str__(self):              # __unicode__ on Python 2
        return self.label


class UserShopDeliveryOption(models.Model):
    class Meta:
        verbose_name = "Способ доставки магазина"
        verbose_name_plural = _("Способы доставки магазина")
        # auto_created = False

    shop = models.ForeignKey(UserShop, on_delete=models.CASCADE)
    delivery = models.ForeignKey(UserShopDelivery, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(_("Цена"), default=0)

    def __str__(self):              # __unicode__ on Python 2
        return "%s - %s ₽" % (self.delivery, self.price)

    # def __html__(self):
    #     return mark_safe(
    #         '<span style="color: red">Number is {0}</span>'.format(self.price))


class ShopProduct(models.Model):

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = _("Товары")

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
    size = models.CharField(_("Размер"), max_length=255, blank=True, default="",
                            help_text="Укажите размеры товара")
    description = models.TextField(
        default="", verbose_name=("Описание"),
        help_text="Как можно более подробно опишите товар.")
    condition = models.IntegerField(
        _("Состояние"),
        choices=settings.PRODUCT_STATUS_TYPE_CHOICES,
        blank=False,
        default=settings.PRODUCT_STATUS_TYPE_CHOICES[0][0], help_text="Готовая работа - работа уже ждет покупателя. Под заказ - Вы можете выполнить точно такую же работу, но потребуется некоторое время. Для примера - повторить работу точь-в-точь невозможно.")

    main_image = models.CharField(
        _("Изображение"), max_length=255, blank=True, default="")

    keywords = KeywordsField()
    reviews_count = models.IntegerField(default=0, editable=True)
    reviews_sum = models.IntegerField(default=0, editable=False)
    reviews_average = models.FloatField(default=0, editable=False)
    # comments = CommentsField()
    # rating = RatingField()
    # objects = SearchableManager()
    # search_fields = ("title", "description")

    # like fields

    slug = models.URLField(editable=False, default='', unique=True)

    def save(self, request=False, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()

        img = self.images.first()
        if img:
            self.main_image = img.file
        else:
            self.main_image = ""
        super(ShopProduct, self).save(*args, **kwargs)

    def generate_unique_slug(self):
        """
        Create a unique slug by passing the result of get_slug() to
        utils.urls.unique_slug, which appends an index if necessary.
        """
        # For custom content types, use the ``Page`` instance for
        # slug lookup.
        slug_qs = ShopProduct.objects.exclude(id=self.id)
        return unique_slug(slug_qs, "slug", self.get_slug())

    def get_slug(self):
        """
        Allows subclasses to implement their own slug creation logic.
        """
        return slugify_unicode(self.title)

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

    class Meta:
        abstract = True

    def __str__(self):
        return ""

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
    number = models.CharField(
        _("Номер заказа"), max_length=7, null=True, blank=True, unique=True)

    shop = models.ForeignKey("UserShop", related_name="orders",
                             on_delete=models.CASCADE, verbose_name=_("Магазин"))

    user_id = models.IntegerField(blank=True, null=True)
    user_first_name = models.CharField(_("First name"), max_length=255)
    user_middle_name = models.CharField(
        _("Отчество"), max_length=255, blank=True)
    user_last_name = models.CharField(_("Last name"), blank=True, max_length=255)
    user_phone = models.CharField(_("Phone"), blank=True, max_length=20)
    user_email = models.EmailField(_("Почта"), max_length=255)
    user_country = models.ForeignKey(Country, verbose_name=("Страна"))

    user_region = ChainedForeignKey(
        Region,
        chained_field="user_country",
        chained_model_field="country",
        show_all=False,
        auto_choose=True,
        sort=True, verbose_name=("Регион"))
    user_city = ChainedForeignKey(
        City,
        chained_field="user_region",
        chained_model_field="region",
        show_all=False,
        auto_choose=True,
        sort=True, verbose_name=("Город"))

    shipping_type = models.CharField(_("Доставка"), max_length=255, default="")
    shipping_price = models.PositiveIntegerField(_("Цена доставки"), default=0)

    shipping = models.ForeignKey("UserShopDeliveryOption", verbose_name=_(
        "Доставка"), null=True, on_delete=models.SET_NULL)

    payment = models.ForeignKey("UserShopPayment", verbose_name=_(
        "Оплата"), null=True, on_delete=models.SET_NULL)

    user_address = models.CharField(
        _("Адрес"), max_length=255, blank=True, help_text="Улица, дом, подъезд, квартира")
    user_postcode = models.CharField(
        _("Zip/Postcode"), max_length=15, blank=True)
    user_additional_info = models.TextField("Пожелания по заказку", blank=True, help_text="Напишите ваши пожелания по способу и времени доставки, требуемый размер, а также любые вопросы по товару.")

    item_quantity_total = models.PositiveIntegerField(
        _("Количество товаров"), default=0)
    item_total = models.PositiveIntegerField(_("Сумма заказа"), default=0)
    total = models.PositiveIntegerField(_("Итого по заказу"), default=0)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = _("Заказы")
        ordering = ("-id",)

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if not self.number:
            # Generate ID once, then check the db. If exists, keep trying.
            self.number = id_generator()
            while Order.objects.filter(number=self.number).exists():
                self.number = id_generator()

        super(Order, self).save(*args, **kwargs)

    # def get_absolute_url(self):
    #     url_name = "shop-order-detail"
    #     kwargs = {"pk": self.pk}
    #     return reverse(url_name, kwargs=kwargs)

    def billing_name(self):
        return "%s %s" % (self.user_first_name,
                          self.user_last_name)

    def complete(self, request, form):
        self.shop = form.shop
        if request.user.is_authenticated():
            self.user_id = request.user.id
        else:
            pass
            # create user -> activate -> send_email -> #create_profile

        self.item_quantity_total = request.cart.total_quantity_for_shop(
            form.shop.id)
        self.item_total = request.cart.total_price_for_shop(form.shop.id)
        self.shipping_type = self.shipping.delivery.label
        self.shipping_price = self.shipping.price
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
        ShopProduct, related_name="in_orders", blank=True, null=True, on_delete=models.SET_NULL)


class Cart(models.Model):
    """docstring for Cart."""

    last_updated = models.DateTimeField(
        _("Last updated"), null=True, auto_now=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    user = models.ForeignKey(
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

    def add_item(self, product, quantity):
        """
        Increase quantity of existing item if id matches, otherwise create
        new.
        """
        if not self.pk:
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
            # item.product = int(product.pk)

        item.quantity += quantity
        item.save()

    def has_items(self):
        """
        Template helper function - does the cart have items?
        """
        return len(list(self)) > 0

    def get_shop_data(self, shop_id=None):
        quantity = 0
        total_price = 0
        for item in self:
            if item.shop_id == shop_id:
                quantity += item.quantity
                total_price += item.total_price
        return [quantity, total_price]

    def get_shop_items(self, shop_id=None):
        return [item for item in self if item.shop_id == shop_id]

    def total_quantity_for_shop(self, shop_id=None):
        return sum([item.quantity for item in self if item.shop_id == shop_id])

    def total_price_for_shop(self, shop_id=None):
        return sum([item.total_price for item in self if item.shop_id == shop_id])

    def get_shops_id_list(self):
        uniqueList = []
        for item in self:
            if item.shop_id not in uniqueList:
                uniqueList.append(item.shop_id)
        return uniqueList

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
    product = models.ForeignKey(
        ShopProduct, related_name="in_cart", on_delete=models.CASCADE)


# hard code review + rating
class ProductReview(models.Model):
    class Meta:
        verbose_name = "Отзыв о товаре"
        verbose_name_plural = _("Отзывы о товарах")
        unique_together = ("author", "product")

    created_at = models.DateTimeField(default=timezone.now)

    approved = models.BooleanField(
        default=False, verbose_name=("Одобрен"))

    rating = models.IntegerField(verbose_name=(
        "Рейтинг"), choices=settings.RATING_CHOICES, default=settings.RATING_CHOICES[0][0])

    content = models.TextField(verbose_name=("Отзыв"))

    author = models.ForeignKey("auth.User", on_delete=models.CASCADE,
                               related_name="author_product_reviews", verbose_name=("Автор"), editable=False)

    product = models.ForeignKey(ShopProduct, on_delete=models.CASCADE,
                                related_name="product_reviews", verbose_name=("Товар"), editable=False)

    def save(self, *args, **kwargs):
        super(ProductReview, self).save(*args, **kwargs)
        print('PRODUCT_RATING_UPDATE')
        ratings = [r.rating for r in ProductReview.objects.filter(product=self.product, approved=True)]
        count = len(ratings)
        _sum = sum(ratings)
        average = _sum / count if count > 0 else 0
        self.product.reviews_count = count
        self.product.reviews_sum = _sum
        self.product.reviews_average = average
        self.product.save()
