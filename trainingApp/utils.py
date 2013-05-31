import hashlib
from django.core.cache import cache


def delete_template_fragment_cache(fragment_name='', *args):
    cache.delete('template.cache.%s.%s' % (fragment_name, hashlib.md5(u':'.join([arg for arg in args])).hexdigest()))
