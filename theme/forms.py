from __future__ import unicode_literals

from django import forms

from mezzanine.core.forms import TinyMceWidget
from mezzanine.utils.static import static_lazy as static
from mezzanine.blog.models import BlogPost
from mezzanine.core.models import CONTENT_STATUS_DRAFT

from theme.models import MyProfile

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


class MyProfileForm(forms.ModelForm):

    class Meta:
        model = MyProfile
        fields = ("image", "city", "phone", "bio")
        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control mask', 'data-inputmask' : "'mask':'9 (999) 999-9999'"}),
        }
        help_texts = {
            'city': 'Укажите конактный адрес',
            'phone': 'Ваш мобильный телефон',
        }

        