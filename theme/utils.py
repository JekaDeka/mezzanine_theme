from transliterate import translit
from django.contrib import messages
from django.core.urlresolvers import reverse
import re

# messages.success(request, "Skadoosh! You've updated your profile!")
# messages.info(request, 'Yo! There are new comments on your photo!')
# messages.error(request, 'Doh! Something went wrong.')
# messages.warning(request, 'Uh-oh. Your account expires in %s days.')


class AuthorIsRequested(Exception):
    """Raise for my specific kind of exception"""


def slugify_unicode(s):
    s = translit(s, 'ru', reversed=True)
    s = re.sub(r"[^\w\s]", '', s)
    return re.sub("[-\s]+", "-", "".join(s).strip()).lower()


def validate_filter(value):
    if isinstance(value, str):
        if value == 'True':
            return True
        elif value == 'False':
            return False
        try:
            value = int(value)
        except Exception as e:
            value = None
        else:
            return value
    return None
