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
from django.forms.formsets import BaseFormSet
from django.utils.datastructures import MultiValueDict
from django.template.loader import render_to_string

from mezzanine.conf import settings
from mezzanine.accounts.forms import ProfileForm
from mezzanine.utils.static import static_lazy as static
from mezzanine.generic.forms import KeywordsWidget
from mezzanine.blog.models import BlogPost
from mezzanine.core.models import CONTENT_STATUS_DRAFT

from cartridge.shop import checkout
from cartridge.shop.models import Cart, CartItem, Order, DiscountCode, Category, ProductOption, ProductVariation, Product, ProductImage
from cartridge.shop.forms import FormsetForm, DiscountForm, AddProductForm, OrderForm
from cartridge.shop.utils import (make_choices, set_locale, set_shipping,
                                  clear_session)

# from profiles.models import UserProfile, Region, City
from ordertable.models import OrderTableItem, OrderTableItemImage
# from shops.models import UserShop, UserShopDeliveryOption, ShopProduct, ShopProductImage
from filebrowser_safe.fields import FileBrowseWidget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML

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


# class UserProfileForm(forms.ModelForm):

#     class Media:
#         js = ('javascript/mymarkup.js',)

#     class Meta:
#         model = UserProfile
#         exclude = ('user', 'allow_blogpost_count', 'allow_product_count')
#         # fields = ("phone",)
#         widgets = {
#             'first_name': forms.TextInput(attrs={'class': '', 'placeholder': 'Имя', }),
#             'last_name': forms.TextInput(attrs={'class': '', 'placeholder': 'Фамилия', }),
#             'phone': forms.TextInput(attrs={'class': 'mask', 'placeholder': '+7 (999) 999-9999'}),
#             'image': forms.FileInput(attrs={'id': 'file-2', 'class': 'inputfile inputfile-2'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super(UserProfileForm, self).__init__(*args, **kwargs)


# class ShopForm(forms.ModelForm):
#     error_css_class = 'class-error'
#     required_css_class = 'class-required'

#     class Meta:
#         model = UserShop
#         fields = ("background", "image", "shopname",  # "phone",
#                   # "country", "region", "city",
#                   "bio", "rules",
#                   "express_point", "express_point_price",
#                   "express_city", "express_city_price",
#                   "express_country", "express_country_price",
#                   "express_world", "express_world_price",
#                   "express_mail", "express_mail_price",
#                   "express_personal", "express_personal_price", "express_other",
#                   "payment_personal", "payment_bank_transfer", "payment_card_transfer", "payment_other")
#         widgets = {
#             'shopname': forms.TextInput(attrs={'class': 'form-control'}),
#             'background': forms.FileInput(attrs={'id': 'file-1', 'class': 'inputfile inputfile-1'}),
#             'image': forms.FileInput(attrs={'id': 'file-5', 'class': 'inputfile inputfile-4'}),
#             # 'phone': forms.TextInput(attrs={'class': 'mask', 'placeholder': '+7 (999) 999-9999'}),
#             # 'express_point_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена', 'readonly': 'readonly'}),
#             # 'express_city_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена', 'readonly': 'readonly'}),
#             # 'express_country_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена', 'readonly': 'readonly'}),
#             # 'express_world_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена', 'readonly': 'readonly'}),
#             # 'express_mail_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена', 'readonly': 'readonly'}),
#             # 'express_personal_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена', 'readonly': 'readonly'}),
#             # 'express_other': forms.Textarea(attrs={'placeholder': 'Дополнительная информация о доставке', 'rows': '5'}),
#             # 'payment_other': forms.Textarea(attrs={'placeholder': 'Дополнительная информация об оплате', 'rows': '5'}),
#             'bio': forms.Textarea(attrs={'placeholder': 'Описание магазина'}),
#             'rules': forms.Textarea(attrs={'placeholder': 'Правила магазина'}),
#         }

#     def clean_file(self):
#         file = self.cleaned_data['file']
#         try:
#             if file:
#                 file_type = file.content_type.split('/')[0]
#                 if len(file.name.split('.')) == 1:
#                     raise forms.ValidationError(
#                         _('File type is not supported'))

#                 if file_type in settings.TASK_UPLOAD_FILE_TYPES:
#                     if file._size > settings.TASK_UPLOAD_FILE_MAX_SIZE:
#                         raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (
#                             filesizeformat(settings.TASK_UPLOAD_FILE_MAX_SIZE), filesizeformat(file._size)))
#                 else:
#                     raise forms.ValidationError(
#                         _('File type is not supported'))
#         except:
#             pass

#         return file
#     # def __init__(self, *args, **kwargs):
#     #     super(ShopForm, self).__init__(*args, **kwargs)
#     #     # adding css classes to widgets without define the fields:
#     #     for field in self.fields:
#     #         self.fields[field].widget.attrs['class'] = 'some-class other-class'

#     # def as_div(self):
#     #     return self._html_output(
#     #         normal_row=u'<div%(html_class_attr)s>%(label)s %(field)s %(help_text)s %(errors)s</div>',
#     #         error_row=u'<div class="error">%s</div>',
#     #         row_ender='</div>',
#     #         help_text_html=u'<div class="hefp-text">%s</div>',
#     #         errors_on_separate_row=False)


