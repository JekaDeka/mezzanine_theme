from __future__ import unicode_literals
from future.builtins import str
from datetime import datetime
from decimal import Decimal

from collections import defaultdict
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model
from django.contrib.admin import site
from django.apps import apps
from django.utils.text import capfirst
from django.utils.html import conditional_escape
from django.utils.safestring import SafeData, mark_for_escaping, mark_safe
from django.utils.encoding import force_text, iri_to_uri
from django.core.urlresolvers import reverse, resolve, NoReverseMatch
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils import six
from django.conf import settings
from django import template
from mezzanine import template
from django import VERSION as DJANGO_VERSION
from django.template import Context, TemplateSyntaxError, Variable
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from mezzanine.utils.urls import home_slug
from django.template.defaultfilters import stringfilter
from django.db.models import Count, Q
from django.contrib.auth.models import User
from mezzanine.blog.models import BlogPost, BlogCategory
from theme.models import Slider, SliderItem, RulesPage
from cartridge.shop.models import Category, Product, ProductImage
from mezzanine.pages.models import Page
from mezzanine.generic.models import Keyword
from mezzanine.generic.forms import RatingForm
import os


# Depending on you python version, reduce has been moved to functools
try:
    from functools import reduce
    from urllib.parse import quote, unquote
except ImportError:
    from urllib import quote, unquote

User = get_user_model()

register = template.Library()


@register.filter("smart_truncate_chars")
def smart_truncate_chars(value, max_length):
    if len(value) > max_length:
        # Limits the number of characters in value tp max_length (blunt cut)
        truncd_val = value[:max_length]
        # Check if the next upcoming character after the limit is not a space,
        # in which case it might be a word continuing
        if value[max_length] != " ":
            # rfind will return the last index where matching the searched character, in this case we are looking for the last space
            # Then we only return the number of character up to that last space
            truncd_val = truncd_val[:truncd_val.rfind(" ")]
        return truncd_val + "..."
    return value


@register.as_tag
def get_slideshow(*args):
    try:
        items = SliderItem.objects.all().select_related('href')
    except Exception as e:
        return None
    if items:
        return list(items)
    return None


# @register.as_tag
# def blog_menu_categories(*args):
#     """
#     Put a list of categories for blog posts into the template context.
#     """
#     # posts = BlogPost.objects.published()
#     # categories = BlogCategory.objects.filter(blogposts__in=posts)
#     categories = BlogCategory.objects.all()
#     return list(categories.annotate(post_count=Count("blogposts")))


def moneyfmt(value, places=0, curr='', sep=',', dp='.',
             pos='', neg='-', trailneg=''):
    """Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<0.02>'

    """
    q = Decimal(10) ** -places      # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = list(map(str, digits))
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    if places:
        build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))


@register.filter
def rub_currency(value):
    """
    Format a value as a RUB currency
    """
    if value is None:
        return "Цена по запросу"
    elif value == 0:
        return "Бесплатно"
    return str(value) + " руб"


@register.as_tag
def blog_recent_posts(limit=5, tag=None, username=None, category=None):
    """
    Put a list of recently published blog posts into the template
    context. A tag title or slug, category title or slug or author's
    username can also be specified to filter the recent posts returned.

    Usage::

        {% blog_recent_posts 5 as recent_posts %}
        {% blog_recent_posts limit=5 tag="django" as recent_posts %}
        {% blog_recent_posts limit=5 category="python" as recent_posts %}
        {% blog_recent_posts 5 username=admin as recent_posts %}

    """
    blog_posts = BlogPost.objects.exclude(
        status=1).select_related("user")
    title_or_slug = lambda s: Q(title=s) | Q(slug=s)
    if tag is not None:
        try:
            tag = Keyword.objects.get(title_or_slug(tag))
            blog_posts = blog_posts.filter(keywords__keyword=tag)
        except Keyword.DoesNotExist:
            return []
    if category is not None:
        try:
            category = BlogCategory.objects.get(title_or_slug(category))
            blog_posts = blog_posts.filter(categories=category)
        except BlogCategory.DoesNotExist:
            return []
    if username is not None:
        try:
            author = User.objects.get(username=username)
            blog_posts = blog_posts.filter(user=author)
        except User.DoesNotExist:
            return []
    return list(blog_posts[:limit])


@register.as_tag
def shop_recent_products(limit=5):

    published_products = Product.objects.exclude(
        status=1).order_by('-created')
    return list(published_products[:limit])


