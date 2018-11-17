import re
import string
import threading
from ipware.ip import get_real_ip, get_ip
from random import choice as random_choice
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser

charset = string.ascii_letters + string.digits


def get_unique_id(length=16):
    """Randomness possiblity is x^n where x is the character_set (ascii) and n is the number of characters. In the case
    of UUID4 with 32 alphanumeric chars (36 chars), this is 36^32. We'll do 64^16. It's faster and saves 20 chars."""
    return ''.join((random_choice(charset) for _ in xrange(length)))


def get_user_from_meta(request):
    """
    If a request has HTTP_AUTHORIZATION in the META, return the User object.
    Have to import models (AuthToken and get_user_model) here to avoid `AppRegistryNotReady: Models aren't loaded yet`
    """
    if not hasattr(request, 'META'):
        return None
    token = re.sub('Token ', '', request.META.get('HTTP_AUTHORIZATION', ''))
    if token:
        try:
            return Token.objects.get(key=token).user
        except Token.DoesNotExist:
            return None
        except TypeError:
            print('Invalid type for token %s', token)
        except Exception:
            print('Unexpected error in get_user_from_meta')
    return None


class RequestContextMiddleware(object):
    THREAD = None

    def process_request(self, request):
        request.user = get_user_from_meta(request)
        RequestContextMiddleware.THREAD = threading.local()
        RequestContextMiddleware.THREAD.id = get_unique_id()
        RequestContextMiddleware.THREAD.ip = get_real_ip(request) or get_ip(request) or request.get_host()
        RequestContextMiddleware.THREAD.user = request.user.id if request.user else AnonymousUser()
