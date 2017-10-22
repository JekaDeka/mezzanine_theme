from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.forms.fields import Field

from datetime import date
from copy import copy

from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.forms.utils import flatatt, to_current_timezone
from django.forms.models import inlineformset_factory
from django.utils.datastructures import MultiValueDict


from mezzanine.conf import settings
from mezzanine.accounts.forms import ProfileForm
from mezzanine.utils.static import static_lazy as static
from mezzanine.blog.models import BlogPost
from mezzanine.core.models import CONTENT_STATUS_DRAFT

from cartridge.shop import checkout
from cartridge.shop.models import Cart, CartItem, Order, DiscountCode, Category, ProductOption, ProductVariation
from cartridge.shop.forms import FormsetForm, DiscountForm, AddProductForm, OrderForm
from cartridge.shop.utils import (make_choices, set_locale, set_shipping,
                                  clear_session)
from theme.models import UserShop, UserProfile, OrderItem, Region, City

# from django_countries.widgets import CountrySelectWidget


setattr(Field, 'is_checkbox', lambda self: isinstance(
    self.widget, forms.CheckboxInput))

# These fields need to be in the form, hidden, with default values,
# since it posts to the blog post admin, which includes these fields
# and will use empty values instead of the model defaults, without
# these specified.
hidden_field_defaults = ("status", "gen_description", "allow_comments")
User = get_user_model()


class ContactForm(forms.Form):
    contact_email = forms.EmailField(required=True)


class OrderMessageForm(forms.Form):
    message = forms.CharField(
        required=False,
        label="Ваше сообщение",
        widget=forms.Textarea
    )


class MessageForm(forms.Form):
    first_name = forms.CharField(
        required=True,
        label="Ваше имя",
    )
    email = forms.EmailField(required=True, label="Ваша почта")
    message = forms.CharField(
        required=False,
        label="Ваше сообщение",
        widget=forms.Textarea
    )


class UserProfileForm(forms.ModelForm):

    class Media:
        js = ('javascript/mymarkup.js',)

    class Meta:
        model = UserProfile
        exclude = ('user',)
        # fields = ("phone",)
        widgets = {
            'first_name': forms.TextInput(attrs={'class': '', 'placeholder': 'Имя', }),
            'last_name': forms.TextInput(attrs={'class': '', 'placeholder': 'Фамилия', }),
            'phone': forms.TextInput(attrs={'class': 'mask', 'placeholder': '+7 (999) 999-9999'}),
            'image': forms.FileInput(attrs={'id': 'file-2', 'class': 'inputfile inputfile-2'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)


class ShopForm(forms.ModelForm):
    error_css_class = 'class-error'
    required_css_class = 'class-required'

    class Meta:
        model = UserShop
        fields = ("background", "image", "shopname",  # "phone",
                  # "country", "region", "city",
                  "bio", "rules",
                  "express_point", "express_point_price",
                  "express_city", "express_city_price",
                  "express_country", "express_country_price",
                  "express_world", "express_world_price",
                  "express_mail", "express_mail_price",
                  "express_personal", "express_personal_price", "express_other",
                  "payment_personal", "payment_bank_transfer", "payment_card_transfer", "payment_other")
        widgets = {
            'shopname': forms.TextInput(attrs={'class': 'form-control'}),
            'background': forms.FileInput(attrs={'id': 'file-1', 'class': 'inputfile inputfile-1'}),
            'image': forms.FileInput(attrs={'id': 'file-5', 'class': 'inputfile inputfile-4'}),
            # 'phone': forms.TextInput(attrs={'class': 'mask', 'placeholder': '+7 (999) 999-9999'}),
            'express_point_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена', 'readonly': 'readonly'}),
            'express_city_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена', 'readonly': 'readonly'}),
            'express_country_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена', 'readonly': 'readonly'}),
            'express_world_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена', 'readonly': 'readonly'}),
            'express_mail_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена', 'readonly': 'readonly'}),
            'express_personal_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена', 'readonly': 'readonly'}),
            'express_other': forms.Textarea(attrs={'placeholder': 'Дополнительная информация о доставке', 'rows': '5'}),
            'payment_other': forms.Textarea(attrs={'placeholder': 'Дополнительная информация об оплате', 'rows': '5'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Описание магазина'}),
            'rules': forms.Textarea(attrs={'placeholder': 'Правила магазина'}),
        }

    def clean_file(self):
        file = self.cleaned_data['file']
        try:
            if file:
                file_type = file.content_type.split('/')[0]
                if len(file.name.split('.')) == 1:
                    raise forms.ValidationError(
                        _('File type is not supported'))

                if file_type in settings.TASK_UPLOAD_FILE_TYPES:
                    if file._size > settings.TASK_UPLOAD_FILE_MAX_SIZE:
                        raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (
                            filesizeformat(settings.TASK_UPLOAD_FILE_MAX_SIZE), filesizeformat(file._size)))
                else:
                    raise forms.ValidationError(
                        _('File type is not supported'))
        except:
            pass

        return file
    # def __init__(self, *args, **kwargs):
    #     super(ShopForm, self).__init__(*args, **kwargs)
    #     # adding css classes to widgets without define the fields:
    #     for field in self.fields:
    #         self.fields[field].widget.attrs['class'] = 'some-class other-class'

    # def as_div(self):
    #     return self._html_output(
    #         normal_row=u'<div%(html_class_attr)s>%(label)s %(field)s %(help_text)s %(errors)s</div>',
    #         error_row=u'<div class="error">%s</div>',
    #         row_ender='</div>',
    #         help_text_html=u'<div class="hefp-text">%s</div>',
    #         errors_on_separate_row=False)