@register.simple_tag
def page_rules_menu():
    return RulesPage.objects.all()

# @register.render_tag
# def page_breadcrumb_menu(context, token):
#     """
#     Return a list of child pages for the given parent, storing all
#     pages in a dict in the context when first called using parents as keys
#     for retrieval on subsequent recursive calls from the menu template.
#     """
#     # First arg could be the menu template file name, or the parent page.
#     # Also allow for both to be used.
#     template_name = None
#     parent_page = None
#     parts = token.split_contents()[1:]
#     for part in parts:
#         part = Variable(part).resolve(context)
#         if isinstance(part, str):
#             template_name = part
#         elif isinstance(part, Page):
#             parent_page = part
#     if template_name is None:
#         try:
#             template_name = context["menu_template_name"]
#         except KeyError:
#             error = "No template found for page_menu in: %s" % parts
#             raise TemplateSyntaxError(error)
#     context["menu_template_name"] = template_name
#     if "bread_menu_pages" not in context:
#         try:
#             user = context["request"].user
#             slug = context["request"].path
#         except KeyError:
#             user = None
#             slug = ""
#         num_children = lambda id: lambda: len(context["bread_menu_pages"][id])
#         has_children = lambda id: lambda: num_children(id)() > 0
#         rel = [m.__name__.lower()
#                for m in Page.get_content_models()
#                if not m._meta.proxy]
#         published = Page.objects.published(for_user=user).select_related(*rel)
#         # Store the current page being viewed in the context. Used
#         # for comparisons in page.set_menu_helpers.
#         if "page" not in context:
#             try:
#                 context.dicts[0]["_current_page"] = published.filter(
#                     content_model='category').get(slug=slug)
#             except Page.DoesNotExist:
#                 context.dicts[0]["_current_page"] = None
#         elif slug:
#             context.dicts[0]["_current_page"] = context["page"]
#         # Some homepage related context flags. on_home is just a helper
#         # indicated we're on the homepage. has_home indicates an actual
#         # page object exists for the homepage, which can be used to
#         # determine whether or not to show a hard-coded homepage link
#         # in the page menu.
#         home = home_slug()
#         context.dicts[0]["on_home"] = slug == home
#         context.dicts[0]["has_home"] = False
#         # Maintain a dict of page IDs -> parent IDs for fast
#         # lookup in setting page.is_current_or_ascendant in
#         # page.set_menu_helpers.
#         context.dicts[0]["_parent_page_ids"] = {}
#         pages = defaultdict(list)
#         for page in published.order_by("_order"):
#             page.set_helpers(context)
#             context["_parent_page_ids"][page.id] = page.parent_id
#             setattr(page, "num_children", num_children(page.id))
#             setattr(page, "has_children", has_children(page.id))
#             pages[page.parent_id].append(page)
#             if page.slug == home:
#                 context.dicts[0]["has_home"] = True
#         # Include bread_menu_pages in all contexts, not only in the
#         # block being rendered.
#         context.dicts[0]["bread_menu_pages"] = pages
#     # ``branch_level`` must be stored against each page so that the
#     # calculation of it is correctly applied. This looks weird but if we do
#     # the ``branch_level`` as a separate arg to the template tag with the
#     # addition performed on it, the addition occurs each time the template
#     # tag is called rather than once per level.
#     context["branch_level"] = 0
#     parent_page_id = None
#     if parent_page is not None:
#         context["branch_level"] = getattr(parent_page, "branch_level", 0) + 1
#         parent_page_id = parent_page.id

#     # Build the ``page_branch`` template variable, which is the list of
#     # pages for the current parent. Here we also assign the attributes
#     # to the page object that determines whether it belongs in the
#     # current menu template being rendered.
#     context["page_branch"] = context[
#         "bread_menu_pages"].get(parent_page_id, [])
#     context["page_branch_in_menu"] = False
#     for page in context["page_branch"]:
#         page.in_menu = page.in_menu_template(template_name)
#         page.num_children_in_menu = 0
#         if page.in_menu:
#             context["page_branch_in_menu"] = True
#         for child in context["bread_menu_pages"].get(page.id, []):
#             if child.in_menu_template(template_name):
#                 page.num_children_in_menu += 1
#         page.has_children_in_menu = page.num_children_in_menu > 0
#         page.branch_level = context["branch_level"]
#         page.parent = parent_page
#         context["parent_page"] = page.parent

