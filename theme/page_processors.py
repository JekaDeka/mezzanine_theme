from __future__ import unicode_literals

from django.template.defaultfilters import slugify
from django.http import HttpResponseRedirect

from mezzanine.conf import settings
from mezzanine.pages.page_processors import processor_for
from mezzanine.utils.views import paginate

from cartridge.shop.models import Category
from mezzanine.pages.models import Page
from shops.models import ShopProduct
from shops.forms import FilterForm
from theme.utils import validate_filter


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


@processor_for(Category, exact_page=True)
def category_processor(request, page):
    """
    Add paging/sorting to the products for the category.
    """
    settings.clear_cache()
    # min_price = validate_filter(request.GET.get("min_price"))
    # max_price = validate_filter(request.GET.get("max_price"))
    #
    # region = validate_filter(request.GET.get("region"))
    # discount = validate_filter(request.GET.get("discount"))
    # pre_order = validate_filter(request.GET.get("pre_order"))
    #
    # express_point = validate_filter(request.GET.get("express_point"))
    # express_city = validate_filter(request.GET.get("express_city"))
    # express_country = validate_filter(request.GET.get("express_country"))
    # express_world = validate_filter(request.GET.get("express_world"))
    # express_mail = validate_filter(request.GET.get("express_mail"))
    # express_personal = validate_filter(request.GET.get("express_personal"))
    #
    # payment_personal = validate_filter(request.GET.get("payment_personal"))
    # payment_bank_transfer = validate_filter(request.GET.get("payment_bank_transfer"))
    # payment_card_transfer = validate_filter(request.GET.get("payment_card_transfer"))
    products = ShopProduct.objects.filter(available=True, categories=page.category).only(
        'id',
        'slug',
        'title',
        'price',
        'condition',
        'shop__shopname',
        'shop__slug'
    ).prefetch_related('images').select_related('shop')
    # if min_price:
    #     products = products.filter(unit_price__gte=min_price)
    # if max_price:
    #     products = products.filter(unit_price__lte=max_price)
    # if region:
    #     products = products.filter(user__profile__region=region)
    # if discount:
    #     products = products.exclude(sale_id=None)
    # if pre_order:
    #     products = products.filter(pre_order=pre_order)
    # if express_point:
    #     products = products.filter(user__shop__express_point=express_point)
    # if express_city:
    #     products = products.filter(user__shop__express_city=express_city)
    # if express_country:
    #     products = products.filter(user__shop__express_country=express_country)
    # if express_world:
    #     products = products.filter(user__shop__express_world=express_world)
    # if express_mail:
    #     products = products.filter(user__shop__express_mail=express_mail)
    # if express_personal:
    #     products = products.filter(user__shop__express_personal=express_personal)
    #
    # if payment_personal:
    #     products = products.filter(user__shop__payment_personal=payment_personal)
    # if payment_bank_transfer:
    #     products = products.filter(user__shop__payment_bank_transfer=payment_bank_transfer)
    # if payment_card_transfer:
    #     products = products.filter(user__shop__payment_card_transfer=payment_card_transfer)
    filter_form = FilterForm()
    filters = {}
    payments_options_id = []
    delivery_options_id = []
    conditions = []
    for key in request.GET:
        try:
            value = request.GET[key]
            filter_form.fields[key].initial = value
            if 'max_price' in key and RepresentsInt(value):
                filters['price__lte'] = value
            if 'min_price' in key and RepresentsInt(value):
                filters['price__gte'] = value
            if 'payment_type_' in key and value == 'on':
                payments_options_id.append(int((key.rpartition('_')[-1])))
            if 'delivery_type_' in key and value == 'on':
                delivery_options_id.append(int((key.rpartition('_')[-1])))
            if 'condition_type_' in key and value == 'on':
                conditions.append(int((key.rpartition('_')[-1])))

        except KeyError:
            # Ignore unexpected parameters
            pass
    if payments_options_id:
        filters['shop__payment_options__id__in'] = payments_options_id
    if delivery_options_id:
        filters['shop__delivery_options__id__in'] = delivery_options_id
    if conditions:
        filters['condition__in'] = conditions

    products = products.filter(**filters)
    sort_options = None
    sort_by = request.GET.get(
        "sort", sort_options[0][1] if sort_options else '-date_added')

    products = paginate(products.order_by(sort_by),
                        request.GET.get("page", 1),
                        settings.SHOP_PER_PAGE_CATEGORY,
                        settings.MAX_PAGING_LINKS)
    products.sort_by = sort_by

    sub_categories = Category.objects.filter(parent=page).select_related('parent')
    # child_categories = Category.objects.published(
    #     for_user=request.user).filter(id__in=sub_categories).select_related('parent')
    return {"true_products": products,
            "sub_categories": sub_categories,
            "filter_form": filter_form,
            # "main_filters": settings.SHOP_PRODUCT_FILTERS,
            # "delivery_filters": settings.SHOP_DELIVERY_FILTERS,
            # "payment_filters": settings.SHOP_PAYMENT_FILTERS, 0
            }
