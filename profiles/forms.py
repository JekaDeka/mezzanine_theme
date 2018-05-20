from django import forms
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.utils.translation import ugettext, ugettext_lazy as _

from filebrowser_safe.fields import FileBrowseWidget

from shops.forms import ShopBackgroundField, ShopImageField
from profiles.models import UserProfile

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML


# class UserProfileImageField(FileBrowseWidget):
#
#     def __init__(self, attrs=None):
#         self.format = 'image'
#         if attrs is not None:
#             self.attrs = attrs.copy()
#         else:
#             self.attrs = {}
#
#     def render(self, name, value, attrs=None):
#         if value is None:
#             value = ""
#         final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
#         final_attrs['format'] = self.format
#         return render_to_string("shops/background_field.html", dict(locals(), MEDIA_URL=settings.MEDIA_URL))


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        exclude = ('user', 'allow_blogpost_count', 'allow_product_count', 'allow_ordertable_count', 'status',)
        # fields = ("phone",)
        widgets = {
            'bio': forms.Textarea(attrs={'rows': '1'}),
            'phone': forms.TextInput(attrs={'class': 'mask',}),
            'image': ShopImageField(),
            'background': ShopBackgroundField(),
        }
