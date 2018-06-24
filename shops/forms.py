from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.forms.utils import flatatt
from django.forms.models import inlineformset_factory
from django.forms.forms import BoundField


from shops.models import UserShop, ShopProduct, ShopProductImage, Cart, CartItem, Order, \
    UserShopDelivery, UserShopDeliveryOption, ProductReview, UserShopPayment
from cartridge.shop.models import Category

from mezzanine.generic.models import Keyword
from mezzanine.generic.forms import KeywordsWidget
from theme.forms import DataGroupModelChoiceField

from itertools import groupby
from filebrowser_safe.fields import FileBrowseWidget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML


class ShopBackgroundField(FileBrowseWidget):

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
        return render_to_string("shops/background_field.html", dict(locals(), MEDIA_URL=settings.MEDIA_URL))


class ShopImageField(FileBrowseWidget):

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
        return render_to_string("shops/image_field.html", dict(locals(), MEDIA_URL=settings.MEDIA_URL))


class ProductImageField(FileBrowseWidget):

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
        return render_to_string("product/image_field.html", dict(locals(), MEDIA_URL=settings.MEDIA_URL))


class QuantityInput(forms.NumberInput):
    """docstring for QuantityInput."""

    def render(self, name, value, attrs=None):
        rendered = super(QuantityInput, self).render(name, value, attrs=attrs)
        return '<div class="qtyminus"></div>%s<div class="qtyplus"></div>' % (rendered)


class AddProductForm(forms.Form):
    quantity = forms.IntegerField(
        label="", min_value=1, widget=QuantityInput(attrs={'class': 'qty'}))
    product_id = forms.CharField(required=False, widget=forms.HiddenInput())
    title = forms.CharField(required=False, widget=forms.HiddenInput())
    price = forms.CharField(required=False, widget=forms.HiddenInput())
    url = forms.CharField(required=False, widget=forms.HiddenInput())
    image = forms.CharField(required=False, widget=forms.HiddenInput())
    shop_id = forms.CharField(required=False, widget=forms.HiddenInput())
    shop_image = forms.CharField(required=False, widget=forms.HiddenInput())
    shop_slug = forms.CharField(required=False, widget=forms.HiddenInput())
    shop_name = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop("product", None)
        self.to_cart = kwargs.pop("to_cart", False)
        super(AddProductForm, self).__init__(*args, **kwargs)
        if self.product:
            self.fields['product_id'].initial = self.product.id
            self.fields['title'].initial = self.product.title
            self.fields['price'].initial = self.product.price
            self.fields['url'].initial = self.product.get_absolute_url()
            img = self.product.images.first()
            if img:
                self.fields['image'].initial = img.file

            self.fields['shop_id'].initial = self.product.shop.id
            self.fields['shop_image'].initial = self.product.shop.image
            self.fields['shop_slug'].initial = self.product.shop.slug
            self.fields['shop_name'].initial = self.product.shop.shopname

        self.fields['quantity'].initial = 1


