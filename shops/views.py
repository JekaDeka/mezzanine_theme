from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, TemplateView
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template.loader import get_template, render_to_string
from django.shortcuts import redirect
from django.core import serializers
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction

from shops.models import UserShop, UserShopDeliveryOption, ShopProduct, ShopProductImage, Cart, Order
from shops.forms import ProductForm, ProductImageForm, UserShopDeliveryOptionFormSet, ShopForm, UserShopDeliveryOptionForm, ProductImageFormSet, AddProductForm, CartItemForm, CartItemFormSet, OrderForm
from shops.utils import Map, recalculate_cart

from cartridge.shop.utils import recalculate_cart, sign

from mezzanine.utils.views import paginate
from mezzanine.conf import settings

from theme.forms import MessageForm


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


def validate_shopname(request):
    shopname = request.GET.get('shopname', None)
    data = {
        'is_taken': UserShop.objects.filter(shopname__iexact=shopname).exclude(user=request.user).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'Магазин с таким именем уже существует.'

    return JsonResponse(data)


def shop_view(request, slug, template_name='accounts/shop_profile.html', extra_context=None):
    try:
        shop = UserShop.objects.get(slug=slug)
    except Exception as e:
        return HttpResponseRedirect(reverse('true_index'))
    try:
        profile = request.user.profile
        data = {'first_name': profile.first_name,
                'email': request.user.email}
    except Exception as e:
        profile = None
        data = None

    form = MessageForm(data)
    if request.method == 'POST':
        form = MessageForm(data=request.POST)
        if form.is_valid():
            message = request.POST.get('message', '')
            first_name = request.POST.get('first_name', '')
            email = request.POST.get('email', '')
            template = get_template('email/shop_message_send.html')
            context = {
                'request': request,
                'shop': shop,
                'profile': profile,
                'first_name': first_name,
                'email': email,
                'message': message,
            }
            content = template.render(context)

            email = EmailMessage(
                "Вашему магазину задали вопрос handmaker.top",
                content,
                settings.EMAIL_HOST_USER,
                [shop.user.email],
                headers={'Reply-To': email}
            )
            email.content_subtype = 'html'
            email.send(fail_silently=True)
            messages.success(request, "Ваше сообщение успешно отправлено")
            return HttpResponseRedirect(reverse('shop_view', args=[shop.slug]))

    context = {'shop': shop, "form": form}
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)


@login_required
def shop_toggle_vacation(request):
    try:
        shop = request.user.shop
        if shop.on_vacation:
            shop.on_vacation = False
            messages.success(
                request, "Ваш магазин успешно вернулся с каникул!")
        else:
            shop.on_vacation = True
            messages.info(
                request, 'Ваш магазин теперь на каникулах и не принимает заказы.')
        shop.save()
    except Exception as e:
        shop = None
        messages.append('go')

    if request.META['HTTP_REFERER']:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseRedirect('/')


@login_required
def shop_create(request, template="accounts/account_shop_create.html"):
    try:
        shop = UserShop.objects.get(user=request.user)
    except:
        shop = None

    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            if shop:
                messages.success(request, "Магазин успешно изменен.")
            else:
                messages.success(request, "Магазин успешно создан.")

            shop = form.save(commit=False)
            shop.user = request.user
            if request.FILES.get('image', False):
                shop.image = request.FILES['image']

            if request.FILES.get('background', False):
                shop.background = request.FILES['background']
            shop.save()

            if not shop.user.groups.filter(name='custom').exists():
                shop.user.is_staff = True
                group = Group.objects.get(name='custom')
                shop.user.groups.add(group)
                shop.user.save()
            return redirect('shop_view', slug=shop.slug)
    else:
        form = ShopForm(instance=shop)
    templates = []
    context = {"form": form, "shop": shop}
    templates.append(template)
    return TemplateResponse(request, templates, context)