# class SmallProfileForm(forms.ModelForm):

#     class Meta:
#         model = UserProfile
#         fields = ("firstname", "lastname", "phone")
#         widgets = {
#             'firstname': forms.TextInput(attrs={'class': 'form-control'}),
#             'lastname': forms.TextInput(attrs={'class': 'form-control'}),
#             'phone': forms.TextInput(attrs={'class': 'form-control mask', 'data-inputmask': "'mask':'9 (999) 999-9999'"}),
#         }


class ThemeProfileForm(ProfileForm):
    """docstring for ThemeProfileForm"""
    agree = forms.BooleanField(
        required=True, label=mark_safe('Регистрируясь на сайте, вы принимаете <a href="/rules/" target="_blank">Правила сайта</a> и даёте согласие на обработку персональных данных.'))

    class Meta:
        model = User
        fields = ("email",)


class DataGroupSelect(forms.widgets.SelectMultiple):
    allow_multiple_selected = True

    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        final_attrs = self.build_attrs(attrs, name=name)
        output = [format_html(
            '<select multiple="multiple" style="display: none;" "{}>', flatatt(final_attrs))]
        options = self.render_options(choices, value)
        if options:
            output.append(options)
        output.append('</select>')
        output.append(
            '<script type="text/javascript" src="/static/admin/js/select_append.js"></script>')
        return mark_safe('\n'.join(output))

    def value_from_datadict(self, data, files, name):
        if isinstance(data, MultiValueDict):
            return data.getlist(name)
        return data.get(name)

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        # get class attrs (customize class_attr by yourself)
        class_attr = 'sub'
        return format_html('<option value="{0}"{1} class="{3}">{2}</option>',
                           option_value,
                           selected_html,
                           force_text(option_label),
                           class_attr)


class DataGroupModelChoiceField(forms.ModelMultipleChoiceField):

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = DataGroupSelect
        super(DataGroupModelChoiceField, self).__init__(*args, **kwargs)


class SelectForm(forms.ModelForm):
    # def get_tree_data(node, data):
    #     level = 0

    #     def allChildren(self, l=None, level=0):
    #         if(l == None):
    #             l = list()
    #         if level != 0:
    #             l.append(tuple((self.id, self.title)))
    #         level += 1
    #         for child in self.children.all():
    #             l = allChildren(child, l, level)
    #         return l
    #     allChildren(node, data)
    #     return data

    # data = list()
    # class Meta:
    #     widgets = {
    #         'unit_price': forms.NumberInput(attrs={'step': '1'}),
    #     }
    categories = DataGroupModelChoiceField(
        queryset=Category.objects.all().order_by('id'),
        label="Категории")

    # def __init__(self, *args, **kwargs):
    #     super(SelectForm, self).__init__(*args, **kwargs)


class OrderItemAdminForm(forms.ModelForm):

    class Meta:
        model = OrderItem
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(OrderItemAdminForm, self).__init__(*args, **kwargs)
        self.fields['ended'].widget.format = '%d/%m/%Y'
        self.fields['ended'].input_formats = ['%d/%m/%Y']


class OrderItemRequestActionForm(forms.Form):
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea,
    )
    send_email = forms.BooleanField(
        required=False,
    )

    @property
    def email_subject_template(self):
        return 'email/base.txt'

    @property
    def email_body_template(self):
        raise NotImplementedError()

    def form_action(self, order, user):
        raise NotImplementedError()

    def save(self, order, user):
        try:
            order, action = self.form_action(order, user)
        except errors.Error as e:
            error_message = str(e)
            self.add_error(None, error_message)
            raise
        if self.cleaned_data.get('send_email', False):
            send_email(
                to=[user.email],
                subject_template=self.email_subject_template,
                body_template=self.email_body_template,
                context={
                    "order": order,
                    "action": action,
                }
            )
        return order, action