class ShopForm(forms.ModelForm):
    deliveries = UserShopDelivery.objects.all()

    class Meta:
        model = UserShop
        exclude = ("user", "delivery_options")

        widgets = {
            'background': ShopBackgroundField(attrs={'class': ''}),
            'image': ShopImageField(attrs={'class': ''}),
            # 'delivery_options':  forms.CheckboxSelectMultiple(),
            'delivery_other': forms.Textarea(attrs={'rows': '1'}),
            'payment_options':  forms.CheckboxSelectMultiple(),
            'payment_other': forms.Textarea(attrs={'rows': '1'}),
            'bio': forms.Textarea(attrs={'rows': '1'}),
            'rules': forms.Textarea(attrs={'rows': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super(ShopForm, self).__init__(*args, **kwargs)
        self.fields['background'].label = ""
        self.fields['background'].help_text = ""
        self.fields['image'].label = ""
        self.fields['image'].help_text = ""
        self.fields['payment_options'].label = ""

        initial_options = UserShopDeliveryOption.objects.filter(
            shop=self.instance).values_list('delivery', 'price')
        for delivery in self.deliveries:
            status = False
            price = None
            initial_option = initial_options.filter(delivery=delivery)
            if initial_option:
                status = True
                # if user didn't set the price it saves as 0
                if initial_option[0][1]:
                    price = initial_option[0][1]

            self.fields['tmp_delivery_status_%s' % delivery.id] = forms.BooleanField(
                label=delivery.label, required=False, initial=status)
            self.fields['tmp_delivery_price_%s' % delivery.id] = forms.IntegerField(
                label="Цена", required=False, initial=price)

    def render_delivery_options(self):
        for name in self.fields:
            if name.startswith('tmp_'):
                field = self.fields[name]
                yield BoundField(self, field, name)

    def get_delivery_options(self):
        for name, value in self.cleaned_data.items():
            if name.startswith('tmp_delivery_status_') and value == True:
                delivery_id = name.rpartition('_')[-1]
                price = self.cleaned_data['tmp_delivery_price_%s' %
                                          delivery_id]
                yield (delivery_id, price)

    def get_delivery_options_id(self):
        for name, value in self.cleaned_data.items():
            if name.startswith('tmp_delivery_status_') and value == True:
                delivery_id = name.rpartition('_')[-1]
                yield delivery_id

    # def clean(self):
    #     cleaned_data = super(ShopForm, self).clean()
    #     options = filter(lambda k: 'tmp_delivery_status_' in k, cleaned_data)
    #     print(options)
    #     raise forms.ValidationError({'tmp_delivery_status_2': ["", ],
    #                                  'tmp_delivery_price_2': ["Заполните хотя бы одно поле", ]},
    #                                 code='invalid')


class UserShopDeliveryOptionForm(forms.ModelForm):
    """docstring for UserShopDeliveryOptionForm"""
    class Meta:
        model = UserShopDeliveryOption
        fields = '__all__'


class ThemeKeywordsWidget(KeywordsWidget):
    """docstring for ThemeKeywordsWidget."""

    def format_output(self, rendered_widgets):
        """
        Wraps the output HTML with a list of all available ``Keyword``
        instances that can be clicked on to toggle a keyword.
        """
        rendered = super(KeywordsWidget, self).format_output(rendered_widgets)
        # links = ""
        # for keyword in Keyword.objects.all().order_by("title"):
        #     # prefix = "+" if str(keyword.id) not in self._ids else "-"
        #     prefix = ""
        #     links += ("<option value='%s%s'>" % (prefix, str(keyword)))
        # rendered += mark_safe("<datalist id='tag-list'>%s</datalist>" % links)
        return rendered


class ProductForm(forms.ModelForm):
    categories = DataGroupModelChoiceField(
        queryset=Category.objects.all().order_by('id'),
        label="Категория")

    class Meta:
        model = ShopProduct
        fields = [
            'title',
            'size',
            'categories',
            'price',
            'material',
            'condition',
            'keywords',
            'description',
        ]
        widgets = {
            # 'material': forms.TextInput(attrs={'multiple': 'multiple'}),
            'description': forms.Textarea(attrs={'rows': '1'}),
        }
        # exclude = ['author', 'performer']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['keywords'].label = "Теги"
        self.fields['keywords'].help_text = "Введите значения через запятую"
        self.fields['keywords'].widget = ThemeKeywordsWidget(
            attrs={'multiple': 'multiple'})
        self.fields['material'].widget = forms.TextInput(
            attrs={'multiple': 'multiple'})
        # self.fields['description'].label = ""
        # self.helper = FormHelper(self)
        # self.helper.template = 'theme_form/whole_uni_form.html'
        # self.helper.include_media = False
        # self.helper.layout.append(
        #     ButtonHolder(
        #         HTML("""
        #         <a class="button dark" href="{% url 'product-list' %}">Назад</a>
        #         """),
        #         Submit('submit', 'Сохранить', css_class='button abc'),
        #     ),
        # )


class ProductImageForm(forms.ModelForm):

    class Meta:
        model = ShopProductImage
        fields = ['file']
        widgets = {
            'file': ProductImageField(),
        }
        # exclude = ['description', ]


class CartItemForm(forms.ModelForm):
    """
    Model form for each item in the cart - used for the
    ``CartItemFormSet`` below which controls editing the entire cart.
    """
    # quantity = forms.IntegerField(label="Количество", min_value=0)
    quantity = forms.IntegerField(
        label="Количество", min_value=0, widget=QuantityInput(attrs={'class': 'qty'}))

    class Meta:
        model = CartItem
        fields = ("quantity",)


class OrderFormAdmin(forms.ModelForm):
    """docstring for OrderFormAdmin."""

    def __init__(self, *args, **kwargs):
        super(OrderFormAdmin, self).__init__(*args, **kwargs)
        self.fields['shipping'].queryset = UserShopDeliveryOption.objects.filter(
            shop=self.instance.shop)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('user_first_name', 'user_middle_name', 'user_last_name',
                  'user_phone', 'user_email', 'user_country', 'user_region', 'user_city', 'shipping', 'payment',
                  'user_address', 'user_postcode', 'user_additional_info')
        widgets = {
            'shipping': forms.RadioSelect(),
            'payment': forms.RadioSelect(),
            'user_phone': forms.TextInput(attrs={'class': 'mask',}),
            'user_additional_info': forms.Textarea(attrs={'rows': '1'}),
            # 'user_email': forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        self.shop = kwargs.pop("shop", None)
        self.user = kwargs.pop("user", None)
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields["shipping"].queryset = UserShopDeliveryOption.objects.filter(
            shop=self.shop)
        self.fields['shipping'].empty_label = None

        self.fields['payment'].queryset = self.shop.payment_options.all()
        self.fields['payment'].empty_label = None

        if self.user:
            try:
                profile = self.user.profile
                self.fields['user_first_name'].initial = self.user.profile.first_name
                self.fields['user_last_name'].initial = self.user.profile.last_name
                self.fields['user_phone'].initial = self.user.profile.phone
                self.fields['user_email'].initial = self.user.email
                self.fields['user_country'].initial = self.user.profile.country
                self.fields['user_city'].initial = self.user.profile.city
                self.fields['user_region'].initial = self.user.profile.region
            except Exception as e:
                pass


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ("rating", "content",)

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop("product", None)
        super(ProductReviewForm, self).__init__(*args, **kwargs)


# class OrderStatusChoiceForm(forms.Form):
#      def __init__(self, *args, **kwargs):
#          super(OrderStatusChoiceForm, self).__init__(*args, **kwargs)
#          for status in settings.SHOP_ORDER_STATUS_CHOICES:
#              self.fields['status_type_%s' % status[0]] = forms.BooleanField(
#                  label=status[1], required=False)

class FilterForm(forms.Form):
    min_price = forms.IntegerField(label="", min_value=0, required=False, widget=forms.NumberInput(
        attrs={'class': 'price-input-filter', 'placeholder': 'От'}))
    min_price.group = "Цена"
    max_price = forms.IntegerField(label="", min_value=0, required=False, widget=forms.NumberInput(
        attrs={'class': 'price-input-filter', 'placeholder': 'До'}))
    max_price.group = "Цена"
    deliveries = UserShopDelivery.objects.all()
    payments = UserShopPayment.objects.all()

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        for payment in self.payments:
            self.fields['payment_type_%s' % payment.id] = forms.BooleanField(
                label=payment.label, required=False)
            self.fields['payment_type_%s' %
                        payment.id].group = "Способы оплаты"

        for delivery in self.deliveries:
            self.fields['delivery_type_%s' % delivery.id] = forms.BooleanField(
                label=delivery.label, required=False)
            self.fields['delivery_type_%s' % delivery.id].group = "Доставка"

        for condition in settings.PRODUCT_STATUS_TYPE_CHOICES:
            self.fields['condition_type_%s' % condition[0]] = forms.BooleanField(
                label=condition[1], required=False)
            self.fields['condition_type_%s' %
                        condition[0]].group = "Вид товара"


CartItemFormSet = inlineformset_factory(Cart, CartItem, form=CartItemForm,
                                        can_delete=True, extra=0)


# UserShopDeliveryOptionFormSet = inlineformset_factory(
#     UserShop,
#     UserShop.delivery_options.through,
#     form=UserShopDeliveryOptionForm,
#     can_delete=False,
#     extra=1)

ProductImageFormSet = inlineformset_factory(
    ShopProduct,
    ShopProductImage,
    form=ProductImageForm,
    can_delete=True,
    extra=6, max_num=6)