#         # Prior to pages having the ``in_menus`` field, pages had two
#         # boolean fields ``in_navigation`` and ``in_footer`` for
#         # controlling menu inclusion. Attributes and variables
#         # simulating these are maintained here for backwards
#         # compatibility in templates, but will be removed eventually.
#         page.in_navigation = page.in_menu
#         page.in_footer = not (not page.in_menu and "footer" in template_name)
#         if page.in_navigation:
#             context["page_branch_in_navigation"] = True
#         if page.in_footer:
#             context["page_branch_in_footer"] = True

#     t = get_template(template_name)
#     return t.render(Context(context))


@register.filter(name='get_product_category')
def get_product_category(product):
    try:
        prod = Product.objects.get(title=product)
        categories = prod.category_set.all()
        titles = []
        for cat in categories:
            titles.append(cat.title)
    except:
        return None

    return ", ".join(str(x) for x in titles)


# @register.filter(name='get_categories')
# def get_categories(categories):
#     return categories


@register.filter(name='get_variation_list')
def get_variation_list(variations):
    sizes = set()
    colors = set()
    foot = set()
    for variation in variations:
        sizes.add(variation.option1)
        colors.add(variation.option2)
        foot.add(variation.option3)
    d = {'Размер': sizes, 'Цвет': colors}
    return d


@register.simple_tag(takes_context=True)
def get_user_by_url(context):
    try:
        request = context["request"]
        url = request.path.split('/')[-2]
    except:
        return None
    return url


MAX_LENGTH_BOOTSTRAP_COLUMN = 12


def css_classes_for_field(field, custom_classes):
    orig_class = field.field.widget.attrs.get('class', '')
    required = 'required' if field.field.required else ''
    classes = field.css_classes(
        ' '.join([orig_class, custom_classes, required]))
    return classes


@register.filter()
def get_label(field, custom_classes=''):
    classes = css_classes_for_field(field, custom_classes)
    return field.label_tag(attrs={'class': classes}, label_suffix='')


@register.filter()
def add_class(field, custom_classes=''):
    classes = css_classes_for_field(field, custom_classes)
    try:
        # For widgets like SelectMultiple, checkboxselectmultiple
        field.field.widget.widget.attrs.update({'class': classes})
    except:
        field.field.widget.attrs.update({'class': classes})
    return field


@register.filter()
def widget_type(field):
    if isinstance(field, dict):
        return 'adminreadonlyfield'
    try:
        # For widgets like SelectMultiple, checkboxselectmultiple
        widget_type = field.field.widget.widget.__class__.__name__.lower()
    except:
        widget_type = field.field.widget.__class__.__name__.lower()
    return widget_type


@register.filter()
def placeholder(field, placeholder=''):
    field.field.widget.attrs.update({'placeholder': placeholder})
    return field


def sidebar_menu_setting():
    return getattr(settings, 'BOOTSTRAP_ADMIN_SIDEBAR_MENU', False)


@register.assignment_tag
def display_sidebar_menu(has_filters=False):
    if has_filters:
        # Always display the menu in change_list.html
        return True
    return sidebar_menu_setting()


@register.assignment_tag
def jquery_vendor_path():
    if DJANGO_VERSION < (1, 9):
        return 'admin/js/jquery.js'
    return 'admin/js/vendor/jquery/jquery.js'


@register.assignment_tag
def datetime_widget_css_path():
    if DJANGO_VERSION < (1, 9):
        return ''
    return 'admin/css/datetime_widget.css'


@register.inclusion_tag('bootstrap_admin/sidebar_menu.html',
                        takes_context=True)
