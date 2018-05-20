from django import forms
from ordertable.models import OrderTableItem, OrderTableItemImage
from django.forms.models import inlineformset_factory
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage

from mezzanine.conf import settings

from shops.forms import ProductImageField, ThemeKeywordsWidget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML


class MessageForm(forms.Form):
    message = forms.CharField(
        required=False,
        label="Ваше сообщение",
        widget=forms.Textarea
    )

    def create_email(self, context, order, user):
        template = get_template('email/order_email_request_approved.html')
        content = template.render(context)
        email = EmailMessage(
            "Для вашей заявки нашелся исполнитель handmaker.top",
            content,
            settings.EMAIL_HOST_USER,
            [order.author.email],
            headers={'Reply-To': user.email}
        )
        email.content_subtype = 'html'
        return email


class OrderTableAdminForm(forms.ModelForm):

    class Meta:
        model = OrderTableItem
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(OrderTableAdminForm, self).__init__(*args, **kwargs)
        self.fields['ended'].widget.format = '%d/%m/%Y'
        self.fields['ended'].input_formats = ['%d/%m/%Y']


class OrderTableItemRequestActionForm(forms.Form):
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


class OrderTableForm(forms.ModelForm):
    """docstring for OrderTableForm"""
    class Meta:
        model = OrderTableItem
        fields = [
            'title',
            'price',
            'count',
            'ended',
            'color_suggest',
            'size_suggest',
            'material_suggest',
            'lock_in_region', 'categories', 'description',
            'keywords']
        widgets = {
            'author': forms.HiddenInput(),
            'performer': forms.HiddenInput(),
            'description': forms.Textarea(attrs={'rows': '1'}),
        }
        # exclude = ['author', 'performer']

    def __init__(self, *args, **kwargs):
        super(OrderTableForm, self).__init__(*args, **kwargs)
        self.fields['ended'].widget.format = '%d/%m/%Y'
        self.fields['ended'].input_formats = ['%d/%m/%Y']
        self.fields['categories'].label = ""

        self.fields['keywords'].label = "Теги"
        self.fields['keywords'].help_text = "Введите значения через запятую"
        self.fields['keywords'].widget = ThemeKeywordsWidget(
            attrs={'multiple': 'multiple'})
        # self.helper = FormHelper(self)
        # # self.helper.template = 'theme_form/whole_uni_form.html'
        # self.helper.include_media = False
        # self.helper.layout.append(
        #     ButtonHolder(
        #         HTML("""
        #         <a class="button dark" href="{% url 'ordertableitem-list' %}">Назад</a>
        #         """),
        #         Submit('submit', 'Сохранить', css_class='button abc'),
        #     ),
        # )


class OrderTableImageForm(forms.ModelForm):

    class Meta:
        model = OrderTableItemImage
        fields = ['file']
        widgets = {
            'file': ProductImageField(),
        }


OrderTableImageFormSet = inlineformset_factory(
    OrderTableItem,
    OrderTableItemImage,
    form=OrderTableImageForm,
    can_delete=True,
    extra=6, max_num=6)
