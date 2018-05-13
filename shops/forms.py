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
    UserShopDelivery, UserShopDeliveryOption
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


class AddProductForm(forms.Form):
    quantity = forms.IntegerField(label="Количество", min_value=1)
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
            'pre_order',
            # 'categories',
            'price',
            'material',
            'condition',
            'keywords',
            'description',
        ]
        widgets = {
            'material': forms.TextInput(attrs={'multiple': 'multiple'}),
        }
        # exclude = ['author', 'performer']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['keywords'].label = "Теги"
        self.fields['keywords'].help_text = "Введите значения через запятую"
        # self.fields['description'].label = ""
        self.fields['keywords'].widget = ThemeKeywordsWidget(
            attrs={'multiple': 'multiple'})
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

    quantity = forms.IntegerField(label="Количество", min_value=0)

    class Meta:
        model = CartItem
        fields = ("quantity",)

    # def clean_quantity(self):
    #     """
    #     Validate that the given quantity is available.
    #     """
    #     variation = ProductVariation.objects.get(sku=self.instance.sku)
    #     quantity = self.cleaned_data["quantity"]
    #     if not variation.has_stock(quantity - self.instance.quantity):
    #         error = ADD_PRODUCT_ERRORS["no_stock_quantity"].rstrip(".")
    #         raise forms.ValidationError("%s: %s" % (error, quantity))
    #     return quantity


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('user_first_name', 'user_middle_name', 'user_last_name',
                  'user_phone', 'user_email', 'user_country', 'user_region', 'user_city', 'shipping_type',
                  'user_address', 'user_postcode', 'user_additional_info')
    # user_first_name = forms.CharField(label="Имя", max_length=255)
    # user_middle_name = forms.CharField(required=False, label="Отчество", max_length=255)
    # user_last_name = forms.CharField(label="Фамилия", max_length=255)
    #
    # user_phone = forms.CharField(label="Телефон", max_length=20)
    # user_email = forms.EmailField(label="Почта", max_length=255)
    #
    # user_country = forms.CharField(label="Страна", max_length=100)
    # user_region = forms.CharField(label="Регион", max_length=100)
    # user_city = forms.CharField(label="Город", max_length=100)

    shipping_type = forms.ChoiceField(
        label="Доставка", choices=[], required=True, widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        self.shop = kwargs.pop("shop", None)
        self.user = kwargs.pop("user", None)
        super(OrderForm, self).__init__(*args, **kwargs)
        if self.shop:
            self.fields['shipping_type'].choices = self.shop.get_express_fields()
        if self.user:
            self.fields['user_first_name'].initial = self.user.profile.first_name
            self.fields['user_last_name'].initial = self.user.profile.last_name
            self.fields['user_phone'].initial = self.user.profile.phone
            self.fields['user_email'].initial = self.user.email
            self.fields['user_country'].initial = self.user.profile.country
            self.fields['user_city'].initial = self.user.profile.city
            self.fields['user_region'].initial = self.user.profile.region


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
