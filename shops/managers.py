from __future__ import unicode_literals
from future.builtins import str, zip

from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta

from django.db.models import Manager, Q
from django.utils.timezone import now
import datetime
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string

from mezzanine.conf import settings
from mezzanine.utils.email import send_verification_mail
from mezzanine.core.managers import SearchableManager, SearchableQuerySet, search_fields_to_dict


class CartManager(Manager):

    def get_from_request(self, request):
        """
        Return the cart for current customer.
        """
        cart_id = request.session.get("cart_id", None)
        # print("session_cart_id_by_request: ", cart_id)
        cart = self.current().filter(id=cart_id)
        last_updated = now()

        # Update timestamp and clear out old carts.
        if cart_id and cart.update(last_updated=last_updated):
            self.expired().delete()
        elif cart_id:
            # Cart has expired. Delete the cart id and
            # forget what checkout step we were up to.
            del request.session["cart_id"]
            cart_id = None

        # This is a cheeky way to save a database call: since Cart only has
        # two fields and we know both of their values, we can simply create
        # a cart instance without taking a trip to the database via the ORM.
        return self.model(id=cart_id, last_updated=last_updated)

    # def get_or_create_from_request(self, request):
    #     if not request.user.is_authenticated():
    #         request.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
    #         # send_verification_mail(request, request.user, "signup_verify")
    #     cart, created = self.get_or_create(user=request.user)
    #     return cart

    # def from_request(self, request):
    #     """
    #     Return a cart by ID stored in the session, updating its last_updated
    #     value and removing old carts. A new cart will be created (but not
    #     persisted in the database) if the session cart is expired or missing.
    #     """
    #     cart_id = request.session.get("cart", None)
    #     cart = self.current().filter(id=cart_id)
    #     last_updated = now()
    #
    #     # Update timestamp and clear out old carts.
    #     if cart_id and cart.update(last_updated=last_updated):
    #         self.expired().delete()
    #     elif cart_id:
    #         # Cart has expired. Delete the cart id and
    #         # forget what checkout step we were up to.
    #         del request.session["cart"]
    #         cart_id = None
    #         try:
    #             del request.session["order"]["step"]
    #         except KeyError:
    #             pass
    #
    #     # This is a cheeky way to save a database call: since Cart only has
    #     # two fields and we know both of their values, we can simply create
    #     # a cart instance without taking a trip to the database via the ORM.
    #     return self.model(id=cart_id, last_updated=last_updated)

    def expiry_time(self):
        """
        Datetime for expired carts.
        """
        return now() - timedelta(minutes=settings.SHOP_CART_EXPIRY_MINUTES)

    def current(self):
        """
        Unexpired carts.
        """
        return self.filter(last_updated__gte=self.expiry_time())

    def expired(self):
        """
        Expired carts.
        """
        return self.filter(last_updated__lt=self.expiry_time())


class ShopProductManager(SearchableManager):

    def published(self, for_user=None):
        """
        For non-staff users, return available items
        """
        if for_user is not None and for_user.is_staff:
            return self.all()
        return self.filter(Q(available=True))

    def search(self, *args, **kwargs):
        categories = kwargs.pop("categories", None)
        user = kwargs.pop("for_user", None)
        all_results = []
        try:
            queryset = self.model.objects.published(for_user=user)
        except AttributeError:
            queryset = self.model.objects.get_queryset()

        if categories:
            queryset = queryset.filter(categories__id__in=categories)

        all_results.extend(
            queryset.search(*args, **kwargs).select_related('shop').prefetch_related('images'))
        return sorted(all_results, key=lambda r: r.result_count, reverse=True)