@method_decorator(login_required, name='dispatch')
class ProductList(ListView):
    model = ShopProduct
    template_name = "product/product_user_list.html"
    context_object_name = "product_list"

    def get_queryset(self):
        return ShopProduct.objects.filter(shop__id=self.request.user.shop.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        remain = self.request.user.profile.allow_blogpost_count - \
            len(context['object_list'])
        context['remain'] = remain
        return context


@method_decorator(login_required, name='dispatch')
class ProductCreate(CreateView):
    model = ShopProduct
    form_class = ProductForm
    success_url = reverse_lazy('product-list')


@method_decorator(login_required, name='dispatch')
class ProductUpdate(UpdateView):
    model = ShopProduct
    form_class = ProductForm
    success_url = reverse_lazy('product-list')
    template_name = "product/product_form.html"


@method_decorator(login_required, name='dispatch')
class ProductDelete(DeleteView):
    model = ShopProduct
    success_url = reverse_lazy('product-list')
    template_name = "product/product_confirm_delete.html"
    success_message = "Товар успешно удален"

    def get_object(self, queryset=None):
        obj = super(ProductDelete, self).get_object()
        if not obj.shop == self.request.user.shop:
            raise Http404
        return obj

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ProductDelete, self).delete(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ProductImageCreate(CreateView):
    """docstring for ProductImageCreate"""
    model = ShopProduct
    form_class = ProductForm
    success_url = reverse_lazy('product-list')
    template_name = "product/product_form.html"
    success_message = "Товар успешно создан"
    warning_message = "Исчерпан лимит"

    def dispatch(self, request, *args, **kwargs):
        if request.user.shop.products.count() >= 10:
            messages.warning(self.request, self.warning_message)
            return redirect(self.success_url)
        return super(ProductImageCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(ProductImageCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['productimage'] = ProductImageFormSet(self.request.POST)
        else:
            data['productimage'] = ProductImageFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        productimage = context['productimage']
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.shop = self.request.user.shop
            # if productimage.is_valid():
            #     for form in productimage[:1]:
            #         self.object.main_image = form.initial['file']
            # else:
            #     self.object.main_image = ""
            self.object.save()

            if productimage.is_valid():
                productimage.instance = self.object
                productimage.save()
        messages.success(self.request, self.success_message)
        return super(ProductImageCreate, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class ProductImageUpdate(UpdateView):
    model = ShopProduct
    form_class = ProductForm
    success_url = reverse_lazy('product-list')
    template_name = "product/product_form.html"
    # queryset = ShopProduct.objects.select_related()
    success_message = "Товар успешно обновлен"

    def get_context_data(self, **kwargs):
        data = super(ProductImageUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['productimage'] = ProductImageFormSet(
                self.request.POST, instance=self.object)
        else:
            data['productimage'] = ProductImageFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        productimage = context['productimage']
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.shop = self.request.user.shop
            # if productimage.is_valid():
            #     for form in productimage:
            #         self.object.main_image = form.initial['file']
            #         break
            # else:
            #     self.object.main_image = ""
            self.object.save()

            if productimage.is_valid():
                productimage.instance = self.object
                productimage.save()
                messages.success(self.request, self.success_message)

        return super(ProductImageUpdate, self).form_valid(form)

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ProductImageUpdate, self).get_object()
        if not obj.shop == self.request.user.shop:
            raise Http404
        return obj


class ProductDetailView(DetailView):
    model = ShopProduct
    template_name = "product/product.html"
    context_object_name = 'product'
    queryset = ShopProduct.objects.prefetch_related(
        'keywords__keyword', 'images').select_related("shop__user__profile", "shop__user__profile__country", "shop__user__profile__city")

    def get_context_data(self, **kwargs):
        data = super(ProductDetailView, self).get_context_data(**kwargs)
        data['form'] = AddProductForm(product=self.object)
        return data


class ShopList(ListView):
    model = UserShop
    template_name = "shops/shop_list.html"


@method_decorator(login_required, name='dispatch')
class ShopCreate(CreateView):
    model = UserShop
    form_class = ShopForm


@method_decorator(login_required, name='dispatch')
class ShopDeliveryOptionCreate(CreateView):
    model = UserShop
    form_class = ShopForm
    success_url = reverse_lazy('profile-settings')
    template_name = "shops/shop_form.html"
    success_message = "Магазин успешно создан"

    def dispatch(self, *args, **kwargs):
        try:
            shop = self.request.user.shop
        except Exception as e:
            pass
        else:
            return redirect(reverse_lazy('shop-update', args=[self.request.user.shop.slug]))
        return super(ShopDeliveryOptionCreate, self).dispatch(*args, **kwargs)

    # def get_context_data(self, **kwargs):
    #     data = super(ShopDeliveryOptionCreate, self).get_context_data(**kwargs)
    #     if self.request.POST:
    #         data['deliveryoption'] = UserShopDeliveryOptionFormSet(self.request.POST)
    #     else:
    #         data['deliveryoption'] = UserShopDeliveryOptionFormSet()
    #     return data

    def form_valid(self, form):
        context = self.get_context_data()
        # deliveryoption = context['deliveryoption']
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()
            messages.success(self.request, self.success_message)
            # if deliveryoption.is_valid():
            #     deliveryoption.instance = self.object
            #     deliveryoption.save()
        return super(ShopDeliveryOptionCreate, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class ShopUpdate(UpdateView):
    model = UserShop
    success_url = '/'
    form_class = ShopForm
    template_name = "shops/shop_form.html"


@method_decorator(login_required, name='dispatch')
class ShopDeliveryOptionUpdate(UpdateView):
    model = UserShop
    form_class = ShopForm
    # fields = ["background", "image", "shopname", "bio", "rules",
    #           "payment_personal", "payment_bank_transfer", "payment_card_transfer", "payment_other"]
    success_url = reverse_lazy('profile-settings')
    template_name = "shops/shop_form.html"
    success_message = "Магазин успешно обновлен"
    # def get_context_data(self, **kwargs):
    #     data = super(ShopDeliveryOptionUpdate, self).get_context_data(**kwargs)
    #     if self.request.POST:
    #         data['deliveryoption'] = UserShopDeliveryOptionFormSet(self.request.POST, instance=self.object)
    #     else:
    #         data['deliveryoption'] = UserShopDeliveryOptionFormSet(instance=self.object)
    #     return data

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ShopDeliveryOptionUpdate, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj

    def form_valid(self, form):
        context = self.get_context_data()
        # deliveryoption = context['deliveryoption']
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()
            messages.success(self.request, self.success_message)
            # if deliveryoption.is_valid():
            #     deliveryoption.instance = self.object
            #     deliveryoption.save()
        return super(ShopDeliveryOptionUpdate, self).form_valid(form)


class ShopDelete(DeleteView):
    model = UserShop
    success_url = reverse_lazy('shop-list')
    template_name = "shops/shop_confirm_delete.html"

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ShopDelete, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj


class ShopDetailView(DetailView):
    model = UserShop
    template_name = "shops/shop_detail.html"
    context_object_name = 'shop'
    queryset = UserShop.objects.prefetch_related(
        'products', 'products__images')

    def post(self, request, *args, **kwargs):
        form = MessageForm(data=request.POST)
        if form.is_valid():
            message = request.POST.get('message', '')
            first_name = request.POST.get('first_name', '')
            email = request.POST.get('email', '')
            template = get_template('email/shop_message_send.html')
            context = {
                'request': request,
                'shop': self.get_object(),
                'profile': self.get_object().user.profile,
                'first_name': first_name,
                'email': email,
                'message': message,
            }
            content = template.render(context)

            email = EmailMessage(
                "Вашему магазину задали вопрос handmaker.top",
                content,
                settings.EMAIL_HOST_USER,
                [self.get_object().user.email],
                headers={'Reply-To': email}
            )
            email.content_subtype = 'html'
            email.send(fail_silently=True)
            messages.success(request, "Ваше сообщение успешно отправлено")
        else:
            messages.error(request, "Проверьте правильность введенных данных")
        return HttpResponseRedirect(self.get_object().get_absolute_url())

    def get_context_data(self, **kwargs):
        data = super(ShopDetailView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['form'] = MessageForm(self.request.POST)
        else:
            data['form'] = MessageForm()
        return data
    # def get_queryset(self):
    # return UserShop.objects.prefetch_related('products')
    # queryset = UserShop.objects.prefetch_related(
    # 'keywords__keyword').select_related("shop__user__profile", "shop__user__profile__country", "shop__user__profile__city")


def get_cart(request):
    if request.is_ajax():
        cart = Cart.objects.get_from_request(request)
        quantity = int(request.POST.get('quantity', 1))
        shop_name = request.POST.get('shop_name', None)
        product = ShopProduct.objects.get(
            id=request.POST.get('product_id', None))
        # product = Map()
        # for key, value in request.POST.items():
        #     product[key]=value
        if cart and product:
            cart.add_item(product, quantity, shop_name)
        html = render_to_string('shops/includes/user_panel.html',
                                {'request': request, 'MEDIA_URL': settings.MEDIA_URL})
        return HttpResponse(html)
    return JsonResponse({})


# class CartView(DetailView):
#     template_name = "shops/cart.html"
#
#     def get_object(self):
#         return self.request.cart
#
#     def get_context_data(self, **kwargs):
#         data = super(CartView, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['cartitems'] = CartItemFormSet(self.request.POST, instance=self.object)
#         else:
#             data['cartitems'] = CartItemFormSet(instance=self.object)
#         return data


class CartView(UpdateView):
    model = Cart
    fields = ()
    template_name = "shops/cart.html"
    context_object_name = 'cart'
    success_url = reverse_lazy('shop-cart')
    success_message = "Корзина обновлена"
    # queryset = UserShop.objects.prefetch_related(
    #     'products', 'products__images')

    def get_object(self):
        return self.request.cart

    def get_context_data(self, **kwargs):
        data = super(CartView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['cartitems'] = CartItemFormSet(
                self.request.POST, instance=self.object)
        else:
            data['cartitems'] = CartItemFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        cartitems = context['cartitems']
        with transaction.atomic():
            if cartitems.is_valid():
                cartitems.save()
                messages.success(self.request, self.success_message)
        return super(CartView, self).form_valid(form)

    # def get_queryset(self):
    #     return Cart.objects.filter(user=self.request.user)

    # def post(self, request, *args, **kwargs):
    #     form = MessageForm(data=request.POST)
    #     if form.is_valid():
    #         message = request.POST.get('message', '')
    #         first_name = request.POST.get('first_name', '')
    #         email = request.POST.get('email', '')
    #         template = get_template('email/shop_message_send.html')
    #         context = {
    #             'request': request,
    #             'shop': self.get_object(),
    #             'profile': self.get_object().user.profile,
    #             'first_name': first_name,
    #             'email': email,
    #             'message': message,
    #         }
    #         content = template.render(context)
    #
    #         email = EmailMessage(
    #             "Вашему магазину задали вопрос handmaker.top",
    #             content,
    #             settings.EMAIL_HOST_USER,
    #             [self.get_object().user.email],
    #             headers={'Reply-To': email}
    #         )
    #         email.content_subtype = 'html'
    #         email.send(fail_silently=True)
    #         messages.success(request, "Ваше сообщение успешно отправлено")
    #     else:
    #         messages.error(request, "Проверьте правильность введенных данных")
    #     return HttpResponseRedirect(self.get_object().get_absolute_url())

    # def get_context_data(self, **kwargs):
    #     data = super(ShopDetailView, self).get_context_data(**kwargs)
    #     if self.request.POST:
    #         data['form'] = MessageForm(self.request.POST)
    #     else:
    #         data['form'] = MessageForm()
    #     return data


class CheckoutProcess(CreateView):
    model = Order
    form_class = OrderForm
    template_name = "shops/checkout.html"
    context_object_name = 'order'
    success_url = reverse_lazy('profile-settings')
    success_message = "Заказ сформирован"

    def get_context_data(self, **kwargs):
        data = super(CheckoutProcess, self).get_context_data(**kwargs)
        data['shop_slug'] = self.kwargs['slug']
        data['shop_id'] = self.kwargs['pk']
        return data

    def get_form_kwargs(self, **kwargs):
        kwargs = super(CheckoutProcess, self).get_form_kwargs(**kwargs)
        kwargs['user'] = self.request.user if self.request.user.is_authenticated() else None
        kwargs['shop'] = UserShop.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        context = self.get_context_data()
        with transaction.atomic():
            self.object = form.save(commit=False)
            # self.object.shop = form.shop
            # self.object.user_id = form.user.id
            # self.object.price_total = 0
            self.object.complete(self.request, form)
            # self.object.save()
            messages.success(self.request, self.success_message)
        return super(CheckoutProcess, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class OrderList(ListView):
    model = Order
    template_name = "shops/order_list.html"
    context_object_name = "order_list"

    def get_queryset(self):
        if self.kwargs.get('pk'):
            qs = self.model.objects.filter(shop__pk=self.kwargs['pk'])
        else:
            qs = self.model.objects.filter(user_id=self.request.user.id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('pk'):
            context['for_shop'] = True
        return context


@method_decorator(login_required, name='dispatch')
class OrderUpdate(UpdateView):
    model = Order
    fields = '__all__'
    form = OrderForm
    template_name = "shops/order_form.html"
    # context_object_name = "order_list"


class OrderDetail(DetailView):
    model = Order
    # template_name = "shops/order.html"
    context_object_name = 'order'
    queryset = Order.objects.select_related('shop').prefetch_related('items')