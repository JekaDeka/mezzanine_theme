from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.template.loader import get_template, render_to_string

from ordertable.models import OrderTableItem, OrderTableItemImage, OrderTableItemRequest, OrderTableItemCategory
from ordertable.forms import OrderTableForm, OrderTableImageFormSet, MessageForm

from mezzanine.utils.views import paginate
from mezzanine.conf import settings

User = get_user_model()


def order_list(request, tag=None, year=None, month=None, username=None,
               category=None, template="ordertable/order_list.html",
               extra_context=None):
    templates = []
    orders = OrderTableItem.objects.filter(available=True).filter(
        performer=None)
    # author = request.user
    order_categories = OrderTableItemCategory.objects.all()
    if category is not None:
        category = get_object_or_404(OrderTableItemCategory, slug=category)
        orders = orders.filter(categories=category)

    region = request.GET.get('region', None)
    if region is not None:
        try:
            orders = orders.filter(Q(lock_in_region=False) | Q(
                author__profile__region=region))
        except Exception as e:
            messages.error(request, "Не удалось применить фильтр региона")
            raise

    orders = paginate(orders, request.GET.get("page", 1),
                      15,
                      settings.MAX_PAGING_LINKS)
    context = {"orders": orders, "year": year, "month": month,
               "tag": tag, "category": category, "order_categories": order_categories}
    context.update(extra_context or {})
    templates.append(template)
    return TemplateResponse(request, templates, context)


def order_detail(request, pk, template="order/order_detail.html",
                 extra_context=None):
    pass
#     templates = []
#     try:
#         order = OrderTableItem.objects.get(pk=pk)
#     except Exception as e:
#         return redirect('order_list')

    # form = OrderMessageForm()
#     if request.method == 'POST':
#         form = OrderMessageForm(data=request.POST)
#         if form.is_valid():
#             message = request.POST.get('message', '')
#             template = get_template('email/order_email_request_approved.html')
#             context = {
#                 'request': request,
#                 'order': order,
#                 'performer': request.user,
#                 'message': message,
#             }
#             content = template.render(context)

#             email = EmailMessage(
#                 "Для вашего заказа нашелся исполнитель handmaker.top",
#                 content,
#                 settings.EMAIL_HOST_USER,
#                 [order.author.email],
#                 headers={'Reply-To': request.user.email}
#             )
#             email.content_subtype = 'html'
#             if order_request_add(request, pk):
#                 email.send(fail_silently=True)
#             return HttpResponseRedirect(reverse('order_detail', args=[pk]))

#     context = {"order": order, "form": form}

#     context.update(extra_context or {})
#     templates.append(template)
#     return TemplateResponse(request, templates, context)


def order_request_add(request, order_pk):
    status = False
    try:
        order = OrderTableItem.objects.get(pk=order_pk, performer=None)
        if request.user == order.author:
            raise ValueError('Нельзя откликнуться на собственную заявку')
        orderRequest = OrderTableItemRequest(
            order=order, performer=request.user)
        orderRequest.save()
    except Exception as error:
        if 'UNIQUE constraint' in error.args[0]:
            messages.error(request, 'Вы уже откликнулись на данный заказ')
        elif 'matching query does not exist' in error.args[0]:
            messages.error(request, 'Данная заявка закрыта')
        else:
            messages.error(request, error.args[0])

    else:
        status = True
        messages.success(
            request, "Ваше сообщение успешно отправлено. Автор данный заявки свяжется с вами по мере своих возможностей.")
    return status


@login_required
def order_request_assign(request, order_pk, performer_pk, extra_context=None):
    try:
        order = OrderTableItem.objects.get(pk=order_pk)
        performer = User.objects.get(pk=performer_pk)
        order.performer = performer
        order.active = False
        order.save()

        ###
        # order.order_requests.all().delete()
        ###
    except Exception as e:
        messages.error(request, e.args[0])
    else:
        template = get_template('email/order_email_request_assign.html')
        context = {
            'request': request,
            'order': order,
            'order_url': order.get_absolute_url,
            'performer': performer,
        }
        content = template.render(context)
        email = EmailMessage(
            "Ваша заявка на исполнение заказа одобрена handmaker.top",
            content,
            settings.EMAIL_HOST_USER,
            [order.author.email],
            headers={'Reply-To': performer.email}
        )
        email.content_subtype = 'html'
        email.send(fail_silently=True)
        messages.success(
            request, "Исполнитель успешно назначен. Ему отправлено уведомление.")

    return redirect(reverse_lazy('ordertableitemrequest-list'))


@login_required
def order_request_delete(request, order_pk, performer_pk, extra_context=None):
    if request.user.has_perm('theme.change_ordertableitemrequest'):
        try:
            order = OrderTableItemRequest.objects.get(
                order=order_pk, performer=performer_pk)
            order.delete()
        except Exception as e:
            messages.error(request, e.args[0])
        else:
            messages.success(request, "Отклик успешно отклонен.")

    return redirect(reverse_lazy('ordertableitemrequest-list'))


