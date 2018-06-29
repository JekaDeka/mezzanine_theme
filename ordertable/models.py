from django.db import models
from mezzanine.utils.models import AdminThumbMixin, upload_to

from mezzanine.core.models import Slugged, Displayable
from mezzanine.core.fields import FileField, RichTextField
from mezzanine.core.managers import SearchableManager
from mezzanine.generic.fields import KeywordsField, CommentsField, RatingField
from mezzanine.conf import settings

from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse


from ordertable.managers import OrderTableItemManager

from theme.utils import slugify_unicode

from datetime import date


def validate_today(value):
    if value < date.today():
        raise ValidationError(
            _('Убедитесь, что выбрали дату не позднее сегодняшней'),
            params={'value': value},
        )


class OrderTableItem(models.Model):

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        ordering = ("-created",)
        permissions = (
            ('view_ordertableitem', 'View order item'),
        )

    objects = OrderTableItemManager()
    search_fields = ("title", "description", "keywords_string")

    title = models.CharField(_("Название"), max_length=500, null=False)
    available = models.BooleanField(_("Отображать на сайте"), default=False)

    status = models.IntegerField(
        _("Состояние"),
        choices=settings.ORDER_TABLE_STATUS_CHOICES,
        default=settings.ORDER_TABLE_STATUS_CHOICES[0][0],
        editable=False)

    created = models.DateField(
        _("Дата добавления"), editable=False, default=date.today)
    ended = models.DateField(
        _("Крайний срок"), null=True, editable=True, blank=True, help_text="Оставьте пустым, если срок неограничен.", validators=[validate_today])
    price = models.PositiveIntegerField(
        _("Бюджет"), default=0, blank=True, null=True,
        help_text="Если Вы не представляете, сколько подобная работа могла бы стоить, оставьте поле незаполненным.", validators=[MinValueValidator(0)])
    count = models.PositiveIntegerField(_("Количество"), default=1, validators=[MinValueValidator(1)])
    # count = models.DecimalField(
    #     _("Количество"), max_digits=8, decimal_places=0, default=1, validators=[MinValueValidator(1)])
    color_suggest = models.CharField(
        _("Пожелания к цвету"), max_length=500, blank=True, default="",
        help_text="Пример: «небесно-голубой» или «любой».")
    size_suggest = models.CharField(
        _("Пожелания к размерам"), max_length=500, blank=True, default="",
        help_text="Пример: «с футбольный мяч» или «длина - 30 см».")
    material_suggest = models.CharField(
        _("Пожелания к материалам"), max_length=500, blank=True, default="",
        help_text="Пример: шерсть")
    lock_in_region = models.BooleanField(
        default=False, verbose_name=("Только мой регион"), help_text="Мастера из других регионов не получат уведомление о Вашем заказе")

    region = models.ForeignKey("profiles.Region",
                                   verbose_name=_("Регион"),
                                   blank=True, null=True,
                                   editable=True)

    description = models.TextField(
        default="", verbose_name=("Подробное описание"),
        help_text="Как можно более подробно опишите желаемое изделие.")

    categories = models.ForeignKey("OrderTableItemCategory",
                                   verbose_name=_("Виды работ"),
                                   blank=False, null=False, related_name="ordertableitems")

    # featured_image = models.ForeignKey(
    #     "OrderTableItemImage", related_name="orderimages")
    author = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, blank=True, null=True, related_name="orders_as_author")

    performer = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, blank=True, null=True, related_name="orders_as_performer")

    # objects = SearchableManager()
    # search_fields = ("title", "description")
    main_image = models.CharField(
        _("Изображение"), max_length=255, blank=True, default="")

    keywords = KeywordsField()

    def __str__(self):              # __unicode__ on Python 2
        return str(self.title)

    def get_absolute_url(self):
        url_name = "order_detail"
        kwargs = {"pk": self.pk}
        return reverse(url_name, kwargs=kwargs)

    def save(self, request=False, *args, **kwargs):
        if self.price == 0:
            self.price = None
        img = self.images.first()
        if img:
            self.main_image = img.file
        else:
            self.main_image = ""

        if not self.region:
            self.region = self.author.profile.region

        if self.performer:
            self.status = settings.ORDER_TABLE_STATUS_CHOICES[1][0]
        else:
            self.status = settings.ORDER_TABLE_STATUS_CHOICES[0][0]

        if self.status == 3:
            ## if order completed
            ### rework
            ### TODO:
            ### проработать вариант отметы заказа
            ### запретить после выполнения???
            self.performer.profile.orders_done += 1
            
        super(OrderTableItem, self).save(*args, **kwargs)

    @property
    def lifespan(self):
        return '%s - present' % self.ended.strftime('%m/%d/%Y')


class OrderTableItemImage(models.Model):
    file = FileField(verbose_name=_("Изображение"),
                     upload_to=upload_to(
        "theme.OrderTableItem.image", "orders"),
        format="Image", max_length=255, null=True, blank=True,
        help_text="Загрузите фотографии эскизов или примеров, которые помогут мастерам точнее понять Ваш заказ.")
    description = models.CharField(
        _("Описание"), blank=True, max_length=100)

    ordertableitem = models.ForeignKey(OrderTableItem, related_name='images')

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


class OrderTableItemRequest(models.Model):
    """Each order item can have many users that requested to complete this order.
    Such that each author can choose specific user to compelte his order."""
    class Meta:
        verbose_name = _("Отклики")
        verbose_name_plural = _("Отклики на заявки")
        ordering = ("order",)
        unique_together = ('order', 'performer',)

    order = models.ForeignKey(
        OrderTableItem, on_delete=models.CASCADE, related_name="order_requests", verbose_name=("Заказ"))
    performer = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name="order_performers", verbose_name=("Исполнитель"))

    # def __str__(self):
    #     return performer.profile.get_full_name()


class OrderTableItemCategory(Slugged):
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