# class NoQuantityAddProductForm(forms.Form):
#     """docstring for AddProductForm"""
#     sku = forms.CharField(required=False, widget=forms.HiddenInput())
#     quantity = forms.IntegerField(widget=forms.HiddenInput())
#     # shop = forms.IntegerField(widget=forms.HiddenInput())

#     def __init__(self, *args, **kwargs):
#         """
#         Handles adding a variation to the cart or wishlist.
#         When adding from the product page, the product is provided
#         from the view and a set of choice fields for all the
#         product options for this product's variations are added to
#         the form. When the form is validated, the selected options
#         are used to determine the chosen variation.
#         A ``to_cart`` boolean keyword arg is also given specifying
#         whether the product is being added to a cart or wishlist.
#         If a product is being added to the cart, then its stock
#         level is also validated.
#         When adding to the cart from the wishlist page, a sku is
#         given for the variation, so the creation of choice fields
#         is skipped.
#         """
#         self._product = kwargs.pop("product", None)
#         self._shop = kwargs.pop("shop")
#         self._to_cart = kwargs.pop("to_cart")
#         super(NoQuantityAddProductForm, self).__init__(*args, **kwargs)
#         # Adding from the wishlist with a sku, bail out.
#         if args[0] is not None and args[0].get("sku", None):
#             return
#         # Adding from the product page, remove the sku field
#         # and build the choice fields for the variations.
#         # del self.fields["sku"]
#         # option_fields = ProductVariation.option_fields()
#         # if not option_fields:
#         #     return
#         # option_names, option_labels = list(zip(*[(f.name, f.verbose_name)
#         #                                          for f in option_fields]))
#         # option_values = list(zip(*self._product.variations.filter(
#         #     unit_price__isnull=False).values_list(*option_names)))
#         # if option_values:
#         #     for i, name in enumerate(option_names):
#         #         values = [_f for _f in set(option_values[i]) if _f]
#         #         if values:
#         #             field = forms.ChoiceField(label=option_labels[i],
#         #                                       choices=make_choices(values))
#         #             self.fields[name] = field

#     def clean(self):
#         """
#         Determine the chosen variation, validate it and assign it as
#         an attribute to be used in views.
#         """
#         if not self.is_valid():
#             return
#         # Posted data will either be a sku, or product options for
#         # a variation.
#         data = self.cleaned_data.copy()
#         quantity = data.pop("quantity")
#         # shop = data.pop("shop")
#         # Ensure the product has a price if adding to cart.
#         if self._to_cart:
#             data["unit_price__isnull"] = False
#         error = None

#         if self._shop is None:
#             return
#         # self.shop = data['shop']
#         # if self._product is not None:
#         # self.variation = self._product
#         # Chosen options will be passed to the product's
#         # variations.
#         # qs = self._product.variations
#         # else:
#         # A product hasn't been given since we have a direct sku.
#         # qs = ProductVariation.objects
#         # try:
#         # variation = qs.get(**data)
#         # except ProductVariation.DoesNotExist:
#         # error = "invalid_options"
#         # else:
#         # Validate stock if adding to cart.
#         # if self._to_cart:
#         #     if not variation.has_stock():
#         #         error = "no_stock"
#         #     elif not variation.has_stock(quantity):
#         #         error = "no_stock_quantity"

#         # if error is not None:
#         # raise forms.ValidationError(ADD_PRODUCT_ERRORS[error])

#         # self.variation = variation
#         return self.cleaned_data


# class NoQuantityCartItemForm(forms.ModelForm):
#     """docstring for NoQuantityCartItemForm"""
#     quantity = forms.IntegerField(label=_("Quantity"), min_value=0)

#     class Meta:
#         model = NoQuantityCartItem
#         exclude = ()

#     def clean_quantity(self):
#         """
#         Validate that the given quantity is available.
#         """
#         variation = ProductVariation.objects.get(sku=self.instance.sku)
#         quantity = self.cleaned_data["quantity"]
#         if not variation.has_stock(quantity - self.instance.quantity):
#             error = ADD_PRODUCT_ERRORS["no_stock_quantity"].rstrip(".")
#             raise forms.ValidationError("%s: %s" % (error, quantity))
#         return quantity

# NoQuantityCartItemFormSet = inlineformset_factory(
#     NQCart, NoQuantityCartItem, form=NoQuantityCartItemForm, can_delete=True, extra=0)

# NoQCartItemFormSet = inlineformset_factory(NoQCart, NoQCartItem, CartItemForm, can_delete=True, extra=1)
