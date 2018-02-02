from __future__ import unicode_literals

from django.template.defaultfilters import slugify
from django.http import HttpResponseRedirect

from mezzanine.conf import settings
from mezzanine.pages.page_processors import processor_for
from mezzanine.utils.views import paginate

from cartridge.shop.models import Category, Product
from mezzanine.pages.models import Page

from theme.utils import validate_filter


@processor_for(Category, exact_page=True)
def category_processor(request, page):
    """
    Add paging/sorting to the products for the category.
    """
    settings.clear_cache()
    min_price = validate_filter(request.GET.get("min_price"))
    max_price = validate_filter(request.GET.get("max_price"))

    region = validate_filter(request.GET.get("region"))
    discount = validate_filter(request.GET.get("discount"))
    pre_order = validate_filter(request.GET.get("pre_order"))

    express_point = validate_filter(request.GET.get("express_point"))
    express_city = validate_filter(request.GET.get("express_city"))
    express_country = validate_filter(request.GET.get("express_country"))
    express_world = validate_filter(request.GET.get("express_world"))
    express_mail = validate_filter(request.GET.get("express_mail"))
    express_personal = validate_filter(request.GET.get("express_personal"))

    payment_personal = validate_filter(request.GET.get("payment_personal"))
    payment_bank_transfer = validate_filter(request.GET.get("payment_bank_transfer"))
    payment_card_transfer = validate_filter(request.GET.get("payment_card_transfer"))

    products = Product.objects.filter(status=2).filter(
        page.category.filters()).distinct().prefetch_related('images')
    if min_price:
        products = products.filter(unit_price__gte=min_price)
    if max_price:
        products = products.filter(unit_price__lte=max_price)
    if region:
        products = products.filter(user__profile__region=region)
    if discount:
        products = products.exclude(sale_id=None)
    if pre_order:
        products = products.filter(pre_order=pre_order)
    if express_point:
        products = products.filter(user__shop__express_point=express_point)
    if express_city:
        products = products.filter(user__shop__express_city=express_city)
    if express_country:
        products = products.filter(user__shop__express_country=express_country)
    if express_world:
        products = products.filter(user__shop__express_world=express_world)
    if express_mail:
        products = products.filter(user__shop__express_mail=express_mail)
    if express_personal:
        products = products.filter(user__shop__express_personal=express_personal)

    if payment_personal:
        products = products.filter(user__shop__payment_personal=payment_personal)
    if payment_bank_transfer:
        products = products.filter(user__shop__payment_bank_transfer=payment_bank_transfer)
    if payment_card_transfer:
        products = products.filter(user__shop__payment_card_transfer=payment_card_transfer)

    sort_options = [(slugify(option[0]), option[1])
                    for option in settings.SHOP_PRODUCT_SORT_OPTIONS]
    sort_by = request.GET.get(
        "sort", sort_options[0][1] if sort_options else '-date_added')
    products = paginate(products.order_by(sort_by),
                        request.GET.get("page", 1),
                        settings.SHOP_PER_PAGE_CATEGORY,
                        settings.MAX_PAGING_LINKS)
    products.sort_by = sort_by
    sub_categories = page.category.children.published()
    child_categories = Category.objects.published(
        for_user=request.user).filter(id__in=sub_categories)
    true_sub_categories = Category.objects.published(
        for_user=request.user).filter(parent_id__in=child_categories)
    no_child = False
    if not true_sub_categories:
        true_sub_categories = child_categories
        no_child = True

    return {"true_products": products,
            "sub_categories": child_categories,
            "main_filters": settings.SHOP_PRODUCT_FILTERS,
            "delivery_filters": settings.SHOP_DELIVERY_FILTERS,
            "payment_filters": settings.SHOP_PAYMENT_FILTERS,
            "sub_child_categories": child_categories,
            'no_child': no_child}
