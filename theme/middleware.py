from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from mezzanine.utils.deprecation import MiddlewareMixin, get_middleware_setting
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.contrib import messages
import os
import HelloDjango.settings
from mezzanine.conf import settings
from cartridge.shop.models import Cart
# from theme.models import ShopRealtedCart


class RestrictAdminMiddleware(object):
    """
    Restricts access to the admin page to only logged-in users with a certain user-level.
    """

    def process_exception(self, request, exception):
        if exception.__class__.__name__ == 'PermissionDenied':
            return redirect(reverse('true_index'))

    def process_request(self, request):
        if request.path == reverse('fb_browse'):
            if not request.user.is_superuser:
                path = HelloDjango.settings.MEDIA_ROOT + '/uploads/' + request.user.username
                url = reverse('fb_browse') + \
                    '?pop=1&type=Image&dir=' + request.user.username
                if not os.path.exists(path):
                    os.makedirs(path)

                current_url = request.get_full_path()
                beg = current_url.find('dir=')
                if beg != -1:
                    dirname = current_url[beg:].split("&")[0]
                    if not request.user.username in dirname:
                        return HttpResponseRedirect(url)
                else:  # if in root dir => redirect to user dir
                    return HttpResponseRedirect(url)


class SSLRedirect(object):

    def __init__(self):
        old = ("SHOP_SSL_ENABLED", "SHOP_FORCE_HOST", "SHOP_FORCE_SSL_VIEWS")
        for name in old:
            try:
                getattr(settings, name)
            except AttributeError:
                pass
            else:
                import warnings
                warnings.warn("The settings %s are deprecated; "
                              "use SSL_ENABLED, SSL_FORCE_HOST and "
                              "SSL_FORCE_URL_PREFIXES, and add "
                              "mezzanine.core.middleware.SSLRedirectMiddleware to "
                              "MIDDLEWARE_CLASSES." % ", ".join(old))
                break


class ShopMiddleware(SSLRedirect):
    """
    Adds cart and wishlist attributes to the current request.
    """

    def process_request(self, request):
        request.cart = Cart.objects.from_request(request)
        # request.cart = NoQCart.objects.from_request(request)
        wishlist = request.COOKIES.get("wishlist", "").split(",")
        if not wishlist[0]:
            wishlist = []
        request.wishlist = wishlist