def render_menu_app_list(context):
    show_global_menu = sidebar_menu_setting()
    if not show_global_menu:
        return {'app_list': ''}

    if DJANGO_VERSION < (1, 8):
        dependencie = 'django.core.context_processors.request'
        processors = settings.TEMPLATE_CONTEXT_PROCESSORS
        dependency_str = 'settings.TEMPLATE_CONTEXT_PROCESSORS'
    else:
        dependencie = 'django.template.context_processors.request'
        implemented_engines = getattr(settings, 'BOOTSTRAP_ADMIN_ENGINES',
                                      ['django.template.backends.django.DjangoTemplates'])
        dependency_str = "the 'context_processors' 'OPTION' of one of the " + \
            "following engines: %s" % implemented_engines
        filtered_engines = [engine for engine in settings.TEMPLATES
                            if engine['BACKEND'] in implemented_engines]
        if len(filtered_engines) == 0:
            raise ImproperlyConfigured(
                "bootstrap_admin: No compatible template engine found" +
                "bootstrap_admin requires one of the following engines: %s"
                % implemented_engines
            )
        processors = reduce(lambda x, y: x.extend(y), [
            engine.get('OPTIONS', {}).get('context_processors', [])
            for engine in filtered_engines])

    if dependencie not in processors:
        raise ImproperlyConfigured(
            "bootstrap_admin: in order to use the 'sidebar menu' requires" +
            " the '%s' to be added to %s"
            % (dependencie, dependency_str)
        )

    # Code adapted from django.contrib.admin.AdminSite
    app_dict = {}
    user = context.get('user')
    for model, model_admin in site._registry.items():
        app_label = model._meta.app_label
        has_module_perms = user.has_module_perms(app_label)

        if has_module_perms:
            perms = model_admin.get_model_perms(context.get('request'))

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True in perms.values():
                info = (app_label, model._meta.model_name)
                model_dict = {
                    'name': capfirst(model._meta.verbose_name_plural),
                    'object_name': model._meta.object_name,
                    'perms': perms,
                }
                if perms.get('change', False):
                    try:
                        model_dict['admin_url'] = reverse(
                            'admin:%s_%s_changelist' % info,
                            current_app=site.name
                        )
                    except NoReverseMatch:
                        pass
                if perms.get('add', False):
                    try:
                        model_dict['add_url'] = reverse(
                            'admin:%s_%s_add' % info,
                            current_app=site.name
                        )
                    except NoReverseMatch:
                        pass
                if app_label in app_dict:
                    app_dict[app_label]['models'].append(model_dict)
                else:
                    app_dict[app_label] = {
                        'name': apps.get_app_config(app_label).verbose_name,
                        'app_label': app_label,
                        'app_url': reverse(
                            'admin:app_list',
                            kwargs={'app_label': app_label},
                            current_app=site.name
                        ),
                        'has_module_perms': has_module_perms,
                        'models': [model_dict],
                    }

    # Sort the apps alphabetically.
    app_list = list(six.itervalues(app_dict))
    app_list.sort(key=lambda x: x['name'].lower())

    # Sort the models alphabetically within each sapp.
    for app in app_list:
        app['models'].sort(key=lambda x: x['name'])
    return {'app_list': app_list, 'current_url': context.get('request').path}


@register.filter()
def class_for_field_boxes(line):
    size_column = MAX_LENGTH_BOOTSTRAP_COLUMN // len(line.fields)
    return 'col-sm-{0}'.format(size_column or 1)  # if '0' replace with 1


@register.filter()
def class_for_single_line():
    # size_column = MAX_LENGTH_BOOTSTRAP_COLUMN // len(line.fields)
    return 'col-sm-{0}'.format(6)


@register.filter("generate_id")
def generate_id(value):
    value = value.replace(" ", "")
    return value


@register.filter("hard_trim")
def hard_trim(value):
    value = value.replace(" ", "")
    value = value.replace(",", "")
    return value


EXTENSIONS = {
    'Папка': [''],
    'Изображения': ['.jpg', '.jpeg', '.gif', '.png', '.bmp'],
}


def allowed_theme_list(separator=','):
    output = []

    for key in EXTENSIONS:
        if key != 'Folder':
            output += EXTENSIONS[key]

    return separator.join(output)
register.simple_tag(allowed_theme_list)


@register.filter
def not_none(value):
    if not value:
        return "не указан"
    return value


@register.assignment_tag
def get_fields(shop, starts_with):
    fields = []
    for f in shop._meta.fields:
        fname = f.name
        try:
            value = getattr(shop, fname)
        except AttributeError:
            value = None

        if fname.startswith(starts_with) and f.editable and (f.name not in ('id', 'express_other')):
            fields.append(
                {
                    'label': f.verbose_name,
                    'name': f.name,
                    'value': value,
                }
            )
    return fields


@register.filter
def grouped(l):
    for i in range(0, len(l), 2):
        yield l[i:i + 2]


@register.filter
def any_is_true(l):
    if any(el["value"] for el in l):
        return True
    return False


