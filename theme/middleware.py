from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from mezzanine.utils.deprecation import MiddlewareMixin, get_middleware_setting
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.contrib import messages
import os
import HelloDjango.settings


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
