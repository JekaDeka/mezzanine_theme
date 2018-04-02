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

class CartManager(Manager):

    def get_from_request(self, request):
        """
        Return the cart for current customer.
        """
        self.expired().delete()
        if request.user.is_authenticated():
            cart, created = self.get_or_create(user=request.user)
            return cart
        else:
            cart_id = request.session.get("cart", None)
            try:
                cart = self.get(id=cart_id)
            except Exception as e:
                if cart_id:
                    del request.session['cart']
                cart = self.create()
                request.session['cart'] = cart.id
            return cart
        return None


    def get_or_create_from_request(self, request):
        if not request.user.is_authenticated():
            request.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
            # send_verification_mail(request, request.user, "signup_verify")
        cart, created = self.get_or_create(user=request.user)
        return cart

    def from_request(self, request):
        """
        Return a cart by ID stored in the session, updating its last_updated
        value and removing old carts. A new cart will be created (but not
        persisted in the database) if the session cart is expired or missing.
        """
        cart_id = request.session.get("cart", None)
        cart = self.current().filter(id=cart_id)
        last_updated = now()

        # Update timestamp and clear out old carts.
        if cart_id and cart.update(last_updated=last_updated):
            self.expired().delete()
        elif cart_id:
            # Cart has expired. Delete the cart id and
            # forget what checkout step we were up to.
            del request.session["cart"]
            cart_id = None
            try:
                del request.session["order"]["step"]
            except KeyError:
                pass

        # This is a cheeky way to save a database call: since Cart only has
        # two fields and we know both of their values, we can simply create
        # a cart instance without taking a trip to the database via the ORM.
        return self.model(id=cart_id, last_updated=last_updated)

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
