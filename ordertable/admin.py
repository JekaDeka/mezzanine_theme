from django.contrib import admin
from ordertable.forms import OrderTableAdminForm
from ordertable.models import OrderTableItem, OrderTableItemImage, OrderTableItemRequest, OrderTableItemCategory
from django.utils.html import format_html


class OrderTableImageInline(admin.TabularInline):
    model = OrderTableItemImage
    extra = 2

@admin.register(OrderTableItem)
class OrderTableAdmin(admin.ModelAdmin):
    view_on_site = True
    list_display = ('title', 'available', 'created', 'price', 'ended',
                    'get_performer', 'view_on_site')
    list_editable = ('available',)
    form = OrderTableAdminForm
    inlines = [OrderTableImageInline, ]

    def view_on_site(self, obj):
        return format_html("<a href={}>Посмотреть на сайте</a>", obj.get_absolute_url())
    view_on_site.short_description = ""

    def get_performer(self, obj):
        if obj.performer:
            return obj.performer.get_full_name()
        return obj.performer
    get_performer.short_description = 'Исполнитель'

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()

    def get_queryset(self, request):
        qs = super(OrderTableAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    # def format_date(self, obj):
    #     return obj.ended.strftime('%d %b %Y %H:%M')

    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     field = super(OrderTableAdmin, self).formfield_for_dbfield(
    #         db_field, **kwargs)

    #     if isinstance(db_field, models.DateField):
    #         return forms.DateField(input_formats=('%d/%m/%Y',))
    #     return field


@admin.register(OrderTableItemRequest)
class OrderTableItemRequestAdmin(admin.ModelAdmin):
    model = OrderTableItemRequest
    # list_display = ('order', 'get_performers', 'view_on_site')
    list_display_links = None

    # def view_on_site(self, obj):
    #     return format_html("<a href={}>Посмотреть на сайте</a>", obj.get_absolute_url())
    # view_on_site.short_description = ""

    # def get_queryset(self, request):
    #     qs = super(OrderTableItemRequestAdmin, self).get_queryset(request)
    #     orders = OrderTableItem.objects.filter(
    #         performer=None).filter(order_requests__in=qs).distinct()
    #     if not request.user.is_superuser:
    #         orders.filter(author=request.user)

    #     if orders:
    #         return orders
    #     else:
    #         return OrderTableItem.objects.none()
    #     # if OrderTableItemRequest.objects.filter(order__in=qs):
    #     #     if request.user.is_superuser:
    #     #         return qs.filter()
    #     #     return qs.filter(author=request.user)
    #     # else:
    #     #     return OrderTableItem.objects.none()

    # def order(self, obj):
    #     return obj.title

    # def buttons(self, order):
    #     return format_html(
    #         '<div class="btn-group dropdown">'
    #         '<a href="{}" class="btn btn-sm btn-default btn-raised" target="_blank">{}<div class="ripple-container"></div></a>'
    #         '<button class="btn btn-sm btn-info btn-raised dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>'
    #         '<ul class="dropdown-menu" role="menu">'
    #         '<li><a href="{}">Одобрить</a></li>'
    #         '<li><a href="{}" target="_blank">Посмотреть профиль</a></li>'
    #         '<li class="divider"></li>'
    #         '<li><a href="{}">Отказать</a></li>'
    #         '</ul>'
    #         '</div><br>',
    #         reverse('profile', args=[order.performer]),
    #         order.performer.profile.get_full_name(),
    #         reverse('order_request_assign', args=[
    #                 order.order.id, order.performer.id]),
    #         reverse('profile', args=[order.performer]),
    #         reverse('order_request_delete', args=[
    #                 order.order.id, order.performer.id]),
    #     )

    # def get_performers(self, obj):
    #     orderRequests = OrderTableItemRequest.objects.filter(order=obj)
    #     html = '<div class="parent">'
    #     html += "".join(self.buttons(order) for order in orderRequests)
    #     html += '</div>'
    #     return html

    # get_performers.short_description = 'Исполнители'
    # get_performers.allow_tags = True


# admin.site.register(OrderTableItem, OrderTableAdmin)
admin.site.register(OrderTableItemCategory)