# @register.assignment_tag
# def get_shop_by_product(sku):
#     p = Product.objects.get(id=71)
#     return sku
    # try:

    #     print(p)
    #     shop = p.user.shop
    # except Exception as e:
    #     shop = None
    # return shop
    # @register.filter
    # def get_shop_slug(user):
    #     if not user:
    #         return "/"
    #     shop = get_object_or_404(UserShop, user=user)
    #     return shop.slug

    # @register.filter
    # def get_shop_name(user):
    #     if not user:
    #         return "/"
    #     shop = get_object_or_404(UserShop, user=user)
    #     return shop.shopname

    # @register.assignment_tag
    # def get_shop(user):
    #     try:
    #         shop = UserShop.objects.get(user=user)
    #     except Exception as e:
    #         return None
    #     return shop

    # @register.assignment_tag
    # def get_shop_products(user):
    #     try:
    #         # products = get_list_or_404(Product, user=user)
    #         products = Product.objects.filter(user=user)
    #     except Exception as e:
    #         return None
    #     return products


@register.as_tag
def get_user_blog_posts(user):
    try:
        posts = BlogPost.objects.filter(user=user)[:4]
    except Exception as e:
        raise
    return posts


@register.simple_tag(takes_context=True)
def get_device_width(context):
    request = context['request']
    width = 194
    if request.device.is_medium:
        # width = 767
        width = 314
    elif request.device.is_large:
        # width = 990
        width = 248
    elif request.device.is_xlarge:
        # width = 1389
        width = 334
    elif request.device.is_xxlarge:
        # width = 1389
        width = 454
    return width


# @register.assignment_tag
# def get_product_images(product):
#     # reducing image count to 2 because of slider which contain only two
#     return ProductImage.objects.filter(product=product)[:2]


@register.filter(is_safe=True, needs_autoescape=True)
def theme_parent_list(value, autoescape=True):
    if autoescape:
        escaper = conditional_escape
    else:
        escaper = lambda x: x

    def walk_items(item_list):
        item_iterator = iter(item_list)
        try:
            item = next(item_iterator)
            while True:
                try:
                    next_item = next(item_iterator)
                except StopIteration:
                    yield item, None
                    break
                if not isinstance(next_item, six.string_types):
                    try:
                        iter(next_item)
                    except TypeError:
                        pass
                    else:
                        yield item, next_item
                        item = next(item_iterator)
                        continue
                yield item, None
                item = next_item
        except StopIteration:
            pass

    def list_formatter(item_list, tabs=1):
        indent = '\t' * tabs
        output = []
        for item, children in walk_items(item_list):
            output.append('%s<li><i class="fa fa-li fa-trash-o"></i>%s</li>' % (
                indent, escaper(force_text(item))))
        return '\n'.join(output)

    return mark_safe(list_formatter(value))


# @register.filter("not_on_vacation")
# def not_on_vacation(object_list):
#     return object_list.filter(user__shop__on_vacation=False)


@register.simple_tag
def active(request, pattern):
    import re
    if re.search(pattern, request.path):
        return 'active'
    return ''


@register.inclusion_tag("generic/includes/rating.html", takes_context=True)
def rating_for(context, obj):
    """
    Provides a generic context variable name for the object that
    ratings are being rendered for, and the rating form.
    """
    request = context['request']
    try:
        context['user_raiting'] = request.user.ratings.get(
            object_pk=obj.pk, content_type=ContentType.objects.get_for_model(obj))
    except:
        context['user_raiting'] = None
    else:
        pass

    context["rating_object"] = context["rating_obj"] = obj
    context["rating_form"] = RatingForm(context["request"], obj)
    ratings = context["request"].COOKIES.get("mezzanine-rating", "")
    rating_string = "%s.%s" % (obj._meta, obj.pk)
    context["rated"] = (rating_string in ratings)
    rating_name = obj.get_ratingfield_name()
    for f in ("average", "count", "sum"):
        context["rating_" + f] = getattr(obj, "%s_%s" % (rating_name, f))

    context["rating_average"] /= 2
    return context

@register.filter(is_safe = False)
@stringfilter
def rupluralize(value, arg):
    bits = arg.split(u',')
    quantity = value
    value = int(value)
    try:
        value = str( 0 if not value or value <= 0 else value )[-1:] # patched version
        return str(quantity) + ' ' + bits[ 0 if value=='1' else (1 if value in '234' else 2) ]
    except:
        pass
    return value


@register.assignment_tag
def split(value=None):
    return value.split(',')

@register.assignment_tag
def get_shop_data(obj, shop_id=None):
    return obj.get_shop_data(int(shop_id))

@register.assignment_tag
def get_shop_items(obj, shop_id=None):
    return obj.get_shop_items(int(shop_id))
# @register.filter
# def get_item_quantity(obj, arg):
#     return obj.total_quantity_for_shop(arg)
#
# @register.filter
# def get_item_total_price(obj, arg):
#     return obj.total_price_for_shop(arg)
