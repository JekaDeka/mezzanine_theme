from __future__ import unicode_literals

from django import forms
from django.forms.fields import Field

from mezzanine.core.forms import TinyMceWidget
from mezzanine.utils.static import static_lazy as static
from mezzanine.blog.models import BlogPost
from mezzanine.core.models import CONTENT_STATUS_DRAFT
from theme.models import UserShop

setattr(Field, 'is_checkbox', lambda self: isinstance(
    self.widget, forms.CheckboxInput))

# These fields need to be in the form, hidden, with default values,
# since it posts to the blog post admin, which includes these fields
# and will use empty values instead of the model defaults, without
# these specified.
hidden_field_defaults = ("status", "gen_description", "allow_comments")


class СustomBlogForm(forms.ModelForm):

    class Meta:
        model = BlogPost
        fields = ("title", "preview_content", "featured_image", "content") + \
            hidden_field_defaults

    def __init__(self):
        initial = {}
        for field in hidden_field_defaults:
            initial[field] = BlogPost._meta.get_field(field).default
        initial["status"] = CONTENT_STATUS_DRAFT
        super(СustomBlogForm, self).__init__(initial=initial)
        for field in hidden_field_defaults:
            self.fields[field].widget = forms.HiddenInput()


# our new form
class ContactForm(forms.Form):
    contact_email = forms.EmailField(required=True)


class ShopForm(forms.ModelForm):
    error_css_class = 'class-error'
    required_css_class = 'class-required'

    class Meta:
        model = UserShop
        fields = ("background", "image", "shopname", "phone",
                  "country", "city", "bio", "rules",
                  "express_point", "express_point_price",
                  "express_city", "express_city_price",
                  "express_country", "express_country_price",
                  "express_world", "express_world_price",
                  "express_mail", "express_mail_price",
                  "express_personal", "express_personal_price", "express_other",
                  "payment_personal", "payment_bank_transfer", "payment_card_transfer", "payment_other")
        widgets = {
            'shopname': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'background': forms.FileInput(attrs={'id': 'file-1', 'class': 'inputfile inputfile-1'}),
            'image': forms.FileInput(attrs={'id': 'file-5', 'class': 'inputfile inputfile-4'}),
            'phone': forms.TextInput(attrs={'class': 'mask', 'placeholder': '+7 (999) 999-9999'}),
            'express_point_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена'}),
            'express_city_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена'}),
            'express_country_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена'}),
            'express_world_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена'}),
            'express_mail_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена'}),
            'express_personal_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Цена'}),
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
