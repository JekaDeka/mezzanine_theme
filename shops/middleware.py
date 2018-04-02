from __future__ import unicode_literals

from mezzanine.conf import settings

from shops.models import Cart
from django.contrib.auth import get_user_model
User = get_user_model()


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
        # if request.user.id:
        #     request.user = User.objects.select_related('shop', 'profile', 'profile__region').get(id=request.user.id)
        # pass
        # try:
        #     User.objects.select_related('shop', 'profile', 'profile__region').get(id=request.user.id)
        # except Exception as e:
        #     pass

        request.cart = Cart.objects.get_from_request(request)
        # wishlist = request.COOKIES.get("wishlist", "").split(",")
        # if not wishlist[0]:
        #     wishlist = []
        # request.wishlist = wishlist
