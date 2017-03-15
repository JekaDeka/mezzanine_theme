from __future__ import unicode_literals

from django.template.defaultfilters import slugify
from django.http import HttpResponseRedirect

from mezzanine.conf import settings
from mezzanine.pages.page_processors import processor_for
from mezzanine.utils.views import paginate

from cartridge.shop.models import Category, Product
from mezzanine.pages.models import Page


@processor_for(Category, exact_page=True)
def category_processor(request, page):
    """
    Add paging/sorting to the products for the category.
    """
    settings.clear_cache()
    pre_order = request.GET.get("pre_order")
    products = Product.objects.published(for_user=request.user
                                ).filter(page.category.filters()).distinct()
    if pre_order:
        products = products.filter(pre_order=pre_order)
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
    child_categories = Category.objects.published(for_user=request.user).filter(id__in=sub_categories)
    true_sub_categories = Category.objects.published(for_user=request.user).filter(parent_id__in=child_categories)
    no_child = False
    if not true_sub_categories:
        true_sub_categories = child_categories
        no_child = True

    return {"true_products": products, 
            "sub_categories": child_categories, 
            # "sub_child_categories": true_sub_categories,
            "sub_child_categories": child_categories,
            'no_child': no_child}