@method_decorator(login_required, name='dispatch')
class OrderTableItemList(ListView):
    model = OrderTableItem
    # template_name = "orders/ordertableitem_user_list.html"
    context_object_name = "ordertableitem_list"

    def get_queryset(self):
        return OrderTableItem.objects.filter(
            author=self.request.user
            ).prefetch_related(
                'order_requests','images'
                ).select_related(
                    'categories', 'performer', 'performer__profile'
                    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        remain = self.request.user.profile.allow_blogpost_count - \
            len(context['object_list'])
        context['remain'] = remain
        return context


@method_decorator(login_required, name='dispatch')
class OrderTableItemCreate(CreateView):
    model = OrderTableItem
    form_class = OrderTableForm
    success_url = reverse_lazy('ordertableitem-list')


@method_decorator(login_required, name='dispatch')
class OrderTableItemUpdate(UpdateView):
    model = OrderTableItem
    form_class = OrderTableForm
    success_url = reverse_lazy('ordertableitem-list')
    # template_name = "orders/ordertableitem_form.html"


@method_decorator(login_required, name='dispatch')
class OrderTableItemDelete(DeleteView):
    model = OrderTableItem
    success_url = reverse_lazy('ordertableitem-list')
    # template_name = "orders/ordertableitem_confirm_delete.html"

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(OrderTableItemDelete, self).get_object()
        if not obj.author == self.request.user:
            raise Http404
        return obj


@method_decorator(login_required, name='dispatch')
class OrderTableItemImageCreate(CreateView):
    """docstring for OrderTableItemImageCreate"""
    model = OrderTableItem
    form_class = OrderTableForm
    success_url = reverse_lazy('ordertableitem-list')
    # template_name = "orders/ordertableitem_form.html"
    warning_message = "Исчерпан лимит"
    success_message = "Заявка успешно создана"

    def dispatch(self, request, *args, **kwargs):
        if request.user.orders_as_author.count() >= 10:
            messages.warning(self.request, self.warning_message)
            return redirect(self.success_url)
        return super(OrderTableItemImageCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(OrderTableItemImageCreate,
                     self).get_context_data(**kwargs)
        if self.request.POST:
            data['ordertableitemimage'] = OrderTableImageFormSet(
                self.request.POST)
        else:
            data['ordertableitemimage'] = OrderTableImageFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        ordertableitemimage = context['ordertableitemimage']
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.author = self.request.user
            self.object.save()

            if ordertableitemimage.is_valid():
                ordertableitemimage.instance = self.object
                ordertableitemimage.save()

            messages.success(self.request, self.success_message)
        return super(OrderTableItemImageCreate, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class OrderTableItemImageUpdate(UpdateView):
    model = OrderTableItem
    form_class = OrderTableForm
    # fields = '__all__'
    success_url = reverse_lazy('ordertableitem-list')
    # template_name = "orders/ordertableitem_form.html"
    queryset = OrderTableItem.objects.select_related()
    success_message = "Заявка успешно обновлена"

    def get_context_data(self, **kwargs):
        data = super(OrderTableItemImageUpdate,
                     self).get_context_data(**kwargs)
        if self.request.POST:
            data['ordertableitemimage'] = OrderTableImageFormSet(
                self.request.POST, instance=self.object)
        else:
            data['ordertableitemimage'] = OrderTableImageFormSet(
                instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        ordertableitemimage = context['ordertableitemimage']
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.author = self.request.user
            self.object.save()

            if ordertableitemimage.is_valid():
                ordertableitemimage.instance = self.object
                ordertableitemimage.save()

            messages.success(self.request, self.success_message)
        return super(OrderTableItemImageUpdate, self).form_valid(form)

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(OrderTableItemImageUpdate, self).get_object()
        if not obj.author == self.request.user:
            raise Http404
        return obj


class OrderTableItemDetail(DetailView):
    model = OrderTableItem
    # template_name = "orders/order_detail.html"
    context_object_name = 'order'
    queryset = OrderTableItem.objects.prefetch_related(
        'images').select_related("author")

    def get_context_data(self, **kwargs):
        context = super(OrderTableItemDetail, self).get_context_data(**kwargs)
        context['form'] = MessageForm()
        return context

    def post(self, request, *args, **kwargs):
        form = MessageForm(request.POST)
        obj = self.get_object()
        if form.is_valid():
            context = {
                'request': request,
                'order': obj,
                'performer': request.user,
                'message': form.cleaned_data['message'],
            }
            email = form.create_email(context, obj, request.user)
            if order_request_add(request, obj.pk):
                email.send(fail_silently=True)

        return redirect(obj.get_absolute_url())

    # def form_valid(self, form):
    #     # context = {
    #     #     'request': self.request,
    #     #     'order': self.object,
    #     #     'performer': self.request.user,
    #     #     'message': form.message,
    #     # }
    #     # email = form.create_email(context, self.object, self.request.user)
    #     # if order_request_add(self.request, self.object.pk):
    #     #     email.send(fail_silently=True)
    #     return HttpResponseRedirect(reverse('order_detail', args=[self.object.pk]))


@method_decorator(login_required, name='dispatch')
class OrderTableIncomeRequestList(ListView):
    model = OrderTableItemRequest
    # template_name = "ordertable/ordertableitem_request.html"
    context_object_name = "ordertableitemrequest_list"

    def get_queryset(self):
        orders = self.request.user.orders_as_author.all().prefetch_related('images')
        return OrderTableItemRequest.objects.filter(order__in=orders).select_related('performer', 'order')

    def get_context_data(self, **kwargs):
        data = super(OrderTableIncomeRequestList,
                     self).get_context_data(**kwargs)
        data['ordertableitems'] = self.request.user.orders_as_author.all(
        ).prefetch_related('images')
        return data


@method_decorator(login_required, name='dispatch')
class OrderTableOutcomeRequestList(ListView):
    model = OrderTableItemRequest
    # template_name = "orders/ordertableitem_request_outcome.html"
    context_object_name = "ordertableitemrequest_list"

    def get_queryset(self):
        return OrderTableItemRequest.objects.filter(performer=self.request.user).prefetch_related('order__images')