# class UserShopDeliveryOptionForm(forms.ModelForm):
#     """docstring for UserShopDeliveryOptionForm"""
#     class Meta:
#         model = UserShopDeliveryOption
#         exclude = ()
#         widgets = {
#             'label': forms.TextInput(attrs={'placeholder': 'Способ доставки'}),
#             'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена'}),
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

    def render(self, name, value, attrs=None):
        if value is None:
            value = []
        final_attrs = self.build_attrs(attrs, name=name)
        output = [format_html(
            '<select multiple="multiple" style="display: none;" "{}>', flatatt(final_attrs))]
        options = self.render_options(value)
        if options:
            output.append(options)
        output.append('</select>')
        return mark_safe('\n'.join(output))


class DataGroupModelChoiceField(forms.ModelMultipleChoiceField):

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = DataGroupSelect
        super(DataGroupModelChoiceField, self).__init__(*args, **kwargs)


class SelectForm(forms.ModelForm):
    categories = DataGroupModelChoiceField(
        queryset=Category.objects.all().order_by('id'),
        label="Категории")


class ThemeCheckboxInput(forms.CheckboxInput):
    """docstring for ThemeCheckboxInput"""

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, type='checkbox', name=name)
        if self.check_test(value):
            final_attrs['checked'] = 'checked'
        if not (value is True or value is False or value is None or value == ''):
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(value)
        return format_html('<input{} />', flatatt(final_attrs))

class BlogPostImageField(FileBrowseWidget):

    def __init__(self, attrs=None):
        self.format = 'image'
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}

    def render(self, name, value, attrs=None):
        if value is None:
            value = ""
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        final_attrs['format'] = self.format
        return render_to_string("blog/blogpost_image_field.html", dict(locals(), MEDIA_URL=settings.MEDIA_URL))

class BlogPostKeywordsWidget(KeywordsWidget):
    """docstring for ThemeKeywordsWidget."""

    def format_output(self, rendered_widgets):
        return super(KeywordsWidget, self).format_output(rendered_widgets)

class BlogPostForm(forms.ModelForm):
    """docstring for BlogPostForm"""
    class Meta:
        model = BlogPost
        fields = ['title', 'featured_image', 'preview_content', 'content', 'allow_comments', 'categories', 'keywords']
        widgets = {
            'featured_image': BlogPostImageField(),
            'preview_content': forms.Textarea(attrs={'class': 'small_editor', 'placeholder': 'Имя', }),
            'categories': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super(BlogPostForm, self).__init__(*args, **kwargs)
        self.fields['preview_content'].label = ""
        self.fields['content'].label = ""
        self.fields['content'].help_text = "Основной текст статьи"
        self.fields['keywords'].label = "Теги"
        self.fields['keywords'].help_text = "Введите значения через запятую"
        self.fields['keywords'].widget = BlogPostKeywordsWidget(attrs={'multiple': 'multiple'})
    #     self.helper = FormHelper(self)
    #     self.helper.template = 'theme_form/whole_uni_form.html'
    #     self.helper.include_media = False
    #     self.helper.layout.append(
    #         ButtonHolder(
    #             HTML("""
    #             <a class="button dark" href="{% url 'blogpost-list' %}">Назад</a>
    #             """),
    #             Submit('submit', 'Сохранить', css_class='button abc'),
    #         ),
    #     )


# class ProductForm(forms.ModelForm):
#     """docstring for ordertableitemForm"""
#     categories = DataGroupModelChoiceField(
#         queryset=Category.objects.all().order_by('id'),
#         label="Категория")

#     class Meta:
#         model = ShopProduct
#         fields = [
#             'title',
#             'pre_order',
#             'categories',
#             'price',
#             'material',
#             # 'categories',
#             'condition',
#             'keywords',
#             'description',
#         ]
#         # widgets = {
#         #     'categories': forms.HiddenInput(),
#         # }
#         # exclude = ['author', 'performer']

#     def __init__(self, *args, **kwargs):
#         super(ProductForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper(self)
#         # self.helper.template = 'theme_form/whole_uni_form.html'
#         self.helper.include_media = False
#         self.helper.layout.append(
#             ButtonHolder(
#                 HTML("""
#                 <a class="button dark" href="{% url 'product-list' %}">Назад</a>
#                 """),
#                 Submit('submit', 'Сохранить', css_class='button abc'),
#             ),
#         )


# class ProductImageForm(forms.ModelForm):

#     class Meta:
#         model = ShopProductImage
#         fields = ['file']
#         # exclude = ['description', ]


# UserShopDeliveryOptionFormSet = inlineformset_factory(
#     UserShop,
#     UserShopDeliveryOption,
#     form=UserShopDeliveryOptionForm,
#     can_delete=True,
#     extra=1)


# ProductImageFormSet = inlineformset_factory(
#     ShopProduct,
#     ShopProductImage,
#     form=ProductImageForm,
#     can_delete=True,
#     extra=1)
