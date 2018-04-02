from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import redirect
import os
import HelloDjango.settings
from mezzanine.conf import settings
from cartridge.shop.models import Cart


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

                pop = request.GET.get('pop', None)
                height = request.GET.get('width', None)
                width = request.GET.get('height', None)

                url = reverse('fb_browse') + '?type=Image&dir=' + request.user.username

                if width and height:
                    url += '&width=' + request.GET['width'] + '&height=' + request.GET['height']

                if pop:
                    url += '&pop=' + pop

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
