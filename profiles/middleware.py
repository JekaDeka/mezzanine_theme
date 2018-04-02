from __future__ import unicode_literals
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import redirect


class RestrictProfileMiddleware(object):
    """
    If user have no profile redirect him to creat page
    """

    def process_request(self, request):
        if request.path == reverse('true_index'):
            if not request.user.is_superuser and request.user.is_authenticated():
                try:
                    profile = request.user.profile
                except Exception as e:
                    return HttpResponseRedirect(reverse('profile-add'))
