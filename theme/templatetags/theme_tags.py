from __future__ import unicode_literals
from future.builtins import str
from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.utils import six
from django.conf import settings
from mezzanine import template
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import stringfilter
from django.contrib.auth.models import User
from theme.models import RulesPage
from cartridge.shop.models import Category
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


@register.filter
def rub_currency(value):
    """
    Format a value as a RUB currency
    """
    rub = '%s <span><i class="fa fa-rub" aria-hidden="true"></i></span>' % value
    return mark_safe(rub)


@register.assignment_tag
def to_stars(value, max_value, scale):
    return round((value / max_value) * scale, 2)


@register.simple_tag
def page_rules_menu():
    return RulesPage.objects.all()


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
        return "Не указан"
    return value

#


@register.filter(is_safe=True, needs_autoescape=True)
def theme_parent_list(value, autoescape=True):
    if autoescape:
        escaper = conditional_escape
    else:
        def escaper(x): return x

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


@register.simple_tag
def active(request, pattern):
    import re
    if re.search(pattern, request.path):
        return 'active'
    return ''


@register.filter(is_safe=False)
@stringfilter
def rupluralize(value, args):
    try:
        one, two, many = args.split(u',')
        value = str(value)[-2:]  # 314 -> 14
        if (21 > int(value) > 4):
            return "%s %s" % (value, many)

        if value.endswith('1'):
            return "%s %s" % (value, one)
        elif value.endswith(('2', '3', '4')):
            return "%s %s" % (value, two)
        else:
            return "%s %s" % (value, many)

    except (ValueError, TypeError):
        return ''


@register.assignment_tag
def get_shop_items(obj, shop_id=None):
    return obj.get_shop_items(int(shop_id))


@register.assignment_tag
def get_shop_data(obj, shop_id=None):
    return obj.get_shop_data(int(shop_id))


@register.filter
@stringfilter
def add_spaces(value):
    values = value.split(',')
    return ", ".join(values)


# @register.filter
# def get_class_name(value):
#     return value.__class__.__name__


@register.inclusion_tag("includes/search_form.html", takes_context=True)
def search_form(context):
    """
    Includes the search form with a list of models to use as choices
    for filtering the search by. Models should be a string with models
    in the format ``app_label.model_name`` separated by spaces. The
    string ``all`` can also be used, in which case the models defined
    by the ``SEARCH_MODEL_CHOICES`` setting will be used.
    """
    template_vars = {
        "request": context["request"],
    }
    search_model_names = list(settings.SEARCH_MODEL_CHOICES)
    search_model_choices = []
    selected_models = context['request'].GET.getlist('search_type')
    for model_name in search_model_names:
        try:
            model = apps.get_model(*model_name.split(".", 1))
        except LookupError:
            pass
        else:
            verbose_name = model._meta.verbose_name_plural.capitalize()
            checked = True if model_name in selected_models else False
            search_model_choices.append(
                (verbose_name, model_name, checked))

    template_vars["search_model_choices"] = search_model_choices
    category_options = Category.objects.only(
        'id', 'title').filter(
        parent__slug='catalog'
    )
    template_vars["category_options"] = ({'id': str(ct.id), 'title': ct.title} for ct in category_options)
    return template_vars
