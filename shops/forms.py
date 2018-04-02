from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from shops.models import UserShop, UserShopDeliveryOption, ShopProduct, ShopProductImage, Cart, CartItem, Order
from cartridge.shop.models import Category
from django.forms.models import inlineformset_factory
from theme.forms import DataGroupModelChoiceField


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
    error_css_class = 'class-error'
    required_css_class = 'class-required'

    class Meta:
        model = UserShop
        fields = ("background", "image", "shopname",
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
            'background': ShopBackgroundField(attrs={'class': ''}),
            'image': ShopImageField(attrs={'class': ''}),
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

    def clean(self):
        cleaned_data = super(ShopForm, self).clean()
        express_empty = True
        payment_empty = True
        for field in cleaned_data.items():
            fname = field[0]
            fvalue = field[1]
            if fname.endswith('_price') and fvalue != None:
                express_empty = False
            if fname.startswith('payment') and fvalue != False and not fname.endswith('_other'):
                payment_empty = False
        if express_empty:
            raise forms.ValidationError(
                _('Заполните хотя бы один способ доставки'))
        if payment_empty:
            raise forms.ValidationError(
                _('Заполните хотя бы один способ оплаты'))
        return cleaned_data

    # def clean_file(self):
    #     file = self.cleaned_data['file']
    #     try:
    #         if file:
    #             file_type = file.content_type.split('/')[0]
    #             if len(file.name.split('.')) == 1:
    #                 raise forms.ValidationError(
    #                     _('File type is not supported'))

    #             if file_type in settings.TASK_UPLOAD_FILE_TYPES:
    #                 if file._size > settings.TASK_UPLOAD_FILE_MAX_SIZE:
    #                     raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (
    #                         filesizeformat(settings.TASK_UPLOAD_FILE_MAX_SIZE), filesizeformat(file._size)))
    #             else:
    #                 raise forms.ValidationError(
    #                     _('File type is not supported'))
    #     except:
    #         pass

    #     return file

    # def __init__(self, *args, **kwargs):
    #     super(ShopForm, self).__init__(*args, **kwargs)
    #     self.fields['background'].widget.attrs.update({'class': 'background'})
        # adding css classes to widgets without define the fields:
        # for field in self.fields:
        #     self.fields[field].widget.attrs['class'] = 'some-class other-class'

    # def as_div(self):
    #     return self._html_output(
    #         normal_row=u'<div%(html_class_attr)s>%(label)s %(field)s %(help_text)s %(errors)s</div>',
    #         error_row=u'<div class="error">%s</div>',
    #         row_ender='</div>',
    #         help_text_html=u'<div class="hefp-text">%s</div>',
    #         errors_on_separate_row=False)


class UserShopDeliveryOptionForm(forms.ModelForm):
    """docstring for UserShopDeliveryOptionForm"""
    class Meta:
        model = UserShopDeliveryOption
        fields = '__all__'
        widgets = {
            'label': forms.TextInput(attrs={'placeholder': 'Способ доставки'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена'}),
        }


class ProductForm(forms.ModelForm):
    """docstring for ProuctForm"""
    categories = DataGroupModelChoiceField(
        queryset=Category.objects.all().order_by('id'),
        label="Категория")

    class Meta:
        model = ShopProduct
        fields = [
            'title',
            'pre_order',
            'categories',
            'price',
            'material',
            # 'categories',
            'condition',
            'keywords',
            'description',
        ]
        # widgets = {
        #     'categories': forms.HiddenInput(),
        # }
        # exclude = ['author', 'performer']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        # self.helper.template = 'theme_form/whole_uni_form.html'
        self.helper.include_media = False
        self.helper.layout.append(
            ButtonHolder(
                HTML("""
                <a class="button dark" href="{% url 'product-list' %}">Назад</a>
                """),
                Submit('submit', 'Сохранить', css_class='button abc'),
            ),
        )


class ProductImageForm(forms.ModelForm):

    class Meta:
        model = ShopProductImage
        fields = ['file']
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
UserShopDeliveryOptionFormSet = inlineformset_factory(
    UserShop,
    UserShopDeliveryOption,
    form=UserShopDeliveryOptionForm,
    can_delete=True,
    extra=1)
ProductImageFormSet = inlineformset_factory(
    ShopProduct,
    ShopProductImage,
    form=ProductImageForm,
    can_delete=True,
    extra=1)
